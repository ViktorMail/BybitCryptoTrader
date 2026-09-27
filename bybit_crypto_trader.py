"""
Bybit Crypto Trader - автоматический мониторинг и покупка криптовалют
"""
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pybit.unified_trading import HTTP
from colorama import init, Fore, Back, Style
import schedule

from config import BybitConfig

# Инициализация цветного вывода
init(autoreset=True)

class BybitCryptoTrader:
    """Класс для мониторинга и автоматической торговли на Bybit"""
    
    def __init__(self):
        """Инициализация трейдера"""
        self.config = BybitConfig()
        self.session = None
        self.price_history = {}
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()
        self.initialize_session()
    
    def initialize_session(self):
        """Инициализация сессии с Bybit API"""
        try:
            # Проверяем конфигурацию
            is_valid, message = self.config.validate_config()
            if not is_valid:
                print(f"{Fore.RED}❌ Ошибка конфигурации: {message}")
                return False
            
            # Создаем сессию
            self.session = HTTP(
                api_key=self.config.API_KEY,
                api_secret=self.config.API_SECRET,
                testnet=self.config.TESTNET
            )
            
            # Проверяем подключение
            account_info = self.session.get_wallet_balance(
                accountType="UNIFIED"
            )
            
            if account_info['retCode'] == 0:
                print(f"{Fore.GREEN}✅ Успешное подключение к Bybit API")
                print(f"{Fore.BLUE}ℹ️  Режим: {'TESTNET' if self.config.TESTNET else 'MAINNET'}")
                return True
            else:
                print(f"{Fore.RED}❌ Ошибка подключения: {account_info['retMsg']}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка инициализации: {str(e)}")
            return False
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Получить текущую цену криптовалюты"""
        try:
            ticker = self.session.get_tickers(
                category="spot",
                symbol=symbol
            )
            
            if ticker['retCode'] == 0 and ticker['result']['list']:
                price = float(ticker['result']['list'][0]['lastPrice'])
                return price
            else:
                print(f"{Fore.YELLOW}⚠️  Не удалось получить цену для {symbol}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка получения цены для {symbol}: {str(e)}")
            return None
    
    def calculate_price_change(self, symbol: str, current_price: float) -> Optional[float]:
        """Вычислить изменение цены в процентах"""
        if symbol not in self.price_history:
            # Первый запуск - сохраняем базовую цену
            self.price_history[symbol] = {
                'base_price': current_price,
                'last_price': current_price,
                'timestamp': datetime.now()
            }
            return 0.0
        
        base_price = self.price_history[symbol]['base_price']
        
        # Обновляем историю каждые 24 часа
        if datetime.now() - self.price_history[symbol]['timestamp'] > timedelta(hours=24):
            self.price_history[symbol]['base_price'] = current_price
            self.price_history[symbol]['timestamp'] = datetime.now()
            base_price = current_price
        
        self.price_history[symbol]['last_price'] = current_price
        
        price_change = ((current_price - base_price) / base_price) * 100
        return price_change
    
    def should_buy(self, symbol: str, price_change: float) -> bool:
        """Определить, нужно ли покупать криптовалюту"""
        # Проверяем, включена ли автоматическая покупка
        if not self.config.USER_SETTINGS['auto_buy_enabled']:
            return False
        
        # Проверяем, есть ли символ в целевых для покупки
        target_symbols = self.config.get_user_targets()
        if symbol not in target_symbols:
            return False
        
        # Проверяем дневной лимит сделок
        if self.daily_trades >= self.config.USER_SETTINGS['max_daily_trades']:
            return False
        
        # Проверяем пороговое значение для покупки
        buy_thresholds = self.config.USER_SETTINGS['buy_thresholds']
        if symbol in buy_thresholds:
            threshold = buy_thresholds[symbol]
            return price_change <= threshold
        
        return False
    
    def get_coin_balance(self, symbol: str) -> float:
        """Получить баланс криптовалюты"""
        try:
            # Извлекаем базовую валюту из символа (например, BTC из BTCUSDT)
            coin = symbol.replace('USDT', '')
            
            balance_info = self.session.get_wallet_balance(accountType="UNIFIED")
            
            if balance_info['retCode'] == 0:
                for coin_data in balance_info['result']['list'][0]['coin']:
                    if coin_data['coin'] == coin:
                        return float(coin_data['walletBalance'])
                return 0.0
            else:
                print(f"{Fore.YELLOW}⚠️  Не удалось получить баланс для {coin}")
                return 0.0
                
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка получения баланса для {symbol}: {str(e)}")
            return 0.0
    
    def execute_buy_order(self, symbol: str, amount_usdt: float) -> bool:
        """Выполнить покупку криптовалюты"""
        try:
            print(f"{Fore.BLUE}🛒 Попытка покупки {symbol} на сумму {amount_usdt} USDT...")
            
            # Размещаем market order на покупку
            order = self.session.place_order(
                category="spot",
                symbol=symbol,
                side="Buy",
                orderType="Market",
                qty=str(amount_usdt),  # В USDT для market orders
                marketUnit="quoteCoin"
            )
            
            if order['retCode'] == 0:
                order_id = order['result']['orderId']
                print(f"{Fore.GREEN}✅ Ордер на покупку размещен успешно!")
                print(f"{Fore.GREEN}   Order ID: {order_id}")
                print(f"{Fore.GREEN}   Символ: {symbol}")
                print(f"{Fore.GREEN}   Сумма: {amount_usdt} USDT")
                
                self.daily_trades += 1
                return True
            else:
                print(f"{Fore.RED}❌ Ошибка размещения ордера: {order['retMsg']}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка выполнения покупки {symbol}: {str(e)}")
            return False
    
    def execute_sell_order(self, symbol: str, amount_to_sell: float = None, sell_percentage: float = None) -> bool:
        """Выполнить продажу криптовалюты"""
        try:
            # Получаем текущий баланс монеты
            current_balance = self.get_coin_balance(symbol)
            
            if current_balance <= 0:
                print(f"{Fore.YELLOW}⚠️  Нет позиции для продажи {symbol}")
                return False
            
            # Определяем количество для продажи
            if amount_to_sell is not None:
                # Продажа точного количества
                qty_to_sell = min(amount_to_sell, current_balance)
            elif sell_percentage is not None:
                # Продажа процента от позиции
                qty_to_sell = current_balance * (sell_percentage / 100.0)
            else:
                # По умолчанию продаем всё
                qty_to_sell = current_balance
            
            if qty_to_sell < 0.000001:  # Минимальное количество для торговли
                print(f"{Fore.YELLOW}⚠️  Недостаточно монет для продажи {symbol}")
                return False
            
            print(f"{Fore.BLUE}💰 Попытка продажи {qty_to_sell:.6f} {symbol.replace('USDT', '')}...")
            
            # Размещаем market order на продажу
            order = self.session.place_order(
                category="spot",
                symbol=symbol,
                side="Sell",
                orderType="Market",
                qty=str(qty_to_sell),  # Количество монет для продажи
                marketUnit="baseCoin"
            )
            
            if order['retCode'] == 0:
                order_id = order['result']['orderId']
                print(f"{Fore.GREEN}✅ Ордер на продажу размещен успешно!")
                print(f"{Fore.GREEN}   Order ID: {order_id}")
                print(f"{Fore.GREEN}   Символ: {symbol}")
                print(f"{Fore.GREEN}   Количество: {qty_to_sell:.6f}")
                
                self.daily_trades += 1
                return True
            else:
                print(f"{Fore.RED}❌ Ошибка размещения ордера на продажу: {order['retMsg']}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка выполнения продажи {symbol}: {str(e)}")
            return False
    
    def display_market_summary(self, prices_data: Dict[str, Dict]):
        """Отобразить сводку по рынку"""
        print(f"\n{Back.BLUE}{Fore.WHITE} 📊 СВОДКА ПО РЫНКУ - {datetime.now().strftime('%H:%M:%S')} {Style.RESET_ALL}")
        print("=" * 80)
        
        target_symbols = self.config.get_user_targets()
        
        for symbol, data in prices_data.items():
            price = data['price']
            change = data['change']
            
            # Цветовая индикация изменения цены
            if change > 0:
                change_color = Fore.GREEN
                change_icon = "📈"
            elif change < 0:
                change_color = Fore.RED
                change_icon = "📉"
            else:
                change_color = Fore.YELLOW
                change_icon = "➡️"
            
            # Отметка целевых криптовалют
            target_mark = "🎯" if symbol in target_symbols else "  "
            
            print(f"{target_mark} {symbol:10} | "
                  f"${price:>10.6f} | "
                  f"{change_color}{change:>+7.2f}% {change_icon}")
        
        print("=" * 80)
        print(f"Сделок сегодня: {self.daily_trades}/{self.config.USER_SETTINGS['max_daily_trades']}")
        print(f"Автопокупка: {'🟢 Включена' if self.config.USER_SETTINGS['auto_buy_enabled'] else '🔴 Отключена'}")
        print(f"Целевые активы: {', '.join(target_symbols)}")
    
    def reset_daily_counter(self):
        """Сброс дневного счетчика сделок"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_trades = 0
            self.last_reset_date = current_date
            print(f"{Fore.BLUE}🔄 Счетчик дневных сделок сброшен")
    
    def monitor_and_trade(self):
        """Основная функция мониторинга и торговли"""
        print(f"{Fore.CYAN}🔍 Запуск мониторинга криптовалют...")
        
        if not self.session:
            print(f"{Fore.RED}❌ Сессия не инициализирована")
            return
        
        self.reset_daily_counter()
        
        watchlist = self.config.USER_SETTINGS['watchlist']
        prices_data = {}
        
        for symbol in watchlist:
            current_price = self.get_current_price(symbol)
            
            if current_price is not None:
                price_change = self.calculate_price_change(symbol, current_price)
                
                prices_data[symbol] = {
                    'price': current_price,
                    'change': price_change
                }
                
                # Проверяем условия для покупки
                if self.should_buy(symbol, price_change):
                    buy_amount = self.config.USER_SETTINGS['buy_amount_usdt']
                    print(f"{Fore.MAGENTA}🚨 Триггер покупки активирован для {symbol}!")
                    print(f"{Fore.MAGENTA}   Падение: {price_change:.2f}%")
                    
                    success = self.execute_buy_order(symbol, buy_amount)
                    if success and self.config.USER_SETTINGS['notifications']['trade_confirmations']:
                        print(f"{Fore.GREEN}📧 Уведомление: Покупка {symbol} выполнена успешно!")
        
        # Отображаем сводку
        if prices_data:
            self.display_market_summary(prices_data)
    
    def start_monitoring(self):
        """Запуск непрерывного мониторинга"""
        print(f"{Fore.CYAN}🚀 Запуск Bybit Crypto Trader")
        print(f"{Fore.CYAN}⏰ Интервал мониторинга: {self.config.MONITOR_INTERVAL} секунд")
        
        # Настройка расписания
        interval = self.config.MONITOR_INTERVAL
        schedule.every(interval).seconds.do(self.monitor_and_trade)
        
        # Первый запуск
        self.monitor_and_trade()
        
        # Основной цикл
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  Остановка мониторинга...")
            print(f"{Fore.GREEN}✨ Спасибо за использование Bybit Crypto Trader!")

def main():
    """Главная функция"""
    import sys
    
    # Проверяем аргументы командной строки
    if "--gui" in sys.argv or len(sys.argv) == 1:
        # Запускаем GUI режим
        try:
            from gui_main import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"{Fore.RED}❌ Ошибка импорта GUI: {str(e)}")
            print(f"{Fore.YELLOW}⚠️  Установите GUI зависимости: pip install ttkbootstrap matplotlib pandas")
            print(f"{Fore.BLUE}🔄 Переключаемся на консольный режим...")
            console_mode()
    elif "--console" in sys.argv:
        # Принудительный консольный режим
        console_mode()
    else:
        print(f"{Fore.BLUE}📋 Использование:")
        print(f"   python bybit_crypto_trader.py         - GUI режим (по умолчанию)")
        print(f"   python bybit_crypto_trader.py --gui   - GUI режим")
        print(f"   python bybit_crypto_trader.py --console - Консольный режим")

def console_mode():
    """Консольный режим"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print(f"{Fore.MAGENTA}🚀 BYBIT CRYPTO TRADER - КОНСОЛЬНЫЙ РЕЖИМ")
    print(f"{Fore.MAGENTA}{'='*60}")
    
    trader = BybitCryptoTrader()
    
    # Показываем текущие настройки
    print(f"\n{Fore.BLUE}📋 Текущие настройки:")
    config = BybitConfig()
    print(f"   • Режим: {'TESTNET' if config.TESTNET else 'MAINNET'}")
    print(f"   • Автопокупка: {'Включена' if config.USER_SETTINGS['auto_buy_enabled'] else 'Отключена'}")
    print(f"   • Целевые активы: {', '.join(config.get_user_targets())}")
    print(f"   • Сумма покупки: {config.USER_SETTINGS['buy_amount_usdt']} USDT")
    print(f"   • Интервал: {config.MONITOR_INTERVAL} сек")
    
    print(f"\n{Fore.YELLOW}⚠️  Для настройки используйте GUI режим или отредактируйте config.py")
    print(f"{Fore.YELLOW}⚠️  Настройте API ключи в файле .env или в config.py")
    print(f"\n{Fore.BLUE}💡 Запустите без аргументов для GUI режима с удобной настройкой")
    
    choice = input(f"\n{Fore.GREEN}Продолжить мониторинг? (y/N): ").lower()
    
    if choice in ['y', 'yes', 'да']:
        trader.start_monitoring()
    else:
        print(f"{Fore.BLUE}👋 До свидания!")

if __name__ == "__main__":
    main()