"""
Скрипт для компиляции крипто-бота в exe файл
"""

import subprocess
import sys
import os
from pathlib import Path

def find_pyinstaller():
    """Поиск PyInstaller с fallback для разных установок Python"""
    import shutil
    
    # Способ 1: Проверяем стандартный pyinstaller в PATH
    if shutil.which("pyinstaller"):
        return ["pyinstaller"]
    
    # Способ 2: Через python -m PyInstaller (работает для Windows Store Python)
    try:
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ PyInstaller найден через python -m: {result.stdout.strip()}")
            return [sys.executable, "-m", "PyInstaller"]
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Способ 3: Прямой поиск в Scripts папке Python
    python_path = Path(sys.executable).parent
    possible_paths = [
        python_path / "Scripts" / "pyinstaller.exe",
        python_path / "pyinstaller.exe",
        python_path.parent / "Scripts" / "pyinstaller.exe"
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"✅ PyInstaller найден: {path}")
            return [str(path)]
    
    return None

def install_pyinstaller():
    """Установка PyInstaller если не установлен"""
    try:
        import PyInstaller
        print("✅ PyInstaller уже установлен")
        return True
    except ImportError:
        print("📦 Установка PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                                timeout=120)
            print("✅ PyInstaller установлен")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"❌ Ошибка установки PyInstaller: {e}")
            print("Попробуйте установить вручную:")
            print("pip install pyinstaller")
            print("Или:")
            print("python -m pip install pyinstaller")
            return False

def build_console_version():
    """Компиляция консольной версии"""
    print("🔨 Компиляция консольной версии...")
    
    # Находим PyInstaller
    pyinstaller_cmd = find_pyinstaller()
    if not pyinstaller_cmd:
        print("❌ PyInstaller не найден!")
        print("Установите PyInstaller:")
        print("pip install pyinstaller")
        print("Или попробуйте:")
        print("python -m pip install pyinstaller")
        return False
        
    cmd = pyinstaller_cmd + [
        "--onefile",
        "--console", 
        "--name=crypto_bot_console",
        "--add-data=.env.example;.",
        "--hidden-import=ccxt",
        "--hidden-import=loguru",
        "--hidden-import=pydantic",
        "--hidden-import=pydantic-settings", 
        "--hidden-import=requests",
        "main_console_exe.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Консольная версия создана: dist/crypto_bot_console.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка компиляции: {e}")
        return False

def build_gui_version():
    """Компиляция GUI версии"""
    print("🔨 Компиляция GUI версии...")
    
    # Находим PyInstaller
    pyinstaller_cmd = find_pyinstaller()
    if not pyinstaller_cmd:
        print("❌ PyInstaller не найден!")
        return False
    
    gui_file = "run_trader_gui_fixed.py" if os.path.exists("run_trader_gui_fixed.py") else "main_gui.py"
    
    cmd = pyinstaller_cmd + [
        "--onefile",
        "--windowed",
        "--name=crypto_bot_gui", 
        "--add-data=.env.example;.",
        "--hidden-import=ccxt",
        "--hidden-import=loguru",
        "--hidden-import=pydantic",
        "--hidden-import=pydantic-settings",
        "--hidden-import=requests",
        "--hidden-import=tkinter",
        gui_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ GUI версия создана: dist/crypto_bot_gui.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка компиляции: {e}")
        return False

def main():
    """Основная функция сборки"""
    print("🚀 Компиляция крипто-бота...")
    
    install_pyinstaller()
    
    console_ok = build_console_version()
    gui_ok = build_gui_version()
    
    if console_ok or gui_ok:
        print("\n🎉 Компиляция завершена!")
        if console_ok:
            print("✅ Консольная версия готова")
        if gui_ok:
            print("✅ GUI версия готова")
    else:
        print("❌ Компиляция не удалась")
    
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
