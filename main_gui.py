#!/usr/bin/env python3
"""
GUI версия крипто-бота для компиляции в exe
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import queue
from pathlib import Path

# Безопасный импорт логирования с fallback
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

# Добавление текущей папки в путь Python для импортов  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from crypto_trading_bot import CryptoTradingBot
    from config import settings
    from bybit_client import ByBitClient
    from exchange_manager import ExchangeManager
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все файлы находятся в одной папке с exe")
    sys.exit(1)

class CryptoTradingGUI:
    """GUI интерфейс для крипто-бота"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Crypto Trading Bot v1.0")
        self.root.geometry("800x600")
        
        # Очередь для обмена данными между потоками
        self.message_queue = queue.Queue()
        
        # Переменные для данных
        self.bot = None
        self.cryptocurrencies = []
        self.selected_crypto = None
        self.trading_amount = 100.0
        
        self.setup_ui()
        self.check_credentials()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Обновить список", command=self.refresh_cryptos).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="⚙️ API Настройки", command=self.show_api_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="💰 Купить", command=self.manual_buy).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="💸 Продать", command=self.manual_sell).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🚀 Авто торговля", command=self.start_auto_trading).pack(side=tk.LEFT)
        
        # Список криптовалют
        crypto_frame = ttk.LabelFrame(main_frame, text="Доступные криптовалюты")
        crypto_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Таблица криптовалют
        columns = ('symbol', 'name', 'price', 'change')
        self.crypto_tree = ttk.Treeview(crypto_frame, columns=columns, show='headings')
        
        self.crypto_tree.heading('symbol', text='Символ')
        self.crypto_tree.heading('name', text='Название') 
        self.crypto_tree.heading('price', text='Цена')
        self.crypto_tree.heading('change', text='Изменение %')
        
        self.crypto_tree.pack(fill=tk.BOTH, expand=True)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Журнал событий")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=10)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def check_credentials(self):
        """Проверка настроек API"""
        if not settings.validate_bybit_credentials():
            messagebox.showwarning(
                "Настройки API", 
                "API ключи ByBit не настроены!\n\nСоздайте файл .env с вашими ключами."
            )
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        logger.info(message)
    
    def refresh_cryptos(self):
        """Обновление списка криптовалют"""
        self.log_message("🔄 Загрузка списка криптовалют...")
        
        def load_cryptos():
            try:
                if not self.bot:
                    self.bot = CryptoTradingBot()
                    
                cryptos = self.bot.get_available_cryptocurrencies()
                
                # Обновляем UI в главном потоке
                self.root.after(0, self.update_crypto_list, cryptos)
                
            except Exception as e:
                self.root.after(0, self.log_message, f"❌ Ошибка: {e}")
        
        threading.Thread(target=load_cryptos, daemon=True).start()
    
    def update_crypto_list(self, cryptos):
        """Обновление таблицы криптовалют"""
        # Очищаем таблицу
        for item in self.crypto_tree.get_children():
            self.crypto_tree.delete(item)
            
        # Добавляем новые данные
        for crypto in cryptos[:20]:  # Показываем топ 20
            self.crypto_tree.insert('', 'end', values=(
                crypto['symbol'],
                crypto.get('name', 'Unknown'),
                f"${crypto.get('price', 'N/A')}",
                f"{crypto.get('change', 'N/A')}%"
            ))
            
        self.log_message(f"✅ Загружено {len(cryptos)} криптовалют")
    
    def show_api_settings(self):
        """Окно настроек API ключей"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ API Настройки ByBit")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Основной фрейм с прокруткой
        canvas = tk.Canvas(settings_window)
        scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ByBit API настройки
        ttk.Label(scrollable_frame, text="🔑 ByBit API Настройки", font=("Arial", 12, "bold")).pack(pady=10)
        
        # API Key
        ttk.Label(scrollable_frame, text="API Key:").pack(anchor="w", padx=10, pady=(5,0))
        api_key_var = tk.StringVar(value=settings.bybit_api_key)
        api_key_entry = ttk.Entry(scrollable_frame, textvariable=api_key_var, width=60, show="*")
        api_key_entry.pack(padx=10, pady=2, fill=tk.X)
        
        # API Secret
        ttk.Label(scrollable_frame, text="API Secret:").pack(anchor="w", padx=10, pady=(10,0))
        api_secret_var = tk.StringVar(value=settings.bybit_api_secret)
        api_secret_entry = ttk.Entry(scrollable_frame, textvariable=api_secret_var, width=60, show="*")
        api_secret_entry.pack(padx=10, pady=2, fill=tk.X)
        
        # Testnet режим
        testnet_var = tk.BooleanVar(value=settings.bybit_testnet)
        ttk.Checkbutton(scrollable_frame, text="🧪 Тестовый режим (Testnet)", variable=testnet_var).pack(anchor="w", padx=10, pady=10)
        
        # Торговые настройки
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(scrollable_frame, text="💰 Торговые настройки", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Сумма торговли
        ttk.Label(scrollable_frame, text="Сумма для торговли (USD):").pack(anchor="w", padx=10, pady=(5,0))
        amount_var = tk.StringVar(value=str(settings.default_trading_amount))
        amount_entry = ttk.Entry(scrollable_frame, textvariable=amount_var, width=20)
        amount_entry.pack(anchor="w", padx=10, pady=2)
        
        def save_settings():
            """Сохранение настроек"""
            try:
                # Сохраняем в переменные окружения (временно)
                os.environ["BYBIT_API_KEY"] = api_key_var.get()
                os.environ["BYBIT_API_SECRET"] = api_secret_var.get()
                os.environ["BYBIT_TESTNET"] = str(testnet_var.get()).lower()
                os.environ["DEFAULT_TRADING_AMOUNT"] = amount_var.get()
                
                # Обновляем объект settings
                settings.bybit_api_key = api_key_var.get()
                settings.bybit_api_secret = api_secret_var.get()
                settings.bybit_testnet = testnet_var.get()
                settings.default_trading_amount = float(amount_var.get())
                
                self.log_message("✅ Настройки API сохранены")
                
                messagebox.showinfo("Успех", "Настройки сохранены!")
                settings_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
        
        # Кнопки
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="💾 Сохранить", command=save_settings).pack(side=tk.LEFT, padx=(10,5))
        ttk.Button(button_frame, text="❌ Отмена", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def manual_buy(self):
        """Ручная покупка криптовалюты"""
        selection = self.crypto_tree.selection()
        if not selection:
            messagebox.showwarning("Выбор", "Выберите криптовалюту для покупки")
            return
            
        item = self.crypto_tree.item(selection[0])
        symbol = item['values'][0]
        current_price = item['values'][2]
        
        # Запрашиваем сумму для покупки
        amount = tk.simpledialog.askfloat(
            "Покупка",
            f"Введите сумму для покупки {symbol}:\n(Текущая цена: {current_price})",
            initialvalue=settings.default_trading_amount,
            minvalue=1.0,
            maxvalue=10000.0
        )
        
        if amount is None:
            return
        
        # Подтверждение покупки
        confirmed = messagebox.askyesno(
            "Подтверждение покупки",
            f"Купить {symbol} на сумму ${amount:.2f}?"
        )
        
        if confirmed:
            self.log_message(f"💰 Покупка {symbol} на ${amount:.2f}")
    
    def manual_sell(self):
        """Ручная продажа криптовалюты"""
        selection = self.crypto_tree.selection()
        if not selection:
            messagebox.showwarning("Выбор", "Выберите криптовалюту для продажи")
            return
            
        item = self.crypto_tree.item(selection[0])
        symbol = item['values'][0]
        
        self.log_message(f"💸 Продажа {symbol}")
    
    def start_auto_trading(self):
        """Запуск автоматической торговли"""
        selection = self.crypto_tree.selection()
        if not selection:
            messagebox.showwarning("Выбор", "Выберите криптовалюту для автоматической торговли")
            return
            
        item = self.crypto_tree.item(selection[0])
        symbol = item['values'][0]
        
        confirmed = messagebox.askyesno(
            "Подтверждение автоторговли",
            f"Запустить автоматическую торговлю {symbol}?\n\n"
            f"Операция: Покупка → Поиск лучших курсов → Продажа\n"
            f"Сумма: ${settings.default_trading_amount:.2f}"
        )
        
        if confirmed:
            self.log_message(f"🚀 Запуск автоторговли {symbol}")
            # Здесь будет логика автоторговли
    
    def run(self):
        """Запуск GUI"""
        self.log_message("🤖 Crypto Trading Bot запущен")
        self.root.mainloop()

def main():
    """Главная функция для совместимости"""
    try:
        app = CryptoTradingGUI()
        app.run()
    except Exception as e:
        logger.error(f"Критическая ошибка GUI: {e}")
        messagebox.showerror("Критическая ошибка", f"Не удалось запустить приложение:\n{e}")

if __name__ == "__main__":
    main()
