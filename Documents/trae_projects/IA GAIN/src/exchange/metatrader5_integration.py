"""
MetaTrader 5 Integration Module
Provides complete integration with MetaTrader 5 platform for forex and CFD trading
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    BUY = mt5.ORDER_TYPE_BUY
    SELL = mt5.ORDER_TYPE_SELL
    BUY_LIMIT = mt5.ORDER_TYPE_BUY_LIMIT
    SELL_LIMIT = mt5.ORDER_TYPE_SELL_LIMIT
    BUY_STOP = mt5.ORDER_TYPE_BUY_STOP
    SELL_STOP = mt5.ORDER_TYPE_SELL_STOP

class OrderState(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class TradeSignal:
    symbol: str
    order_type: OrderType
    volume: float
    price: float
    sl: float
    tp: float
    comment: str = "IA GAIN"
    magic: int = 123456

@dataclass
class Position:
    ticket: int
    symbol: str
    type: OrderType
    volume: float
    price_open: float
    price_current: float
    sl: float
    tp: float
    profit: float
    comment: str
    magic: int

@dataclass
class AccountInfo:
    login: int
    balance: float
    equity: float
    margin: float
    free_margin: float
    leverage: int
    profit: float
    company: str
    name: str
    server: str

class MetaTrader5Integration:
    """
    Complete MetaTrader 5 integration with advanced features
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connected = False
        self.account_info = None
        self.positions_cache = {}
        self.symbols_info = {}
        
    def connect(self) -> bool:
        """
        Connect to MetaTrader 5 terminal
        """
        try:
            # Initialize MT5 connection
            if not mt5.initialize(
                login=self.config.get('login'),
                password=self.config.get('password'),
                server=self.config.get('server'),
                path=self.config.get('path', '')
            ):
                logger.error(f"Failed to initialize MT5: {mt5.last_error()}")
                return False
            
            # Check connection
            if not mt5.terminal_info():
                logger.error("Failed to get terminal info")
                return False
            
            self.connected = True
            logger.info("Successfully connected to MetaTrader 5")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from MetaTrader 5
        """
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MetaTrader 5")
    
    def get_account_info(self) -> Optional[AccountInfo]:
        """
        Get account information
        """
        if not self.connected:
            return None
            
        try:
            account = mt5.account_info()
            if account:
                self.account_info = AccountInfo(
                    login=account.login,
                    balance=account.balance,
                    equity=account.equity,
                    margin=account.margin,
                    free_margin=account.margin_free,
                    leverage=account.leverage,
                    profit=account.profit,
                    company=account.company,
                    name=account.name,
                    server=account.server
                )
                return self.account_info
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
        
        return None
    
    def get_symbols(self, refresh: bool = False) -> List[str]:
        """
        Get available trading symbols
        """
        if not self.connected:
            return []
            
        try:
            if refresh or not self.symbols_info:
                symbols = mt5.symbols_get()
                if symbols:
                    self.symbols_info = {s.name: s for s in symbols}
                    return [s.name for s in symbols]
            else:
                return list(self.symbols_info.keys())
                
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
        
        return []
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed symbol information
        """
        if not self.connected:
            return None
            
        try:
            if symbol not in self.symbols_info:
                self.symbols_info[symbol] = mt5.symbol_info(symbol)
            
            symbol_info = self.symbols_info.get(symbol)
            if symbol_info:
                return {
                    'name': symbol_info.name,
                    'description': symbol_info.description,
                    'point': symbol_info.point,
                    'digits': symbol_info.digits,
                    'spread': symbol_info.spread,
                    'trade_contract_size': symbol_info.trade_contract_size,
                    'trade_tick_value': symbol_info.trade_tick_value,
                    'trade_tick_size': symbol_info.trade_tick_size,
                    'volume_min': symbol_info.volume_min,
                    'volume_max': symbol_info.volume_max,
                    'volume_step': symbol_info.volume_step,
                    'swap_long': symbol_info.swap_long,
                    'swap_short': symbol_info.swap_short,
                    'swap_mode': symbol_info.swap_mode
                }
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
        
        return None
    
    def get_historical_data(self, symbol: str, timeframe: str = 'H1', 
                           start_date: datetime = None, end_date: datetime = None,
                           count: int = 1000) -> Optional[pd.DataFrame]:
        """
        Get historical price data
        """
        if not self.connected:
            return None
            
        try:
            # Map timeframe strings to MT5 constants
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1,
                'W1': mt5.TIMEFRAME_W1,
                'MN1': mt5.TIMEFRAME_MN1
            }
            
            tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            if start_date and end_date:
                rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
            else:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
            
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df.set_index('time', inplace=True)
                return df
                
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
        
        return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """
        Get current market price
        """
        if not self.connected:
            return None
            
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                return {
                    'bid': tick.bid,
                    'ask': tick.ask,
                    'last': tick.last,
                    'time': datetime.fromtimestamp(tick.time),
                    'spread': tick.ask - tick.bid
                }
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
        
        return None
    
    def get_positions(self, symbol: str = None) -> List[Position]:
        """
        Get open positions
        """
        if not self.connected:
            return []
            
        try:
            positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                position = Position(
                    ticket=pos.ticket,
                    symbol=pos.symbol,
                    type=OrderType(pos.type),
                    volume=pos.volume,
                    price_open=pos.price_open,
                    price_current=pos.price_current,
                    sl=pos.sl,
                    tp=pos.tp,
                    profit=pos.profit,
                    comment=pos.comment,
                    magic=pos.magic
                )
                result.append(position)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
        
        return []
    
    def calculate_lot_size(self, symbol: str, risk_percentage: float, 
                          stop_loss_pips: float, account_balance: float = None) -> float:
        """
        Calculate lot size based on risk management
        """
        if not self.connected:
            return 0.0
            
        try:
            if account_balance is None:
                account_info = self.get_account_info()
                if account_info:
                    account_balance = account_info.balance
                else:
                    return 0.0
            
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return 0.0
            
            # Calculate risk amount
            risk_amount = account_balance * (risk_percentage / 100)
            
            # Calculate pip value
            tick_value = symbol_info['trade_tick_value']
            pip_value = tick_value * symbol_info['trade_contract_size']
            
            # Calculate lot size
            lot_size = risk_amount / (stop_loss_pips * pip_value)
            
            # Round to volume step
            volume_step = symbol_info['volume_step']
            lot_size = round(lot_size / volume_step) * volume_step
            
            # Ensure within min/max limits
            volume_min = symbol_info['volume_min']
            volume_max = symbol_info['volume_max']
            lot_size = max(volume_min, min(lot_size, volume_max))
            
            return lot_size
            
        except Exception as e:
            logger.error(f"Error calculating lot size: {e}")
        
        return 0.0
    
    def send_order(self, signal: TradeSignal) -> Optional[int]:
        """
        Send trading order
        """
        if not self.connected:
            return None
            
        try:
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": signal.symbol,
                "volume": signal.volume,
                "type": signal.order_type.value,
                "price": signal.price,
                "sl": signal.sl,
                "tp": signal.tp,
                "deviation": 20,
                "magic": signal.magic,
                "comment": signal.comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Order successful: {result.order}")
                return result.order
            else:
                logger.error(f"Order failed: {result.retcode} - {result.comment}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending order: {e}")
        
        return None
    
    def send_pending_order(self, signal: TradeSignal, order_type: OrderType,
                          expiration: datetime = None) -> Optional[int]:
        """
        Send pending order (limit/stop)
        """
        if not self.connected:
            return None
            
        try:
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": signal.symbol,
                "volume": signal.volume,
                "type": order_type.value,
                "price": signal.price,
                "sl": signal.sl,
                "tp": signal.tp,
                "magic": signal.magic,
                "comment": signal.comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            if expiration:
                request["expiration"] = int(expiration.timestamp())
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Pending order successful: {result.order}")
                return result.order
            else:
                logger.error(f"Pending order failed: {result.retcode} - {result.comment}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending pending order: {e}")
        
        return None
    
    def close_position(self, ticket: int, volume: float = None, 
                      deviation: int = 20) -> bool:
        """
        Close specific position
        """
        if not self.connected:
            return False
            
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"Position {ticket} not found")
                return False
            
            position = position[0]
            
            # Determine close type (opposite of position type)
            close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": volume if volume else position.volume,
                "type": close_type,
                "position": ticket,
                "price": mt5.symbol_info_tick(position.symbol).ask if close_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).bid,
                "deviation": deviation,
                "magic": position.magic,
                "comment": "IA GAIN Close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Position {ticket} closed successfully")
                return True
            else:
                logger.error(f"Failed to close position {ticket}: {result.retcode} - {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Error closing position {ticket}: {e}")
        
        return False
    
    def close_all_positions(self, symbol: str = None, magic: int = None) -> int:
        """
        Close all positions matching criteria
        """
        if not self.connected:
            return 0
            
        try:
            positions = self.get_positions(symbol)
            if magic is not None:
                positions = [p for p in positions if p.magic == magic]
            
            closed_count = 0
            for position in positions:
                if self.close_position(position.ticket):
                    closed_count += 1
            
            logger.info(f"Closed {closed_count} positions")
            return closed_count
            
        except Exception as e:
            logger.error(f"Error closing all positions: {e}")
        
        return 0
    
    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> bool:
        """
        Modify position stop loss and take profit
        """
        if not self.connected:
            return False
            
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"Position {ticket} not found")
                return False
            
            position = position[0]
            
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": ticket,
                "sl": sl if sl is not None else position.sl,
                "tp": tp if tp is not None else position.tp,
                "magic": position.magic,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Position {ticket} modified successfully")
                return True
            else:
                logger.error(f"Failed to modify position {ticket}: {result.retcode} - {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Error modifying position {ticket}: {e}")
        
        return False
    
    def get_order_history(self, days: int = 30) -> pd.DataFrame:
        """
        Get order history for specified number of days
        """
        if not self.connected:
            return pd.DataFrame()
            
        try:
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get history
            history = mt5.history_deals_get(start_date, end_date)
            if history is None:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(list(history), columns=history[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting order history: {e}")
        
        return pd.DataFrame()
    
    def get_market_depth(self, symbol: str) -> Optional[Dict]:
        """
        Get market depth (Level 2) data
        """
        if not self.connected:
            return None
            
        try:
            # Get market depth
            depth = mt5.market_book_get(symbol)
            if depth is None:
                return None
            
            # Convert to structured format
            bids = [{'price': item.price, 'volume': item.volume} for item in depth if item.type == mt5.BOOK_TYPE_BUY]
            asks = [{'price': item.price, 'volume': item.volume} for item in depth if item.type == mt5.BOOK_TYPE_SELL]
            
            return {
                'symbol': symbol,
                'bids': sorted(bids, key=lambda x: x['price'], reverse=True),
                'asks': sorted(asks, key=lambda x: x['price']),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting market depth for {symbol}: {e}")
        
        return None
    
    def calculate_margin_requirement(self, symbol: str, volume: float, 
                                   order_type: OrderType) -> Optional[float]:
        """
        Calculate margin requirement for a trade
        """
        if not self.connected:
            return None
            
        try:
            request = {
                "action": mt5.TRADE_ACTION_ORDER_CHECK,
                "symbol": symbol,
                "volume": volume,
                "type": order_type.value,
                "price": mt5.symbol_info_tick(symbol).ask if order_type in [OrderType.BUY, OrderType.BUY_LIMIT, OrderType.BUY_STOP] else mt5.symbol_info_tick(symbol).bid,
            }
            
            result = mt5.order_check(request)
            if result:
                return result.margin
            
        except Exception as e:
            logger.error(f"Error calculating margin for {symbol}: {e}")
        
        return None
    
    def get_trading_hours(self, symbol: str) -> Optional[Dict]:
        """
        Get trading hours for a symbol
        """
        if not self.connected:
            return None
            
        try:
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return None
            
            # Get session info
            session_info = mt5.symbol_info_session_quote(symbol)
            if session_info:
                return {
                    'symbol': symbol,
                    'sessions': [
                        {
                            'day': session.day,
                            'start_hour': session.start_hour,
                            'start_minutes': session.start_minutes,
                            'end_hour': session.end_hour,
                            'end_minutes': session.end_minutes
                        }
                        for session in session_info
                    ]
                }
            
        except Exception as e:
            logger.error(f"Error getting trading hours for {symbol}: {e}")
        
        return None
    
    def is_market_open(self, symbol: str) -> bool:
        """
        Check if market is open for trading
        """
        if not self.connected:
            return False
            
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                return symbol_info.visible and symbol_info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL
            
        except Exception as e:
            logger.error(f"Error checking market status for {symbol}: {e}")
        
        return False
    
    def get_spread_analysis(self, symbol: str, hours: int = 24) -> Optional[Dict]:
        """
        Analyze spread patterns over specified hours
        """
        if not self.connected:
            return None
            
        try:
            # Get historical ticks
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            ticks = mt5.copy_ticks_range(symbol, start_time, end_time, mt5.COPY_TICKS_ALL)
            if ticks is None or len(ticks) == 0:
                return None
            
            # Calculate spread statistics
            spreads = [(tick['ask'] - tick['bid']) / tick['bid'] * 10000 for tick in ticks]  # in pips
            
            return {
                'symbol': symbol,
                'current_spread': mt5.symbol_info_tick(symbol).ask - mt5.symbol_info_tick(symbol).bid,
                'avg_spread': np.mean(spreads),
                'min_spread': np.min(spreads),
                'max_spread': np.max(spreads),
                'std_spread': np.std(spreads),
                'spread_percentiles': {
                    '25th': np.percentile(spreads, 25),
                    '50th': np.percentile(spreads, 50),
                    '75th': np.percentile(spreads, 75),
                    '95th': np.percentile(spreads, 95)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spread for {symbol}: {e}")
        
        return None
    
    def get_economic_calendar(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get economic calendar events
        """
        # This would typically integrate with an economic calendar API
        # For now, return empty list as placeholder
        return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on connection and trading capabilities
        """
        health = {
            'connected': self.connected,
            'timestamp': datetime.now(),
            'status': 'healthy' if self.connected else 'disconnected'
        }
        
        if self.connected:
            try:
                # Check terminal info
                terminal_info = mt5.terminal_info()
                if terminal_info:
                    health['terminal_connected'] = terminal_info.connected
                    health['terminal_dlls_allowed'] = terminal_info.dlls_allowed
                
                # Check account info
                account_info = self.get_account_info()
                if account_info:
                    health['account_balance'] = account_info.balance
                    health['account_equity'] = account_info.equity
                    health['account_margin_level'] = (account_info.equity / account_info.margin * 100) if account_info.margin > 0 else 0
                
                # Check symbol availability
                symbols = self.get_symbols()
                health['available_symbols'] = len(symbols)
                
                # Check open positions
                positions = self.get_positions()
                health['open_positions'] = len(positions)
                
            except Exception as e:
                health['status'] = f'error: {str(e)}'
        
        return health

# Example usage and testing functions
def test_metatrader_connection():
    """
    Test MetaTrader 5 connection and basic functionality
    """
    config = {
        'login': 12345678,  # Replace with actual credentials
        'password': 'your_password',
        'server': 'YourBroker-Server',
        'path': 'C:\\Program Files\\MetaTrader 5\\terminal64.exe'
    }
    
    mt5_integration = MetaTrader5Integration(config)
    
    # Test connection
    if mt5_integration.connect():
        print("Connection successful!")
        
        # Get account info
        account_info = mt5_integration.get_account_info()
        if account_info:
            print(f"Account: {account_info.name} - Balance: ${account_info.balance:.2f}")
        
        # Get available symbols
        symbols = mt5_integration.get_symbols()
        print(f"Available symbols: {len(symbols)}")
        
        # Test EURUSD
        if 'EURUSD' in symbols:
            price = mt5_integration.get_current_price('EURUSD')
            if price:
                print(f"EURUSD - Bid: {price['bid']:.5f}, Ask: {price['ask']:.5f}")
        
        # Health check
        health = mt5_integration.health_check()
        print(f"Health status: {health['status']}")
        
    else:
        print("Connection failed!")
    
    mt5_integration.disconnect()

if __name__ == "__main__":
    test_metatrader_connection()