"""Менеджер для работы с различными обменниками"""

import ccxt
from typing import Dict, List, Optional, Any
from loguru import logger
from config import settings


class ExchangeManager:
    """Менеджер для работы с различными криптообменниками"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.exchanges = {}
        self.supported_exchanges = {
            'binance': ccxt.binance,
            'kucoin': ccxt.kucoin,
            'huobi': ccxt.huobi,
            'okx': ccxt.okx,
            'gate': ccxt.gateio
        }
    
    def get_available_exchanges(self) -> List[str]:
        """Получить список поддерживаемых обменников"""
        return list(self.supported_exchanges.keys())
    
    def initialize_exchange(self, exchange_name: str) -> bool:
        """
        Инициализировать подключение к обменнику
        
        Args:
            exchange_name: Название обменника
            
        Returns:
            True если подключение успешно
        """
        try:
            if exchange_name not in self.supported_exchanges:
                raise ValueError(f"Обменник {exchange_name} не поддерживается")
            
            # Получение credentials
            credentials = settings.get_exchange_credentials(exchange_name)
            if not credentials or not credentials.get('apiKey'):
                logger.warning(f"⚠️ API ключи для {exchange_name} не настроены. Будет использован публичный доступ.")
                credentials = {}
            
            # Создание экземпляра обменника
            exchange_class = self.supported_exchanges[exchange_name]
            exchange_instance = exchange_class({
                **credentials,
                'enableRateLimit': True,
                'sandbox': False  # Для продакшена используем основную сеть
            })
            
            # Проверка подключения
            try:
                markets = exchange_instance.load_markets()
                logger.info(f"✅ Подключение к {exchange_name} установлено. Загружено {len(markets)} рынков.")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки рынков {exchange_name}: {e}. Продолжаем с публичным API.")
            
            self.exchanges[exchange_name] = exchange_instance
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации {exchange_name}: {e}")
            return False
    
    def get_exchange_rates(self, from_currency: str, to_currency: str, exchanges: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Получить курсы обмена на разных биржах
        
        Args:
            from_currency: Валюта для обмена (например, 'BTC')
            to_currency: Целевая валюта (например, 'ETH')
            exchanges: Список бирж для проверки (если None - все доступные)
            
        Returns:
            Словарь с курсами на каждой бирже
        """
        if exchanges is None:
            exchanges = self.get_available_exchanges()
        
        rates = {}
        
        for exchange_name in exchanges:
            try:
                if exchange_name not in self.exchanges:
                    if not self.initialize_exchange(exchange_name):
                        continue
                
                exchange = self.exchanges[exchange_name]
                
                # Попробуем найти прямую пару
                symbol = f"{from_currency}/{to_currency}"
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    rates[exchange_name] = {
                        'symbol': symbol,
                        'rate': ticker['last'],
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'volume': ticker['quoteVolume'],
                        'direct_pair': True
                    }
                    continue
                except:
                    pass
                
                # Если прямой пары нет, ищем через USDT
                try:
                    from_usdt_symbol = f"{from_currency}/USDT"
                    to_usdt_symbol = f"{to_currency}/USDT"
                    
                    from_ticker = exchange.fetch_ticker(from_usdt_symbol)
                    to_ticker = exchange.fetch_ticker(to_usdt_symbol)
                    
                    # Расчет кросс-курса через USDT
                    cross_rate = from_ticker['last'] / to_ticker['last']
                    
                    rates[exchange_name] = {
                        'symbol': f"{from_currency}/{to_currency} (via USDT)",
                        'rate': cross_rate,
                        'from_usdt_rate': from_ticker['last'],
                        'to_usdt_rate': to_ticker['last'],
                        'direct_pair': False
                    }
                    
                except Exception as inner_e:
                    logger.warning(f"⚠️ Не удалось получить курс {from_currency}/{to_currency} на {exchange_name}: {inner_e}")
                    continue
                    
            except Exception as e:
                logger.error(f"❌ Ошибка получения курса на {exchange_name}: {e}")
                continue
        
        return rates
    
    def find_best_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Dict[str, Any]]:
        """
        Найти лучший курс обмена среди всех бирж
        
        Args:
            from_currency: Валюта для обмена
            to_currency: Целевая валюта
            
        Returns:
            Информация о лучшем курсе или None
        """
        rates = self.get_exchange_rates(from_currency, to_currency)
        
        if not rates:
            return None
        
        # Найти биржу с лучшим курсом (максимальным)
        best_exchange = max(rates.items(), key=lambda x: x[1]['rate'])
        
        result = {
            'exchange': best_exchange[0],
            'rate': best_exchange[1]['rate'],
            'symbol': best_exchange[1]['symbol'],
            'direct_pair': best_exchange[1]['direct_pair']
        }
        
        logger.info(f"🏆 Лучший курс {from_currency}/{to_currency}: {result['rate']:.8f} на {result['exchange']}")
        
        return result
    
    def execute_exchange(self, exchange_name: str, from_currency: str, to_currency: str, amount: float) -> Optional[Dict[str, Any]]:
        """
        Выполнить обмен криптовалют на выбранной бирже
        
        Args:
            exchange_name: Название биржи
            from_currency: Валюта для обмена
            to_currency: Целевая валюта
            amount: Количество для обмена
            
        Returns:
            Информация о выполненной операции
        """
        try:
            if exchange_name not in self.exchanges:
                if not self.initialize_exchange(exchange_name):
                    raise ValueError(f"Не удалось подключиться к {exchange_name}")
            
            exchange = self.exchanges[exchange_name]
            
            # Проверка баланса
            balance = exchange.fetch_balance()
            available_balance = balance.get(from_currency, {}).get('free', 0)
            
            if available_balance < amount:
                raise ValueError(f"Недостаточно {from_currency}. Доступно: {available_balance:.8f}, требуется: {amount:.8f}")
            
            # Попробуем прямой обмен
            symbol = f"{from_currency}/{to_currency}"
            try:
                # Продаем from_currency за to_currency
                order = exchange.create_market_sell_order(symbol, amount)
                
                logger.info(f"✅ Обмен выполнен на {exchange_name}: {amount:.8f} {from_currency} -> {to_currency}")
                logger.info(f"📊 ID ордера: {order['id']}")
                
                return order
                
            except:
                # Если прямого обмена нет, делаем через USDT
                logger.info(f"💱 Прямой обмен {symbol} недоступен, используем обмен через USDT")
                
                # Сначала продаем from_currency за USDT
                from_usdt_symbol = f"{from_currency}/USDT"
                sell_order = exchange.create_market_sell_order(from_usdt_symbol, amount)
                
                # Получаем количество USDT
                usdt_amount = sell_order.get('cost', 0)  # Примерное количество USDT
                if usdt_amount == 0:
                    # Пересчитываем через ticker
                    ticker = exchange.fetch_ticker(from_usdt_symbol)
                    usdt_amount = amount * ticker['last']
                
                # Покупаем to_currency за USDT
                to_usdt_symbol = f"{to_currency}/USDT"
                ticker_to = exchange.fetch_ticker(to_usdt_symbol)
                to_amount = usdt_amount / ticker_to['last']
                
                buy_order = exchange.create_market_buy_order(to_usdt_symbol, to_amount)
                
                logger.info(f"✅ Двойной обмен выполнен на {exchange_name}: {amount:.8f} {from_currency} -> {usdt_amount:.2f} USDT -> {to_amount:.8f} {to_currency}")
                
                return {
                    'sell_order': sell_order,
                    'buy_order': buy_order,
                    'final_amount': to_amount,
                    'intermediate_usdt': usdt_amount
                }
                
        except Exception as e:
            logger.error(f"❌ Ошибка обмена на {exchange_name}: {e}")
            raise