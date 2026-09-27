"""Основной класс крипто-бота для автоматизации торговли"""

import time
from typing import Dict, Any, Optional
from loguru import logger

from bybit_client import ByBitClient
from exchange_manager import ExchangeManager
from user_interface import UserInterface
from config import settings


class CryptoTradingBot:
    """Основной класс для автоматизации крипто-торговли"""
    
    def __init__(self):
        """Инициализация бота"""
        self.bybit_client = None
        self.exchange_manager = ExchangeManager()
        self.ui = UserInterface()
        self.trading_session = {}
        
        # Настройка логирования
        logger.add(
            "crypto_bot.log",
            rotation="1 day",
            retention="7 days",
            level=settings.log_level
        )
        
    def initialize(self) -> bool:
        """
        Инициализация всех компонентов бота
        
        Returns:
            True если инициализация успешна
        """
        try:
            logger.info("🚀 Запуск крипто-бота...")
            
            # Инициализация ByBit клиента
            try:
                self.bybit_client = ByBitClient()
                logger.info("✅ ByBit клиент инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации ByBit: {e}")
                logger.error("⚠️ Проверьте настройки API ключей в .env файле")
                return False
            
            logger.info("🎯 Крипто-бот готов к работе!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка инициализации: {e}")
            return False
    
    def run_interactive_session(self) -> None:
        """Запуск интерактивной сессии торговли"""
        try:
            print("\\n" + "="*80)
            print("🤖 КРИПТО-БОТ ДЛЯ АВТОМАТИЗАЦИИ ТОРГОВЛИ")
            print("="*80)
            print("Функционал:")
            print("• Просмотр криптовалют на ByBit")
            print("• Покупка выбранной криптовалюты")
            print("• Обмен через различные биржи")
            print("• Продажа обмененной криптовалюты")
            print("="*80)
            
            if not self.initialize():
                print("❌ Ошибка инициализации. Проверьте настройки.")
                return
            
            # Основной цикл интерактивной торговли
            while True:
                try:
                    success = self._execute_trading_workflow()
                    
                    if not success:
                        break
                        
                    # Спросить пользователя о продолжении
                    continue_trading = input("\\nХотите выполнить еще одну операцию? (y/n): ").strip().lower()
                    if continue_trading not in ['y', 'yes', 'д', 'да']:
                        break
                        
                except KeyboardInterrupt:
                    print("\\n👋 Сессия завершена пользователем")
                    break
                except Exception as e:
                    logger.error(f"❌ Ошибка в торговой сессии: {e}")
                    print(f"❌ Ошибка: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Критическая ошибка сессии: {e}")
            print(f"❌ Критическая ошибка: {e}")
    
    def _execute_trading_workflow(self) -> bool:
        """
        Выполнить полный цикл торговли: покупка -> обмен -> продажа
        
        Returns:
            True если операция успешна
        """
        try:
            # Шаг 1: Получение списка доступных криптовалют
            logger.info("📊 Получение списка криптовалют с ByBit...")
            print("\\n🔄 Загрузка данных с ByBit...")
            
            cryptocurrencies = self.bybit_client.get_available_cryptocurrencies()
            
            # Шаг 2: Выбор криптовалюты пользователем
            selected_crypto = self.ui.select_cryptocurrency(cryptocurrencies)
            if not selected_crypto:
                return False
            
            # Шаг 3: Выбор суммы для торговли
            trading_amount = self.ui.get_trading_amount(settings.default_trading_amount)
            if not trading_amount:
                return False
            
            # Сохранение данных сессии
            self.trading_session = {
                'selected_crypto': selected_crypto,
                'trading_amount': trading_amount,
                'start_time': time.time()
            }
            
            # Шаг 4: Покупка криптовалюты на ByBit
            logger.info(f"💰 Покупка {selected_crypto['base_currency']} за ${trading_amount}...")
            
            buy_order = self._buy_cryptocurrency(
                selected_crypto['symbol'], 
                trading_amount
            )
            
            if not buy_order:
                return False
            
            self.trading_session['buy_order'] = buy_order
            
            # Шаг 5: Выбор целевой криптовалюты для обмена
            target_crypto = self.ui.get_target_cryptocurrency()
            if not target_crypto:
                return False
            
            self.trading_session['target_crypto'] = target_crypto
            
            # Шаг 6: Выбор обменника
            exchanges = self.exchange_manager.get_available_exchanges()
            selected_exchange = self.ui.select_exchange(exchanges)
            if not selected_exchange:
                return False
            
            self.trading_session['selected_exchange'] = selected_exchange
            
            # Шаг 7: Выполнение обмена
            exchange_result = self._perform_exchange(
                selected_crypto['base_currency'],
                target_crypto,
                selected_exchange
            )
            
            if not exchange_result:
                return False
            
            self.trading_session['exchange_result'] = exchange_result
            
            # Шаг 8: Продажа обмененной криптовалюты на ByBit
            final_result = self._sell_cryptocurrency(
                target_crypto,
                exchange_result.get('final_amount', 0)
            )
            
            if final_result:
                self.trading_session['sell_order'] = final_result
                self._display_session_summary()
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка в рабочем процессе: {e}")
            return False
    
    def _buy_cryptocurrency(self, symbol: str, amount_usdt: float) -> Optional[Dict[str, Any]]:
        """Купить криптовалюту на ByBit"""
        try:
            operation_details = {
                "Операция": "Покупка на ByBit",
                "Символ": symbol,
                "Сумма": f"${amount_usdt:.2f}",
                "Биржа": "ByBit"
            }
            
            if not self.ui.confirm_operation(operation_details):
                logger.info("❌ Операция покупки отменена пользователем")
                return None
            
            logger.info(f"🔄 Выполняется покупка {symbol} за ${amount_usdt}...")
            order = self.bybit_client.buy_cryptocurrency(symbol, amount_usdt)
            
            logger.info("✅ Покупка выполнена успешно")
            return order
            
        except Exception as e:
            logger.error(f"❌ Ошибка покупки: {e}")
            print(f"❌ Ошибка покупки: {e}")
            return None
    
    def _perform_exchange(self, from_currency: str, to_currency: str, exchange_name: str) -> Optional[Dict[str, Any]]:
        """Выполнить обмен криптовалют на выбранной бирже"""
        try:
            # Получение текущего баланса
            balance = self.bybit_client.get_account_balance()
            available_amount = balance.get(from_currency, {}).get('free', 0)
            
            if available_amount == 0:
                logger.error(f"❌ Нет доступного баланса {from_currency} для обмена")
                return None
            
            # Получение лучшего курса обмена
            logger.info(f"🔍 Поиск лучшего курса {from_currency}/{to_currency}...")
            best_rate = self.exchange_manager.find_best_exchange_rate(from_currency, to_currency)
            
            if best_rate:
                print(f"\\n💱 Лучший курс найден на {best_rate['exchange']}: {best_rate['rate']:.8f}")
            
            operation_details = {
                "Операция": "Обмен криптовалют",
                "Из валюты": from_currency,
                "В валюту": to_currency,
                "Количество": f"{available_amount:.8f} {from_currency}",
                "Биржа": exchange_name,
                "Примерный курс": f"{best_rate['rate']:.8f}" if best_rate else "Определяется рынком"
            }
            
            if not self.ui.confirm_operation(operation_details):
                logger.info("❌ Операция обмена отменена пользователем")
                return None
            
            logger.info(f"🔄 Выполняется обмен {from_currency} -> {to_currency} на {exchange_name}...")
            
            # Выполнение обмена
            exchange_result = self.exchange_manager.execute_exchange(
                exchange_name, 
                from_currency, 
                to_currency, 
                available_amount
            )
            
            logger.info("✅ Обмен выполнен успешно")
            return exchange_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обмена: {e}")
            print(f"❌ Ошибка обмена: {e}")
            return None
    
    def _sell_cryptocurrency(self, currency: str, amount: float) -> Optional[Dict[str, Any]]:
        """Продать криптовалюту на ByBit"""
        try:
            symbol = f"{currency}/USDT"
            
            operation_details = {
                "Операция": "Продажа на ByBit",
                "Символ": symbol,
                "Количество": f"{amount:.8f} {currency}",
                "Биржа": "ByBit"
            }
            
            if not self.ui.confirm_operation(operation_details):
                logger.info("❌ Операция продажи отменена пользователем")
                return None
            
            logger.info(f"🔄 Выполняется продажа {amount:.8f} {currency}...")
            order = self.bybit_client.sell_cryptocurrency(symbol, amount)
            
            logger.info("✅ Продажа выполнена успешно")
            return order
            
        except Exception as e:
            logger.error(f"❌ Ошибка продажи: {e}")
            print(f"❌ Ошибка продажи: {e}")
            return None
    
    def _display_session_summary(self) -> None:
        """Отобразить сводку торговой сессии"""
        try:
            session = self.trading_session
            duration = time.time() - session.get('start_time', 0)
            
            summary = {
                "Время операции": f"{duration:.1f} секунд",
                "Изначальная криптовалюта": session['selected_crypto']['base_currency'],
                "Целевая криптовалюта": session['target_crypto'],
                "Сумма торговли": f"${session['trading_amount']:.2f}",
                "Использованный обменник": session['selected_exchange'].upper(),
                "ID заказа покупки": session.get('buy_order', {}).get('id', 'N/A'),
                "ID заказа продажи": session.get('sell_order', {}).get('id', 'N/A')
            }
            
            self.ui.display_operation_result(summary, True)
            
            logger.info("📊 Торговая сессия завершена успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отображения сводки: {e}")