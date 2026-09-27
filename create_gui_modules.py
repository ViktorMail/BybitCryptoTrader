"""
Создание GUI модулей проекта
"""
import os

def create_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Создан файл: {filename}")

def main():
    print("🖥️ Создание GUI модулей...")
    
    # Переходим в папку проекта
    if os.path.exists("BybitCryptoTrader"):
        os.chdir("BybitCryptoTrader")
    
    # Сообщаем пользователю
    print("""
📋 Следующие шаги:
1. Скопируйте полное содержимое файлов из сообщения выше
2. Создайте файлы в Visual Studio:
   - bybit_crypto_trader.py (основной модуль)
   - config.py (конфигурация)
   - gui_main.py (GUI окно)
   - gui_dialogs.py (диалоги)
   - build_exe.py (компиляция)

3. Установите зависимости: pip install -r requirements.txt
4. Настройте .env файл с API ключами
5. Запустите: python run_trader_gui.py

🎉 Готово! Полнофункциональный крипто-трейдер с GUI!
    """)

if __name__ == "__main__":
    main()
