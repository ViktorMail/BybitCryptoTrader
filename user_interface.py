"""Пользовательский интерфейс для крипто-бота"""

from typing import List, Dict, Optional, Any

# Безопасный импорт логирования с fallback
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

class UserInterface:
    """Класс для взаимодействия с пользователем"""
    
    def __init__(self):
        """Инициализация интерфейса"""
        pass
    
    def safe_input(self, prompt: str) -> Optional[str]:
        """Безопасный ввод с обработкой ошибок"""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return None
        except Exception:
            # Fallback для exe файлов
            try:
                import tkinter as tk
                from tkinter import simpledialog
                
                root = tk.Tk()
                root.withdraw()
                result = simpledialog.askstring("Ввод", prompt)
                root.destroy()
                
                return result if result else None
            except:
                return None
    
    def display_cryptocurrencies(self, cryptocurrencies: List[Dict]) -> None:
        """Отображение списка криптовалют"""
        print("\n" + "="*80)
        print("🪙 ДОСТУПНЫЕ КРИПТОВАЛЮТЫ")
        print("="*80)
        print(f"{'#':<3} {'Символ':<15} {'Цена':<15} {'Изменение %':<15} {'Объем':<15}")
        print("-"*80)
        
        for i, crypto in enumerate(cryptocurrencies[:20], 1):
            symbol = crypto.get('symbol', 'N/A')
            price = crypto.get('price', 0)
            change = crypto.get('change', 0)
            volume = crypto.get('volume', 0)
            
            price_str = f"${price:.4f}" if price else "N/A"
            change_str = f"{change:.2f}%" if change else "N/A"
            volume_str = f"${volume:,.0f}" if volume else "N/A"
            
            print(f"{i:<3} {symbol:<15} {price_str:<15} {change_str:<15} {volume_str:<15}")
        
        print("="*80)
    
    def select_cryptocurrency(self, cryptocurrencies: List[Dict]) -> Optional[str]:
        """Выбор криптовалюты пользователем"""
        try:
            if not cryptocurrencies:
                print("❌ Нет доступных криптовалют")
                return None
            
            self.display_cryptocurrencies(cryptocurrencies)
            
            while True:
                choice = self.safe_input("\n🎯 Выберите номер криптовалюты (1-20) или 'q' для выхода: ")
                
                if not choice:
                    return None
                
                if choice.lower() == 'q':
                    return None
                
                try:
                    index = int(choice) - 1
                    if 0 <= index < min(len(cryptocurrencies), 20):
                        selected = cryptocurrencies[index]
                        symbol = selected['symbol']
                        
                        print(f"\n✅ Выбрана криптовалюта: {symbol}")
                        print(f"💰 Текущая цена: ${selected.get('price', 'N/A')}")
                        print(f"📈 Изменение: {selected.get('change', 'N/A')}%")
                        
                        return symbol
                    else:
                        print("❌ Неверный номер. Попробуйте еще раз.")
                
                except ValueError:
                    print("❌ Введите число от 1 до 20 или 'q' для выхода")
            
        except Exception as e:
            logger.error(f"Error in cryptocurrency selection: {e}")
            return None
    
    def confirm_trading(self, symbol: str, amount: float) -> bool:
        """Подтверждение начала торговли"""
        try:
            print("\n" + "="*60)
            print("⚠️  ПОДТВЕРЖДЕНИЕ ТОРГОВЛИ")
            print("="*60)
            print(f"🪙 Криптовалюта: {symbol}")
            print(f"💵 Сумма торговли: ${amount:.2f}")
            print(f"🔄 Операция: Покупка -> Поиск лучшего курса -> Продажа")
            print("="*60)
            
            while True:
                confirm = self.safe_input("\n✅ Начать торговлю? (y/n): ")
                
                if not confirm:
                    return False
                
                if confirm.lower() in ['y', 'yes', 'д', 'да']:
                    return True
                elif confirm.lower() in ['n', 'no', 'н', 'нет']:
                    return False
                else:
                    print("❌ Введите 'y' (да) или 'n' (нет)")
        
        except Exception as e:
            logger.error(f"Error in trading confirmation: {e}")
            return False
    
    def show_trading_result(self, result: Dict[str, Any]) -> None:
        """Отображение результатов торговли"""
        try:
            print("\n" + "="*60)
            print("📊 РЕЗУЛЬТАТ ТОРГОВЛИ")
            print("="*60)
            
            status = result.get('status', 'unknown')
            
            if status == 'completed':
                print("✅ Торговля завершена успешно!")
                
                if result.get('type') == 'bybit_roundtrip':
                    print("🔄 Тип: Покупка и продажа на ByBit")
                
                if result.get('attempted_arbitrage'):
                    print("🔍 Попытка арбитража выполнена")
                    best_rate = result.get('best_external_rate', {})
                    if best_rate:
                        print(f"📈 Лучший внешний курс: {best_rate.get('exchange', 'N/A')}")
                        print(f"💹 Потенциальная прибыль: {best_rate.get('profit_margin', 0):.4f}%")
                
                amount = result.get('amount', 0)
                print(f"💰 Торговое количество: {amount:.6f}")
                
            elif status == 'skipped':
                print("⏭️  Торговля пропущена")
                reason = result.get('reason', 'unknown')
                if reason == 'low_profit':
                    margin = result.get('profit_margin', 0)
                    print(f"📉 Причина: Низкая маржа прибыли ({margin:.4f}%)")
            
            else:
                print("❌ Торговля завершилась с ошибкой")
                print(f"🔍 Статус: {status}")
            
            print("="*60)
            
        except Exception as e:
            logger.error(f"Error showing trading result: {e}")
            print("❌ Ошибка отображения результатов")
    
    def confirm_continue(self) -> bool:
        """Подтверждение продолжения торговли"""
        try:
            while True:
                choice = self.safe_input("\n🔄 Продолжить торговлю? (y/n): ")
                
                if not choice:
                    return False
                
                if choice.lower() in ['y', 'yes', 'д', 'да']:
                    return True
                elif choice.lower() in ['n', 'no', 'н', 'нет']:
                    return False
                else:
                    print("❌ Введите 'y' (да) или 'n' (нет)")
        
        except Exception as e:
            logger.error(f"Error in continue confirmation: {e}")
            return False
    
    def confirm_continue_after_error(self, error_message: str) -> bool:
        """Подтверждение продолжения после ошибки"""
        try:
            print(f"\n❌ Произошла ошибка: {error_message}")
            
            while True:
                choice = self.safe_input("\n🔄 Попробовать еще раз? (y/n): ")
                
                if not choice:
                    return False
                
                if choice.lower() in ['y', 'yes', 'д', 'да']:
                    return True
                elif choice.lower() in ['n', 'no', 'н', 'нет']:
                    return False
                else:
                    print("❌ Введите 'y' (да) или 'n' (нет)")
        
        except Exception as e:
            logger.error(f"Error in error confirmation: {e}")
            return False
    
    def show_welcome_message(self) -> None:
        """Показать приветственное сообщение"""
        print("\n" + "="*80)
        print("🤖 ДОБРО ПОЖАЛОВАТЬ В CRYPTO TRADING BOT")
        print("="*80)
        print("🎯 Функции бота:")
        print("   • 🪙 Просмотр доступных криптовалют на ByBit")
        print("   • 🛒 Автоматическая покупка выбранной криптовалюты")
        print("   • 🔍 Поиск лучших курсов на внешних биржах")
        print("   • 💱 Автоматический обмен для максимизации прибыли")
        print("   • 💰 Продажа обратно на ByBit")
        print("="*80)
        print("⚠️  Убедитесь что ваши API ключи настроены в файле .env")
        print("="*80)
    
    def show_goodbye_message(self) -> None:
        """Показать прощальное сообщение"""
        print("\n" + "="*60)
        print("👋 СПАСИБО ЗА ИСПОЛЬЗОВАНИЕ CRYPTO TRADING BOT!")
        print("="*60)
        print("🚀 Удачных торгов!")
        print("="*60)
