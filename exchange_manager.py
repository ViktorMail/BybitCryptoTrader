"""Менеджер для работы с множественными криптобиржами"""

from typing import Dict, List, Optional, Any, Tuple

# Безопасный импорт ccxt с fallback
try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False
    ccxt = None

# Безопасный импорт логирования с fallback
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

from config import settings

class ExchangeManager:
    """Менеджер для работы с несколькими биржами"""
    
    def __init__(self):
        """Инициализация менеджера бирж"""
        self.exchanges = {}
        self.initialize_exchanges()
    
    def initialize_exchanges(self):
        """Инициализация доступных бирж"""
        if not HAS_CCXT:
            logger.warning("ccxt не установлен - внешние биржи недоступны")
            return
            
        exchange_configs = {
            'binance': {
                'class': ccxt.binance,
                'credentials': settings.get_exchange_credentials('binance')
            },
            'kucoin': {
                'class': ccxt.kucoin,
                'credentials': settings.get_exchange_credentials('kucoin')
            }
        }
        
        for name, config in exchange_configs.items():
            try:
                credentials = config['credentials']
                if credentials and all(credentials.values()):
                    exchange = config['class'](credentials)
                    exchange.load_markets()
                    self.exchanges[name] = exchange
                    logger.info(f"Exchange {name} initialized successfully")
                else:
                    logger.warning(f"Exchange {name} credentials not configured")
                    
            except Exception as e:
                logger.error(f"Failed to initialize exchange {name}: {e}")
    
    def get_available_exchanges(self) -> List[str]:
        """Получение списка доступных бирж"""
        return list(self.exchanges.keys())
    
    def find_best_rate(self, symbol: str, side: str = 'buy') -> Optional[Tuple[str, float]]:
        """Поиск лучшего курса среди бирж"""
        rates = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                ticker = exchange.fetch_ticker(symbol)
                if side == 'buy':
                    rates[exchange_name] = ticker['ask']  # Цена покупки
                else:
                    rates[exchange_name] = ticker['bid']  # Цена продажи
                    
            except Exception as e:
                logger.warning(f"Could not get rate from {exchange_name}: {e}")
        
        if not rates:
            return None
        
        if side == 'buy':
            # Для покупки ищем минимальную цену
            best_exchange = min(rates.items(), key=lambda x: x[1])
        else:
            # Для продажи ищем максимальную цену
            best_exchange = max(rates.items(), key=lambda x: x[1])
        
        logger.info(f"Best {side} rate for {symbol}: {best_exchange}")
        return best_exchange
    
    def execute_arbitrage_trade(self, symbol: str, amount: float) -> Dict[str, Any]:
        """Выполнение арбитражной сделки"""
        try:
            # Находим лучшие курсы для покупки и продажи
            buy_rate = self.find_best_rate(symbol, 'buy')
            sell_rate = self.find_best_rate(symbol, 'sell')
            
            if not buy_rate or not sell_rate:
                raise ValueError("Could not find suitable rates")
            
            buy_exchange, buy_price = buy_rate
            sell_exchange, sell_price = sell_rate
            
            # Проверяем профитабельность
            profit_margin = (sell_price - buy_price) / buy_price
            
            if profit_margin < settings.max_slippage:
                logger.warning(f"Low profit margin: {profit_margin:.4f}")
                return {
                    'status': 'skipped',
                    'reason': 'low_profit',
                    'profit_margin': profit_margin
                }
            
            # Выполняем сделки
            quantity = amount / buy_price
            
            # Покупаем на одной бирже
            buy_order = self.exchanges[buy_exchange].create_market_buy_order(symbol, quantity)
            
            # Продаем на другой бирже
            sell_order = self.exchanges[sell_exchange].create_market_sell_order(symbol, quantity)
            
            result = {
                'status': 'completed',
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'buy_order': buy_order,
                'sell_order': sell_order,
                'profit_margin': profit_margin,
                'quantity': quantity
            }
            
            logger.info(f"Arbitrage trade completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Arbitrage trade failed: {e}")
            raise
    
    def transfer_between_exchanges(self, symbol: str, amount: float, from_exchange: str, to_exchange: str) -> Dict[str, Any]:
        """Перевод между биржами"""
        try:
            # Это упрощенная версия - реальный перевод требует дополнительной настройки
            logger.info(f"Transfer request: {amount} {symbol} from {from_exchange} to {to_exchange}")
            
            # Здесь должна быть логика перевода через withdraw/deposit
            return {
                'status': 'transfer_initiated',
                'from': from_exchange,
                'to': to_exchange,
                'amount': amount,
                'symbol': symbol
            }
            
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            raise
    
    def get_exchange_balances(self) -> Dict[str, Dict]:
        """Получение балансов со всех бирж"""
        balances = {}
        
        for name, exchange in self.exchanges.items():
            try:
                balance = exchange.fetch_balance()
                balances[name] = balance
            except Exception as e:
                logger.error(f"Could not get balance from {name}: {e}")
                balances[name] = {}
        
        return balances
    
    def compare_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Сравнение цен по биржам"""
        comparison = {}
        
        for symbol in symbols:
            comparison[symbol] = {}
            
            for name, exchange in self.exchanges.items():
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    comparison[symbol][name] = {
                        'bid': ticker['bid'],
                        'ask': ticker['ask'],
                        'last': ticker['last'],
                        'volume': ticker['quoteVolume']
                    }
                except Exception as e:
                    logger.warning(f"Could not get price from {name} for {symbol}: {e}")
        
        return comparison
