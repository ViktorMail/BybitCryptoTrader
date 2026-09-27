#!/usr/bin/env python3
"""
Консольная версия крипто-бота, совместимая с exe компиляцией
Исправляет проблемы с input() в скомпилированных exe файлах
"""

import sys
import os
import time
from loguru import logger

# Добавление текущей папки в путь Python для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Фикс для exe: создание fake stdin если его нет
if not hasattr(sys.stdin, 'isatty') or not sys.stdin.isatty():
    import io
    sys.stdin = io.StringIO("")

try:
    from crypto_trading_bot import CryptoTradingBot
    from config import settings
    from bybit_client import ByBitClient
    from exchange_manager import ExchangeManager
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все файлы находятся в одной папке с exe")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

class ConsoleInterface:
    """Упрощенный консольный интерфейс для exe"""
    
    def __init__(self):
        self.bot = None
        
    def safe_input(self, prompt):
        """Безопасный ввод для exe"""
        try:
            print(prompt, end=" ")
            return input().strip()
        except (EOFError, KeyboardInterrupt):
            return None
        except Exception:
            # Fallback для exe
            import tkinter as tk
            from tkinter import simpledialog
            
            root = tk.Tk()
            root.withdraw()  # Скрыть главное окно
            
            result = simpledialog.askstring("Ввод", prompt)
            root.destroy()
            
            return result if result else None
    
    def show_menu(self):
        """Отобразить главное меню"""
        print("\n" + "="*60)
        print("🤖 CRYPTO TRADING BOT - КОНСОЛЬНАЯ ВЕРСИЯ")
        print("="*60)
        print("1. Проверить подключение к ByBit")
        print("2. Показать доступные криптовалюты")
        print("3. Запустить автоматическую торговлю")
        print("4. Проверить баланс")
        print("5. Выход")
        print("="*60)
    
    def check_connection(self):
        """Проверка подключения"""
        print("\n🔄 Проверка подключения к ByBit...")
        
        try:
            if not settings.validate_bybit_credentials():
                print("❌ API ключи ByBit не настроены!")
                print("Создайте файл .env с вашими ключами")
                return False
            
            self.bot = CryptoTradingBot()
            success = self.bot.initialize()
            
            if success:
                print("✅ Подключение к ByBit успешно!")
                return True
            else:
                print("❌ Ошибка подключения к ByBit")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def run(self):
        """Запуск консольного интерфейса"""
        print("🤖 Добро пожаловать в Crypto Trading Bot!")
        
        while True:
            try:
                self.show_menu()
                
                choice = self.safe_input("Выберите пункт меню:")
                
                if not choice:
                    continue
                
                if choice == '1':
                    self.check_connection()
                elif choice == '2':
                    print("Функция в разработке")
                elif choice == '3':
                    print("Функция в разработке")
                elif choice == '4':
                    print("Функция в разработке")
                elif choice == '5':
                    print("👋 До свидания!")
                    break
                else:
                    print("❌ Неверный выбор")
                
                if choice != '5':
                    input("\nНажмите Enter для продолжения...")
                    
            except KeyboardInterrupt:
                print("\n👋 Программа завершена пользователем")
                break
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
                logger.error(f"Ошибка в консольном интерфейсе: {e}")

def is_exe_environment():
    """Определение запуска из exe файла"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def main():
    """Главная функция"""
    try:
        # В exe среде все модули уже встроены, проверка файлов не нужна
        if not is_exe_environment():
            # Проверка наличия необходимых файлов только для обычного Python
            required_files = [
                'config.py', 'bybit_client.py', 'exchange_manager.py',
                'crypto_trading_bot.py', 'user_interface.py'
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if missing_files:
                print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
                print("Убедитесь, что все файлы находятся в одной папке с exe")
                input("Нажмите Enter для выхода...")
                return
        
        # Запуск интерфейса
        interface = ConsoleInterface()
        interface.run()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
