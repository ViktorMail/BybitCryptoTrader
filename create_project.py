"""
Автоматический генератор проекта Bybit Crypto Trader
Запустите этот файл и он создаст все необходимые файлы проекта
"""
import os

def create_file(filename, content):
    """Создать файл с содержимым"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Создан файл: {filename}")

def main():
    print("🚀 Создание проекта Bybit Crypto Trader...")
    print("=" * 50)
    
    # Создаем папку проекта
    project_name = "BybitCryptoTrader"
    if not os.path.exists(project_name):
        os.makedirs(project_name)
        print(f"📁 Создана папка: {project_name}")
    
    os.chdir(project_name)
    
    # 1. requirements.txt
    requirements = """pybit>=5.6.0
python-dotenv>=1.0.0
requests>=2.31.0
schedule>=1.2.0
colorama>=0.4.6
tkinter
Pillow>=10.0.0
matplotlib>=3.7.0
pandas>=2.0.0
ttkbootstrap>=1.10.0"""
    create_file("requirements.txt", requirements)
    
    # 2. .env.example
    env_example = """# Bybit API Configuration
# Скопируйте этот файл в .env и заполните своими данными

# API ключи Bybit (получите на bybit.com в разделе API Management)
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here

# Режим работы (True для тестовой сети, False для основной)
BYBIT_TESTNET=True

# Интервал мониторинга в секундах
MONITOR_INTERVAL=60"""
    create_file(".env.example", env_example)
    
    # 3. .gitignore
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.bak"""
    create_file(".gitignore", gitignore)
    
    # 4. start_trader.bat
    bat_content = """@echo off
echo ========================================
echo  🚀 Bybit Crypto Trader - GUI запуск
echo ========================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo    Установите Python с python.org
    pause
    exit /b 1
)

echo ✅ Python найден
echo 🔄 Запуск Bybit Crypto Trader...
echo.

REM Запускаем GUI версию
python run_trader_gui.py

echo.
echo 👋 Программа завершена
pause"""
    create_file("start_trader.bat", bat_content)
    
    # 5. run_trader_gui.py
    run_gui = '''"""
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
            f"Не удалось запустить GUI интерфейс.\\n\\n"
            f"Ошибка: {str(e)}\\n\\n"
            f"Решение:\\n"
            f"1. Установите зависимости: pip install -r requirements.txt\\n"
            f"2. Проверьте файл requirements.txt в папке с программой\\n\\n"
            f"Для консольной версии запустите:\\n"
            f"python bybit_crypto_trader.py --console"
        )
        
        # Пытаемся запустить консольную версию
        try:
            from bybit_crypto_trader import console_mode
            console_mode()
        except ImportError:
            messagebox.showerror(
                "Критическая ошибка", 
                "Не удалось запустить ни GUI, ни консольную версию.\\n"
                "Проверьте целостность файлов программы."
            )
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror(
            "Ошибка выполнения",
            f"Произошла непредвиденная ошибка:\\n\\n{str(e)}\\n\\n"
            f"Обратитесь к разработчику для решения проблемы."
        )

if __name__ == "__main__":
    main()'''
    create_file("run_trader_gui.py", run_gui)
    
    print(f"\n🎉 Проект создан в папке: {os.path.abspath('.')}")
    print("\n📋 Следующие шаги:")
    print("1. Запустите: create_remaining_files.py для создания основных модулей")
    print("2. Установите зависимости: pip install -r requirements.txt")
    print("3. Настройте API ключи в файле .env")
    print("4. Запустите: python run_trader_gui.py")

if __name__ == "__main__":
    main()
