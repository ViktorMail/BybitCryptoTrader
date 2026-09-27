"""
GUI диалоги для настройки Bybit Crypto Trader
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import json
import os
from typing import List, Dict, Optional, Tuple
from pybit.unified_trading import HTTP

class LoginDialog:
    """Диалог входа в личный кабинет"""
    
    def __init__(self, parent=None):
        self.result = None
        self.window = tb.Toplevel(parent) if parent else tb.Window(themename="darkly")
        self.window.title("🚀 Bybit Crypto Trader - Вход в личный кабинет")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # Центрирование окна
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = tb.Frame(self.window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        title_label = tb.Label(
            main_frame, 
            text="🔐 Настройка API ключей Bybit",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Инструкции
        instructions = tb.Text(main_frame, height=4, wrap=tk.WORD, state=DISABLED)
        instructions.pack(fill=X, pady=(0, 15))
        instructions.config(state=tk.NORMAL)
        instructions.insert(tk.END, 
            "1. Войдите на bybit.com\n"
            "2. Перейдите в API Management\n"
            "3. Создайте API ключ с правами spot trading\n"
            "4. Введите ключи ниже:")
        instructions.config(state=DISABLED)
        
        # Поля ввода
        tb.Label(main_frame, text="API Key:").pack(anchor=W, pady=(10, 5))
        self.api_key_var = tb.StringVar()
        self.api_key_entry = tb.Entry(
            main_frame, 
            textvariable=self.api_key_var,
            font=("Courier", 10),
            width=60
        )
        self.api_key_entry.pack(fill=X, pady=(0, 10))
        
        tb.Label(main_frame, text="API Secret:").pack(anchor=W, pady=(0, 5))
        self.api_secret_var = tb.StringVar()
        self.api_secret_entry = tb.Entry(
            main_frame, 
            textvariable=self.api_secret_var,
            font=("Courier", 10),
            show="*",
            width=60
        )
        self.api_secret_entry.pack(fill=X, pady=(0, 15))
        
        # Режим работы
        mode_frame = tb.LabelFrame(main_frame, text="Режим работы", padding=10)
        mode_frame.pack(fill=X, pady=(0, 15))
        
        self.testnet_var = tb.BooleanVar(value=True)
        tb.Checkbutton(
            mode_frame,
            text="🧪 Тестовая сеть (рекомендуется для начала)",
            variable=self.testnet_var,
            bootstyle="success"
        ).pack(anchor=W)
        
        tb.Label(
            mode_frame, 
            text="⚠️ Отключите для реальной торговли",
            foreground="orange"
        ).pack(anchor=W, pady=(5, 0))
        
        # Кнопки
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X, pady=(15, 0))
        
        tb.Button(
            button_frame,
            text="🧪 Тестировать подключение",
            command=self.test_connection,
            bootstyle="info"
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            button_frame,
            text="✅ Сохранить и продолжить",
            command=self.save_and_continue,
            bootstyle="success"
        ).pack(side=LEFT, padx=10)
        
        tb.Button(
            button_frame,
            text="❌ Отмена",
            command=self.cancel,
            bootstyle="danger"
        ).pack(side=RIGHT)
        
    def test_connection(self):
        """Тестирование подключения к API"""
        api_key = self.api_key_var.get().strip()
        api_secret = self.api_secret_var.get().strip()
        testnet = self.testnet_var.get()
        
        if not api_key or not api_secret:
            messagebox.showerror("Ошибка", "Пожалуйста, введите API ключи")
            return
            
        try:
            # Тестируем подключение
            session = HTTP(
                api_key=api_key,
                api_secret=api_secret,
                testnet=testnet
            )
            
            # Проверяем подключение
            account_info = session.get_wallet_balance(accountType="UNIFIED")
            
            if account_info['retCode'] == 0:
                mode_text = "TESTNET" if testnet else "MAINNET" 
                messagebox.showinfo(
                    "✅ Успех!", 
                    f"Подключение к Bybit API успешно!\nРежим: {mode_text}"
                )
            else:
                messagebox.showerror(
                    "❌ Ошибка", 
                    f"Ошибка API: {account_info['retMsg']}"
                )
                
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Не удалось подключиться: {str(e)}")
    
    def save_and_continue(self):
        """Сохранить настройки и продолжить"""
        api_key = self.api_key_var.get().strip()
        api_secret = self.api_secret_var.get().strip()
        testnet = self.testnet_var.get()
        
        if not api_key or not api_secret:
            messagebox.showerror("Ошибка", "Пожалуйста, введите API ключи")
            return
            
        self.result = {
            'api_key': api_key,
            'api_secret': api_secret,
            'testnet': testnet
        }
        
        self.window.destroy()
    
    def cancel(self):
        """Отмена"""
        self.result = None
        self.window.destroy()
    
    def show(self):
        """Показать диалог и дождаться результата"""
        self.window.wait_window()
        return self.result

class CryptoSelectionDialog:
    """Диалог выбора криптовалют"""
    
    def __init__(self, parent, api_credentials):
        self.parent = parent
        self.api_credentials = api_credentials
        self.result = None
        self.all_symbols = []
        self.selected_symbols = []
        
        self.window = tb.Toplevel(parent)
        self.window.title("🎯 Выбор криптовалют для мониторинга и торговли")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_symbols()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = tb.Frame(self.window, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        title_label = tb.Label(
            main_frame,
            text="🎯 Выберите криптовалюты",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Инструкции
        tb.Label(
            main_frame,
            text="Выберите криптовалюты для мониторинга и отметьте ⭐ те, которые хотите покупать автоматически:",
            wraplength=750
        ).pack(pady=(0, 15))
        
        # Поиск
        search_frame = tb.Frame(main_frame)
        search_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(search_frame, text="🔍 Поиск:").pack(side=LEFT, padx=(0, 5))
        self.search_var = tb.StringVar()
        self.search_var.trace("w", self.filter_symbols)
        search_entry = tb.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=LEFT, padx=(0, 10))
        
        # Быстрые фильтры
        tb.Button(
            search_frame, text="BTC", 
            command=lambda: self.search_var.set("BTC"),
            bootstyle="outline"
        ).pack(side=LEFT, padx=2)
        
        tb.Button(
            search_frame, text="ETH", 
            command=lambda: self.search_var.set("ETH"),
            bootstyle="outline"
        ).pack(side=LEFT, padx=2)
        
        tb.Button(
            search_frame, text="USDT", 
            command=lambda: self.search_var.set("USDT"),
            bootstyle="outline"
        ).pack(side=LEFT, padx=2)
        
        tb.Button(
            search_frame, text="Очистить", 
            command=lambda: self.search_var.set(""),
            bootstyle="outline"
        ).pack(side=LEFT, padx=2)
        
        # Таблица с криптовалютами
        self.setup_symbols_table(main_frame)
        
        # Выбранные символы
        selected_frame = tb.LabelFrame(main_frame, text="Выбранные для торговли ⭐", padding=10)
        selected_frame.pack(fill=X, pady=10)
        
        self.selected_text = tb.Text(selected_frame, height=3, state=DISABLED, wrap=tk.WORD)
        self.selected_text.pack(fill=X)
        
        # Кнопки
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X, pady=15)
        
        tb.Button(
            button_frame,
            text="✅ Сохранить выбор",
            command=self.save_selection,
            bootstyle="success"
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            button_frame,
            text="🎲 Популярные",
            command=self.select_popular,
            bootstyle="info"
        ).pack(side=LEFT, padx=10)
        
        tb.Button(
            button_frame,
            text="❌ Отмена",
            command=self.cancel,
            bootstyle="danger"
        ).pack(side=RIGHT)
    
    def setup_symbols_table(self, parent):
        """Настройка таблицы символов"""
        table_frame = tb.Frame(parent)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Treeview с прокруткой
        self.tree = ttk.Treeview(
            table_frame,
            columns=("symbol", "price", "change", "volume", "monitor", "trade"),
            show="headings",
            height=15
        )
        
        # Заголовки
        self.tree.heading("symbol", text="Символ")
        self.tree.heading("price", text="Цена")
        self.tree.heading("change", text="Изменение 24ч")
        self.tree.heading("volume", text="Объём")
        self.tree.heading("monitor", text="Мониторить")
        self.tree.heading("trade", text="Торговать ⭐")
        
        # Ширина колонок
        self.tree.column("symbol", width=120)
        self.tree.column("price", width=100)
        self.tree.column("change", width=100)
        self.tree.column("volume", width=120)
        self.tree.column("monitor", width=80)
        self.tree.column("trade", width=80)
        
        # Прокрутка
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Привязка событий
        self.tree.bind("<Double-1>", self.toggle_selection)
    
    def load_symbols(self):
        """Загрузка списка символов с Bybit"""
        try:
            session = HTTP(
                api_key=self.api_credentials['api_key'],
                api_secret=self.api_credentials['api_secret'],
                testnet=self.api_credentials['testnet']
            )
            
            # Получаем список символов
            tickers = session.get_tickers(category="spot")
            
            if tickers['retCode'] == 0:
                self.all_symbols = []
                for ticker in tickers['result']['list']:
                    symbol_data = {
                        'symbol': ticker['symbol'],
                        'price': float(ticker['lastPrice']),
                        'change': float(ticker['price24hPcnt']) * 100,
                        'volume': float(ticker['volume24h']),
                        'monitor': False,
                        'trade': False
                    }
                    
                    # Фильтруем только USDT пары
                    if symbol_data['symbol'].endswith('USDT'):
                        self.all_symbols.append(symbol_data)
                
                # Сортируем по объёму торгов
                self.all_symbols.sort(key=lambda x: x['volume'], reverse=True)
                
                # Предварительно выбираем популярные
                popular_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']
                for symbol_data in self.all_symbols:
                    if symbol_data['symbol'] in popular_symbols:
                        symbol_data['monitor'] = True
                        if symbol_data['symbol'] in ['BTCUSDT', 'ETHUSDT']:
                            symbol_data['trade'] = True
                
                self.update_symbols_display()
                self.update_selected_display()
                
            else:
                messagebox.showerror("Ошибка", f"Не удалось получить список символов: {tickers['retMsg']}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки символов: {str(e)}")
    
    def filter_symbols(self, *args):
        """Фильтрация символов по поиску"""
        self.update_symbols_display()
    
    def update_symbols_display(self):
        """Обновление отображения символов"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получаем поисковый запрос
        search_term = self.search_var.get().upper()
        
        # Фильтруем и отображаем символы
        for symbol_data in self.all_symbols:
            if not search_term or search_term in symbol_data['symbol']:
                monitor_text = "✅" if symbol_data['monitor'] else ""
                trade_text = "⭐" if symbol_data['trade'] else ""
                
                change_text = f"{symbol_data['change']:+.2f}%"
                volume_text = f"{symbol_data['volume']:,.0f}"
                
                self.tree.insert("", "end", values=(
                    symbol_data['symbol'],
                    f"${symbol_data['price']:.6f}",
                    change_text,
                    volume_text,
                    monitor_text,
                    trade_text
                ))
    
    def toggle_selection(self, event):
        """Переключение выбора символа"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            symbol = self.tree.item(item, 'values')[0]
            
            # Находим символ в данных
            for symbol_data in self.all_symbols:
                if symbol_data['symbol'] == symbol:
                    # Показываем диалог выбора
                    choice = messagebox.askyesnocancel(
                        "Выбор действия",
                        f"Что делать с {symbol}?\n\n"
                        f"ДА - Мониторить и торговать ⭐\n"
                        f"НЕТ - Только мониторить\n"
                        f"ОТМЕНА - Убрать из списка"
                    )
                    
                    if choice is True:  # Да - торговать
                        symbol_data['monitor'] = True
                        symbol_data['trade'] = True
                    elif choice is False:  # Нет - только мониторить
                        symbol_data['monitor'] = True
                        symbol_data['trade'] = False
                    else:  # Отмена - убрать
                        symbol_data['monitor'] = False
                        symbol_data['trade'] = False
                    
                    break
            
            self.update_symbols_display()
            self.update_selected_display()
    
    def update_selected_display(self):
        """Обновление отображения выбранных символов"""
        monitor_symbols = [s['symbol'] for s in self.all_symbols if s['monitor']]
        trade_symbols = [s['symbol'] for s in self.all_symbols if s['trade']]
        
        self.selected_text.config(state=tk.NORMAL)
        self.selected_text.delete(1.0, tk.END)
        self.selected_text.insert(tk.END, 
            f"📊 Мониторинг ({len(monitor_symbols)}): {', '.join(monitor_symbols)}\n\n"
            f"⭐ Торговля ({len(trade_symbols)}): {', '.join(trade_symbols)}"
        )
        self.selected_text.config(state=DISABLED)
    
    def select_popular(self):
        """Выбор популярных криптовалют"""
        popular = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'DOGEUSDT', 'XRPUSDT', 'DOTUSDT']
        
        for symbol_data in self.all_symbols:
            if symbol_data['symbol'] in popular:
                symbol_data['monitor'] = True
                if symbol_data['symbol'] in ['BTCUSDT', 'ETHUSDT']:
                    symbol_data['trade'] = True
        
        self.update_symbols_display()
        self.update_selected_display()
    
    def save_selection(self):
        """Сохранить выбор"""
        monitor_symbols = [s['symbol'] for s in self.all_symbols if s['monitor']]
        trade_symbols = [s['symbol'] for s in self.all_symbols if s['trade']]
        
        if not monitor_symbols:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы одну криптовалюту для мониторинга")
            return
        
        self.result = {
            'watchlist': monitor_symbols,
            'target_symbols': trade_symbols
        }
        
        self.window.destroy()
    
    def cancel(self):
        """Отмена"""
        self.result = None
        self.window.destroy()
    
    def show(self):
        """Показать диалог и дождаться результата"""
        self.window.wait_window()
        return self.result

class TradingSettingsDialog:
    """Диалог настройки торговых параметров"""
    
    def __init__(self, parent, selected_symbols):
        self.parent = parent
        self.selected_symbols = selected_symbols
        self.result = None
        
        self.window = tb.Toplevel(parent)
        self.window.title("⚙️ Настройки торговли")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = tb.Frame(self.window, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        title_label = tb.Label(
            main_frame,
            text="⚙️ Настройки автоматической торговли",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Основные настройки
        settings_frame = tb.LabelFrame(main_frame, text="Основные параметры", padding=10)
        settings_frame.pack(fill=X, pady=(0, 15))
        
        # Автоторговля
        self.auto_buy_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            settings_frame,
            text="🤖 Включить автоматическую покупку",
            variable=self.auto_buy_var
        ).pack(anchor=W, pady=5)
        
        # Сумма покупки
        tb.Label(settings_frame, text="💰 Сумма покупки (USDT):").pack(anchor=W, pady=(10, 5))
        self.buy_amount_var = tb.DoubleVar(value=10.0)
        tb.Entry(settings_frame, textvariable=self.buy_amount_var).pack(anchor=W, pady=(0, 5))
        
        # Лимит сделок
        tb.Label(settings_frame, text="📊 Максимум сделок в день:").pack(anchor=W, pady=(10, 5))
        self.max_trades_var = tb.IntVar(value=5)
        tb.Entry(settings_frame, textvariable=self.max_trades_var).pack(anchor=W, pady=(0, 5))
        
        # Интервал мониторинга
        tb.Label(settings_frame, text="⏰ Интервал мониторинга (секунд):").pack(anchor=W, pady=(10, 5))
        self.monitor_interval_var = tb.IntVar(value=60)
        tb.Entry(settings_frame, textvariable=self.monitor_interval_var).pack(anchor=W, pady=(0, 5))
        
        # Пороговые значения
        if self.selected_symbols.get('target_symbols'):
            thresholds_frame = tb.LabelFrame(main_frame, text="📉 Пороги покупки (% падения)", padding=10)
            thresholds_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
            
            # Создаем canvas для прокрутки
            canvas = tk.Canvas(thresholds_frame)
            scrollbar_thresh = ttk.Scrollbar(thresholds_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tb.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_thresh.set)
            
            self.threshold_vars = {}
            default_thresholds = {
                'BTCUSDT': -5.0, 'ETHUSDT': -4.0, 'BNBUSDT': -4.5,
                'SOLUSDT': -5.5, 'ADAUSDT': -6.0, 'DOGEUSDT': -7.0
            }
            
            for symbol in self.selected_symbols['target_symbols']:
                frame = tb.Frame(scrollable_frame)
                frame.pack(fill=X, padx=5, pady=2)
                
                tb.Label(frame, text=f"{symbol}:", width=15).pack(side=LEFT)
                
                var = tb.DoubleVar(value=default_thresholds.get(symbol, -5.0))
                self.threshold_vars[symbol] = var
                
                entry = tb.Entry(frame, textvariable=var, width=10)
                entry.pack(side=LEFT, padx=5)
                
                tb.Label(frame, text="%").pack(side=LEFT)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_thresh.pack(side="right", fill="y")
        
        # Кнопки
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X, pady=15)
        
        tb.Button(
            button_frame,
            text="✅ Сохранить настройки",
            command=self.save_settings,
            bootstyle="success"
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            button_frame,
            text="🔄 По умолчанию",
            command=self.reset_defaults,
            bootstyle="warning"
        ).pack(side=LEFT, padx=10)
        
        tb.Button(
            button_frame,
            text="❌ Отмена",
            command=self.cancel,
            bootstyle="danger"
        ).pack(side=RIGHT)
    
    def reset_defaults(self):
        """Сброс к значениям по умолчанию"""
        self.auto_buy_var.set(False)
        self.buy_amount_var.set(10.0)
        self.max_trades_var.set(5)
        self.monitor_interval_var.set(60)
        
        default_thresholds = {
            'BTCUSDT': -5.0, 'ETHUSDT': -4.0, 'BNBUSDT': -4.5,
            'SOLUSDT': -5.5, 'ADAUSDT': -6.0, 'DOGEUSDT': -7.0
        }
        
        for symbol, var in getattr(self, 'threshold_vars', {}).items():
            var.set(default_thresholds.get(symbol, -5.0))
    
    def save_settings(self):
        """Сохранить настройки"""
        try:
            buy_thresholds = {}
            for symbol, var in getattr(self, 'threshold_vars', {}).items():
                buy_thresholds[symbol] = var.get()
            
            sell_thresholds = {}
            for symbol, var in getattr(self, 'sell_threshold_vars', {}).items():
                sell_thresholds[symbol] = var.get()
            
            self.result = {
                'auto_buy_enabled': self.auto_buy_var.get(),
                'buy_amount_usdt': self.buy_amount_var.get(),
                'max_daily_trades': self.max_trades_var.get(),
                'monitor_interval': self.monitor_interval_var.get(),
                'buy_thresholds': buy_thresholds,
                'auto_sell_enabled': getattr(self, 'auto_sell_var', tb.BooleanVar(value=False)).get(),
                'sell_percentage': getattr(self, 'sell_percentage_var', tb.DoubleVar(value=50.0)).get(),
                'sell_all_positions': getattr(self, 'sell_all_var', tb.BooleanVar(value=False)).get(),
                'sell_thresholds': sell_thresholds
            }
            
            if self.result['buy_amount_usdt'] <= 0:
                messagebox.showerror("Ошибка", "Сумма покупки должна быть больше 0")
                return
            
            if self.result['max_daily_trades'] <= 0:
                messagebox.showerror("Ошибка", "Лимит сделок должен быть больше 0")
                return
                
            if self.result['monitor_interval'] < 30:
                messagebox.showerror("Ошибка", "Минимальный интервал мониторинга: 30 секунд")
                return
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка в настройках: {str(e)}")
    
    def cancel(self):
        """Отмена"""
        self.result = None
        self.window.destroy()
    
    def show(self):
        """Показать диалог и дождаться результата"""
        self.window.wait_window()
        return self.result

class SellDialog:
    """Диалог для продажи криптовалюты"""
    
    def __init__(self, parent, symbol, current_balance, current_price, trader_session):
        self.parent = parent
        self.symbol = symbol
        self.current_balance = current_balance
        self.current_price = current_price
        self.trader_session = trader_session
        self.result = None
        
        self.window = tb.Toplevel(parent)
        self.window.title(f"💰 Продажа {symbol}")
        self.window.geometry("450x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = tb.Frame(self.window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Заголовок
        title_label = tb.Label(
            main_frame,
            text=f"💰 Продажа {self.symbol}",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Информация о позиции
        info_frame = tb.LabelFrame(main_frame, text="Информация о позиции", padding=10)
        info_frame.pack(fill=X, pady=(0, 15))
        
        coin_name = self.symbol.replace('USDT', '')
        tb.Label(
            info_frame, 
            text=f"Доступно для продажи: {self.current_balance:.6f} {coin_name}",
            font=("Arial", 11, "bold")
        ).pack(anchor=W, pady=2)
        
        tb.Label(
            info_frame, 
            text=f"Текущая цена: ${self.current_price:.6f}",
            font=("Arial", 11)
        ).pack(anchor=W, pady=2)
        
        estimated_value = self.current_balance * self.current_price
        tb.Label(
            info_frame, 
            text=f"Ориентировочная стоимость: {estimated_value:.2f} USDT",
            font=("Arial", 11),
            foreground="green"
        ).pack(anchor=W, pady=2)
        
        # Настройки продажи
        sell_frame = tb.LabelFrame(main_frame, text="Настройки продажи", padding=10)
        sell_frame.pack(fill=X, pady=(0, 15))
        
        # Тип продажи
        self.sell_type_var = tb.StringVar(value="percentage")
        
        tb.Radiobutton(
            sell_frame,
            text="По проценту от позиции",
            variable=self.sell_type_var,
            value="percentage",
            command=self.update_sell_type
        ).pack(anchor=W, pady=5)
        
        self.percentage_frame = tb.Frame(sell_frame)
        self.percentage_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(self.percentage_frame, text="Процент для продажи:").pack(side=LEFT)
        self.sell_percentage_var = tb.DoubleVar(value=50.0)
        percentage_scale = tb.Scale(
            self.percentage_frame,
            from_=1.0, to=100.0,
            orient=HORIZONTAL,
            variable=self.sell_percentage_var,
            command=self.update_preview
        )
        percentage_scale.pack(side=LEFT, fill=X, expand=True, padx=(10, 5))
        
        self.percentage_label = tb.Label(self.percentage_frame, text="50%")
        self.percentage_label.pack(side=LEFT)
        
        tb.Radiobutton(
            sell_frame,
            text="Точное количество",
            variable=self.sell_type_var,
            value="amount",
            command=self.update_sell_type
        ).pack(anchor=W, pady=(10, 5))
        
        self.amount_frame = tb.Frame(sell_frame)
        self.amount_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(self.amount_frame, text=f"Количество {coin_name}:").pack(side=LEFT)
        self.sell_amount_var = tb.DoubleVar(value=self.current_balance / 2)
        amount_entry = tb.Entry(
            self.amount_frame, 
            textvariable=self.sell_amount_var,
            width=15
        )
        amount_entry.pack(side=LEFT, padx=10)
        amount_entry.bind('<KeyRelease>', self.update_preview)
        
        tb.Radiobutton(
            sell_frame,
            text="Продать всё",
            variable=self.sell_type_var,
            value="all",
            command=self.update_sell_type
        ).pack(anchor=W, pady=(10, 5))
        
        # Предварительный расчет
        preview_frame = tb.LabelFrame(main_frame, text="Предварительный расчет", padding=10)
        preview_frame.pack(fill=X, pady=(0, 15))
        
        self.preview_amount_label = tb.Label(preview_frame, text="", font=("Arial", 10, "bold"))
        self.preview_amount_label.pack(anchor=W)
        
        self.preview_value_label = tb.Label(preview_frame, text="", foreground="green")
        self.preview_value_label.pack(anchor=W)
        
        self.preview_remaining_label = tb.Label(preview_frame, text="", foreground="blue")
        self.preview_remaining_label.pack(anchor=W)
        
        # Кнопки
        button_frame = tb.Frame(main_frame)
        button_frame.pack(fill=X, pady=(15, 0))
        
        tb.Button(
            button_frame,
            text="💰 Выполнить продажу",
            command=self.execute_sell,
            bootstyle="success"
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            button_frame,
            text="❌ Отмена",
            command=self.cancel,
            bootstyle="danger"
        ).pack(side=RIGHT)
        
        # Первоначальное обновление
        self.update_sell_type()
        self.update_preview()
    
    def update_sell_type(self):
        """Обновить тип продажи"""
        sell_type = self.sell_type_var.get()
        
        if sell_type == "percentage":
            for widget in self.percentage_frame.winfo_children():
                widget.configure(state="normal")
            for widget in self.amount_frame.winfo_children():
                if isinstance(widget, tb.Entry):
                    widget.configure(state="disabled")
        elif sell_type == "amount":
            for widget in self.percentage_frame.winfo_children():
                if isinstance(widget, tb.Scale):
                    widget.configure(state="disabled")
            for widget in self.amount_frame.winfo_children():
                widget.configure(state="normal")
        else:  # all
            for widget in self.percentage_frame.winfo_children():
                if isinstance(widget, tb.Scale):
                    widget.configure(state="disabled")
            for widget in self.amount_frame.winfo_children():
                if isinstance(widget, tb.Entry):
                    widget.configure(state="disabled")
        
        self.update_preview()
    
    def update_preview(self, *args):
        """Обновить предварительный расчет"""
        try:
            sell_type = self.sell_type_var.get()
            coin_name = self.symbol.replace('USDT', '')
            
            if sell_type == "percentage":
                percentage = self.sell_percentage_var.get()
                amount_to_sell = self.current_balance * (percentage / 100.0)
                self.percentage_label.configure(text=f"{percentage:.0f}%")
            elif sell_type == "amount":
                amount_to_sell = min(self.sell_amount_var.get(), self.current_balance)
            else:  # all
                amount_to_sell = self.current_balance
            
            estimated_value = amount_to_sell * self.current_price
            remaining_balance = self.current_balance - amount_to_sell
            
            self.preview_amount_label.configure(
                text=f"К продаже: {amount_to_sell:.6f} {coin_name}"
            )
            self.preview_value_label.configure(
                text=f"Ориентировочная сумма: {estimated_value:.2f} USDT"
            )
            self.preview_remaining_label.configure(
                text=f"Останется: {remaining_balance:.6f} {coin_name}"
            )
            
        except Exception as e:
            print(f"Ошибка обновления превью: {e}")
    
    def execute_sell(self):
        """Выполнить продажу"""
        try:
            sell_type = self.sell_type_var.get()
            
            if sell_type == "percentage":
                percentage = self.sell_percentage_var.get()
                if percentage <= 0 or percentage > 100:
                    messagebox.showerror("Ошибка", "Процент должен быть от 1 до 100")
                    return
                self.result = {"type": "percentage", "value": percentage}
            elif sell_type == "amount":
                amount = self.sell_amount_var.get()
                if amount <= 0 or amount > self.current_balance:
                    messagebox.showerror("Ошибка", f"Количество должно быть от 0 до {self.current_balance:.6f}")
                    return
                self.result = {"type": "amount", "value": amount}
            else:  # all
                self.result = {"type": "all", "value": 100.0}
            
            # Подтверждение
            sell_type_text = self.sell_type_var.get()
            if sell_type_text == "percentage":
                confirm_text = f"Продать {self.sell_percentage_var.get():.0f}% позиции {self.symbol}?"
            elif sell_type_text == "amount":
                confirm_text = f"Продать {self.sell_amount_var.get():.6f} {self.symbol.replace('USDT', '')}?"
            else:
                confirm_text = f"Продать всю позицию {self.symbol}?"
            
            if messagebox.askyesno("Подтверждение продажи", confirm_text):
                self.window.destroy()
            else:
                self.result = None
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка в настройках продажи: {str(e)}")
    
    def cancel(self):
        """Отмена"""
        self.result = None
        self.window.destroy()
    
    def show(self):
        """Показать диалог и дождаться результата"""
        self.window.wait_window()
        return self.result

def show_setup_wizard():
    """Показать мастер настройки"""
    try:
        # 1. Диалог входа
        login_dialog = LoginDialog()
        api_credentials = login_dialog.show()
        
        if not api_credentials:
            return None
        
        # 2. Выбор криптовалют  
        crypto_dialog = CryptoSelectionDialog(None, api_credentials)
        crypto_selection = crypto_dialog.show()
        
        if not crypto_selection:
            return None
        
        # 3. Настройки торговли
        settings_dialog = TradingSettingsDialog(None, crypto_selection)
        trading_settings = settings_dialog.show()
        
        if not trading_settings:
            return None
        
        # Объединяем все настройки
        final_config = {
            **api_credentials,
            **crypto_selection,
            **trading_settings
        }
        
        return final_config
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка в мастере настройки: {str(e)}")
        return None

if __name__ == "__main__":
    # Тест мастера настройки
    config = show_setup_wizard()
    if config:
        print("Настройки сохранены:", json.dumps(config, indent=2, ensure_ascii=False))
    else:
        print("Настройка отменена")