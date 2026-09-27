"""ByBit API клиент для торговли криптовалютами"""

from typing import Dict, List, Optional, Any

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

class ByBitClient:
    """Клиент для работы с ByBit API"""
    
    def __init__(self):
        """Инициализация клиента"""
        self.exchange = None
        self.initialize_exchange()
    
    def initialize_exchange(self):
        """Инициализация подключения к ByBit"""
        try:
            if not HAS_CCXT:
                raise ValueError("Модуль ccxt не установлен. Выполните: pip install ccxt")
                
            if not settings.validate_bybit_credentials():
                raise ValueError("ByBit API credentials не настроены")
            
            self.exchange = ccxt.bybit({
                'apiKey': settings.bybit_api_key,
                'secret': settings.bybit_api_secret,
                'sandbox': settings.bybit_testnet,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'  # торговля спот
                }
            })
            
            # Тестируем подключение
            self.exchange.load_markets()
            logger.info("ByBit client successfully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ByBit client: {e}")
            raise
    
    def get_available_cryptocurrencies(self) -> List[Dict]:
        """Получение списка доступных криптовалют"""
        try:
            if not self.exchange:
                self.initialize_exchange()
            
            markets = self.exchange.load_markets()
            tickers = self.exchange.fetch_tickers()
            
            cryptocurrencies = []
            
            for symbol, market in markets.items():
                if market['spot'] and market['active']:
                    ticker = tickers.get(symbol, {})
                    
                    crypto_info = {
                        'symbol': symbol,
                        'base': market['base'],
                        'quote': market['quote'],
                        'price': ticker.get('last'),
                        'change': ticker.get('percentage'),
                        'volume': ticker.get('quoteVolume'),
                        'market': market
                    }
                    cryptocurrencies.append(crypto_info)
            
            # Сортируем по объему торгов
            cryptocurrencies.sort(key=lambda x: x['volume'] or 0, reverse=True)
            
            logger.info(f"Found {len(cryptocurrencies)} available cryptocurrencies")
            return cryptocurrencies
            
        except Exception as e:
            logger.error(f"Error fetching cryptocurrencies: {e}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """Получение баланса аккаунта"""
        try:
            if not self.exchange:
                self.initialize_exchange()
                
            balance = self.exchange.fetch_balance()
            logger.info("Balance retrieved successfully")
            return balance
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise
    
    def buy_cryptocurrency(self, symbol: str, amount: float) -> Dict[str, Any]:
        """Покупка криптовалюты"""
        try:
            if not self.exchange:
                self.initialize_exchange()
            
            # Получаем текущую цену
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            
            # Рассчитываем количество для покупки
            quantity = amount / price
            
            # Размещаем ордер на покупку
            order = self.exchange.create_market_buy_order(symbol, quantity)
            
            logger.info(f"Buy order placed: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Error buying {symbol}: {e}")
            raise
    
    def sell_cryptocurrency(self, symbol: str, amount: float) -> Dict[str, Any]:
        """Продажа криптовалюты"""
        try:
            if not self.exchange:
                self.initialize_exchange()
            
            # Размещаем ордер на продажу
            order = self.exchange.create_market_sell_order(symbol, amount)
            
            logger.info(f"Sell order placed: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Error selling {symbol}: {e}")
            raise
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Проверка статуса ордера"""
        try:
            if not self.exchange:
                self.initialize_exchange()
                
            order = self.exchange.fetch_order(order_id, symbol)
            return order
            
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """Получение текущей цены криптовалюты"""
        try:
            if not self.exchange:
                self.initialize_exchange()
                
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise
