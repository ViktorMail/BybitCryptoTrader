@echo off
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
pause