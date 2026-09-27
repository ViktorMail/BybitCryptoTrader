"""Конфигурация для крипто-бота"""

import os
from typing import Optional

# Безопасный импорт зависимостей с fallback
try:
    from pydantic_settings import BaseSettings
    HAS_PYDANTIC_SETTINGS = True
except ImportError:
    try:
        # Fallback для старых версий pydantic
        from pydantic import BaseSettings
        HAS_PYDANTIC_SETTINGS = True
    except (ImportError, Exception) as e:
        # Обработка любых ошибок, включая "BaseSettings has been moved"
        HAS_PYDANTIC_SETTINGS = False
        # Fallback базовый класс
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    def load_dotenv():
        pass

# Пытаемся загрузить .env если доступно
load_dotenv()

class Settings(BaseSettings if HAS_PYDANTIC_SETTINGS else object):
    """Настройки приложения"""
    
    # ByBit API
    bybit_api_key: str = os.getenv("BYBIT_API_KEY", "")
    bybit_api_secret: str = os.getenv("BYBIT_API_SECRET", "")
    bybit_testnet: bool = os.getenv("BYBIT_TESTNET", "false").lower() == "true"
    
    # Exchange APIs
    binance_api_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    
    kucoin_api_key: str = os.getenv("KUCOIN_API_KEY", "")
    kucoin_api_secret: str = os.getenv("KUCOIN_API_SECRET", "")
    kucoin_passphrase: str = os.getenv("KUCOIN_PASSPHRASE", "")
    
    # Trading settings
    default_trading_amount: float = float(os.getenv("DEFAULT_TRADING_AMOUNT", "100"))
    max_slippage: float = float(os.getenv("MAX_SLIPPAGE", "0.02"))
    transaction_timeout: int = int(os.getenv("TRANSACTION_TIMEOUT", "60"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    def validate_bybit_credentials(self) -> bool:
        """Проверка API ключей ByBit"""
        return bool(self.bybit_api_key and self.bybit_api_secret)
    
    def get_exchange_credentials(self, exchange_name: str) -> Optional[dict]:
        """Получение credentials для обменника"""
        credentials = {
            'binance': {
                'apiKey': self.binance_api_key,
                'secret': self.binance_api_secret
            },
            'kucoin': {
                'apiKey': self.kucoin_api_key,
                'secret': self.kucoin_api_secret,
                'passphrase': self.kucoin_passphrase
            }
        }
        
        return credentials.get(exchange_name.lower())

# Глобальный объект настроек
settings = Settings()

# Алиас для обратной совместимости (если где-то используется BybitConfig)
BybitConfig = Settings

# Экспортируемые объекты
__all__ = ['Settings', 'settings', 'BybitConfig']
