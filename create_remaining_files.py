"""
Создание основных Python модулов проекта
"""
import os

def create_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Создан файл: {filename}")

def main():
    print("📦 Создание основных модулей проекта...")
    
    # Переходим в папку проекта если её нет
    if os.path.exists("BybitCryptoTrader"):
        os.chdir("BybitCryptoTrader")
    
    # Создаем файл config.py
    config_content = '''"""
Конфигурационный модуль для Bybit крипто-трейдера
"""
import os
from dotenv import load_dotenv

load_dotenv()

class BybitConfig:
    API_KEY = os.getenv('BYBIT_API_KEY', 'YOUR_API_KEY_HERE')
    API_SECRET = os.getenv('BYBIT_API_SECRET', 'YOUR_API_SECRET_HERE')
    TESTNET = os.getenv('BYBIT_TESTNET', 'True').lower() == 'true'
    MONITOR_INTERVAL = int(os.getenv('MONITOR_INTERVAL', '60'))
    
    USER_SETTINGS = {
        'watchlist': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT'],
        'auto_buy_enabled': False,
        'buy_amount_usdt': 10.0,
        'max_daily_trades': 5,
        'auto_sell_enabled': False,
        'sell_percentage': 50.0,
        'sell_all_positions': False,
        'buy_thresholds': {
            'BTCUSDT': -5.0, 'ETHUSDT': -4.0, 'ADAUSDT': -6.0,
            'SOLUSDT': -5.5, 'DOTUSDT': -5.0
        },
        'sell_thresholds': {
            'BTCUSDT': 10.0, 'ETHUSDT': 8.0, 'ADAUSDT': 12.0,
            'SOLUSDT': 11.0, 'DOTUSDT': 10.0
        },
        'target_symbols': ['BTCUSDT'],
        'notifications': {
            'price_alerts': True, 'trade_confirmations': True, 
            'error_notifications': True
        }
    }
    
    @classmethod
    def validate_config(cls):
        if cls.API_KEY == 'YOUR_API_KEY_HERE':
            return False, "Не настроены API ключи"
        return True, "Конфигурация валидна"
    
    @classmethod
    def get_user_targets(cls):
        return cls.USER_SETTINGS['target_symbols']
    
    @classmethod
    def set_user_targets(cls, symbols):
        cls.USER_SETTINGS['target_symbols'] = symbols
'''
    create_file("config.py", config_content)
    
    print("\n✅ Базовые файлы созданы!")
    print("📝 Для получения полных модулей GUI и торговли:")
    print("   Скопируйте оставшиеся файлы из моих следующих сообщений")

if __name__ == "__main__":
    main()
