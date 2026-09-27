"""
Исправленный запускатель GUI для крипто-бота
Решает проблемы с ImportError и exe компиляцией
"""
import sys
import os
import traceback

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def is_exe_environment():
    """Определение запуска из exe файла"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def main():
    """Запуск GUI приложения"""
    try:
        # В exe среде все модули уже встроены, проверка файлов не нужна
        if not is_exe_environment():
            # Проверяем наличие необходимых файлов только для обычного Python
            required_files = [
                'main_gui.py', 'config.py', 'bybit_client.py', 
                'exchange_manager.py', 'crypto_trading_bot.py', 
                'user_interface.py'
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if missing_files:
                error_msg = (
                    f"Отсутствуют необходимые файлы:\n"
                    f"{', '.join(missing_files)}\n\n"
                    f"Убедитесь, что все файлы находятся в одной папке!"
                )
                
                # Показываем ошибку через tkinter
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Ошибка файлов", error_msg)
                root.destroy()
                return
        
        # Импортируем и запускаем GUI из нашего main_gui.py
        from main_gui import main
        main()
        
    except ImportError as e:
        # Если не удалось импортировать GUI модули
        error_msg = (
            f"Ошибка импорта модулей:\n{str(e)}\n\n"
            f"Решения:\n"
            f"1. Установите зависимости: pip install -r requirements.txt\n"
            f"2. Убедитесь, что файл main_gui.py существует\n"
            f"3. Проверьте, что все .py файлы в одной папке\n\n"
            f"Для консольной версии запустите:\n"
            f"python main_console_exe.py"
        )
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Ошибка импорта", error_msg)
            root.destroy()
            
            # Пытаемся запустить консольную версию как fallback
            try:
                print("Попытка запуска консольной версии...")
                from main_console_exe import main as console_main
                console_main()
            except ImportError:
                print("Консольная версия также недоступна")
                input("Нажмите Enter для выхода...")
                
        except Exception:
            print(error_msg)
            input("Нажмите Enter для выхода...")
            
    except Exception as e:
        # Непредвиденная ошибка
        error_msg = (
            f"Непредвиденная ошибка:\n{str(e)}\n\n"
            f"Полная информация об ошибке:\n"
            f"{traceback.format_exc()}\n\n"
            f"Обратитесь к разработчику для решения проблемы."
        )
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Критическая ошибка", error_msg)
            root.destroy()
        except Exception:
            print(error_msg)
            input("Нажмите Enter для выхода...")

# Функция main() уже определена в main_gui.py - не нужно дублировать

if __name__ == "__main__":
    main()
