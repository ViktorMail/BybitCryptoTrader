"""
Запускатель Bybit Crypto Trader с GUI интерфейсом для Windows
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Запуск GUI приложения"""
    try:
        # Импортируем и запускаем GUI
        from gui_main import main as gui_main
        gui_main()
    except ImportError as e:
        # Если не удалось импортировать GUI, показываем ошибку
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        messagebox.showerror(
            "Ошибка запуска",
            f"Не удалось запустить GUI интерфейс.\n\n"
            f"Ошибка: {str(e)}\n\n"
            f"Решение:\n"
            f"1. Установите зависимости: pip install -r requirements.txt\n"
            f"2. Проверьте файл requirements.txt в папке с программой\n\n"
            f"Для консольной версии запустите:\n"
            f"python bybit_crypto_trader.py --console"
        )
        
        # Пытаемся запустить консольную версию
        try:
            from bybit_crypto_trader import console_mode
            console_mode()
        except ImportError:
            messagebox.showerror(
                "Критическая ошибка", 
                "Не удалось запустить ни GUI, ни консольную версию.\n"
                "Проверьте целостность файлов программы."
            )
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror(
            "Ошибка выполнения",
            f"Произошла непредвиденная ошибка:\n\n{str(e)}\n\n"
            f"Обратитесь к разработчику для решения проблемы."
        )

if __name__ == "__main__":
    main()