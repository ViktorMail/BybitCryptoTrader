"""Основная логика крипто-торгового бота"""

import time
from typing import Dict, List, Optional, Any

# Безопасный импорт логирования с fallback
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

from config import settings
from bybit_client import ByBitClient
from exchange_manager import ExchangeManager
from user_interface import UserInterface

class CryptoTradingBot:
    """Основной класс крипто-торгового бота"""
    
    def __init__(self):
        """Инициализация бота"""
        self.bybit_client = None
        self.exchange_manager = None
        self.ui = UserInterface()
        self.is_running = False
        self.selected_crypto = None
        self.trading_amount = settings.default_trading_amount
    
    def initialize(self) -> bool:
        """Инициализация всех компонентов бота"""
        try:
            logger.info("Initializing Crypto Trading Bot...")
            
            # Инициализация ByBit клиента
            self.bybit_client = ByBitClient()
            logger.info("ByBit client initialized")
            
            # Инициализация менеджера бирж
            self.exchange_manager = ExchangeManager()
            logger.info("Exchange manager initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"Bot initialization failed: {e}")
            return False
    
    def get_available_cryptocurrencies(self) -> List[Dict]:
        """Получение списка доступных криптовалют"""
        try:
            if not self.bybit_client:
                self.initialize()
            
            return self.bybit_client.get_available_cryptocurrencies()
            
        except Exception as e:
            logger.error(f"Error getting cryptocurrencies: {e}")
            return []
    
    def select_cryptocurrency(self) -> Optional[str]:
        """Выбор криптовалюты для торговли"""
        try:
            cryptocurrencies = self.get_available_cryptocurrencies()
            
            if not cryptocurrencies:
                logger.error("No cryptocurrencies available")
                return None
            
            # Используем UI для выбора
            selected = self.ui.select_cryptocurrency(cryptocurrencies)
            
            if selected:
                self.selected_crypto = selected
                logger.info(f"Selected cryptocurrency: {selected}")
            
            return selected
            
        except Exception as e:
            logger.error(f"Error selecting cryptocurrency: {e}")
            return None
    
    def execute_trading_cycle(self) -> Dict[str, Any]:
        """Выполнение полного цикла торговли: покупка -> обмен -> продажа"""
        try:
            if not self.selected_crypto:
                raise ValueError("No cryptocurrency selected")
            
            logger.info(f"Starting trading cycle for {self.selected_crypto}")
            
            # Шаг 1: Покупка на ByBit
            logger.info("Step 1: Buying on ByBit...")
            buy_order = self.bybit_client.buy_cryptocurrency(
                self.selected_crypto, 
                self.trading_amount
            )
            
            if not buy_order or buy_order.get('status') != 'closed':
                raise Exception("Buy order failed")
            
            # Получаем количество купленной криптовалюты
            bought_amount = buy_order.get('filled', 0)
            
            logger.info(f"Bought {bought_amount} {self.selected_crypto}")
            
            # Шаг 2: Поиск лучшего курса на других биржах
            logger.info("Step 2: Finding best exchange rate...")
            best_rate = self.exchange_manager.find_best_rate(self.selected_crypto, 'sell')
            
            if not best_rate:
                logger.warning("No better rates found on other exchanges")
                # Продаем обратно на ByBit
                return self.sell_back_on_bybit(bought_amount)
            
            exchange_name, sell_price = best_rate
            bybit_price = self.bybit_client.get_current_price(self.selected_crypto)
            
            profit_margin = (sell_price - bybit_price) / bybit_price
            
            if profit_margin < settings.max_slippage:
                logger.info(f"Profit margin too low: {profit_margin:.4f}")
                return self.sell_back_on_bybit(bought_amount)
            
            # Шаг 3: Перевод и продажа на лучшей бирже
            logger.info(f"Step 3: Transferring to {exchange_name} and selling...")
            
            # В реальной реализации здесь был бы перевод между биржами
            # Для демонстрации продаем обратно на ByBit
            final_result = self.sell_back_on_bybit(bought_amount)
            
            final_result['attempted_arbitrage'] = True
            final_result['best_external_rate'] = {
                'exchange': exchange_name,
                'price': sell_price,
                'profit_margin': profit_margin
            }
            
            return final_result
            
        except Exception as e:
            logger.error(f"Trading cycle failed: {e}")
            # В случае ошибки пытаемся продать то что купили
            try:
                balance = self.bybit_client.get_balance()
                available = balance.get('free', {}).get(self.selected_crypto.split('/')[0], 0)
                if available > 0:
                    return self.sell_back_on_bybit(available)
            except:
                pass
            
            raise
    
    def sell_back_on_bybit(self, amount: float) -> Dict[str, Any]:
        """Продажа обратно на ByBit"""
        try:
            logger.info(f"Selling back {amount} on ByBit...")
            
            sell_order = self.bybit_client.sell_cryptocurrency(self.selected_crypto, amount)
            
            if not sell_order or sell_order.get('status') != 'closed':
                raise Exception("Sell order failed")
            
            result = {
                'status': 'completed',
                'type': 'bybit_roundtrip',
                'buy_order': None,  # Не сохраняем для краткости
                'sell_order': sell_order,
                'amount': amount
            }
            
            logger.info("Successfully sold back on ByBit")
            return result
            
        except Exception as e:
            logger.error(f"Failed to sell back on ByBit: {e}")
            raise
    
    def run_interactive_session(self):
        """Запуск интерактивной сессии"""
        try:
            logger.info("Starting interactive trading session...")
            
            if not self.initialize():
                logger.error("Bot initialization failed")
                return
            
            while True:
                try:
                    # Выбор криптовалюты
                    if not self.select_cryptocurrency():
                        logger.info("No cryptocurrency selected, exiting")
                        break
                    
                    # Подтверждение торговли
                    if not self.ui.confirm_trading(self.selected_crypto, self.trading_amount):
                        logger.info("Trading cancelled by user")
                        continue
                    
                    # Выполнение торговли
                    result = self.execute_trading_cycle()
                    
                    # Показ результатов
                    self.ui.show_trading_result(result)
                    
                    # Спрашиваем о продолжении
                    if not self.ui.confirm_continue():
                        logger.info("Trading session ended by user")
                        break
                        
                except KeyboardInterrupt:
                    logger.info("Trading session interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error in trading session: {e}")
                    if not self.ui.confirm_continue_after_error(str(e)):
                        break
            
            logger.info("Interactive session completed")
            
        except Exception as e:
            logger.error(f"Interactive session failed: {e}")
            raise
    
    def get_trading_statistics(self) -> Dict[str, Any]:
        """Получение статистики торговли"""
        try:
            stats = {
                'bybit_balance': self.bybit_client.get_balance() if self.bybit_client else {},
                'exchange_balances': self.exchange_manager.get_exchange_balances() if self.exchange_manager else {},
                'available_exchanges': self.exchange_manager.get_available_exchanges() if self.exchange_manager else [],
                'selected_crypto': self.selected_crypto,
                'trading_amount': self.trading_amount
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
