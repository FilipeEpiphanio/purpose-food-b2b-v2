import ccxt
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
import pandas as pd

@dataclass
class Trade:
    id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    amount: float
    price: float
    timestamp: datetime
    status: str  # 'open', 'closed', 'cancelled'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    fees: float = 0.0
    pnl: float = 0.0

@dataclass
class TradingSignal:
    symbol: str
    signal: str  # 'buy', 'sell', 'hold'
    confidence: float
    price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reasoning: str

class AutomatedTrading:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self.load_config(config_path)
        self.logger = self.setup_logger()
        self.exchanges = {}
        self.active_trades: Dict[str, Trade] = {}
        self.trade_history: List[Trade] = []
        self.daily_trades = 0
        self.last_trade_date = datetime.now().date()
        self.portfolio_value = 0.0
        self.initial_balance = 0.0
        
    def load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        return {
            "trading": {
                "max_position_size": 0.1,
                "stop_loss": 0.02,
                "take_profit": 0.05,
                "max_daily_trades": 10,
                "min_volume_threshold": 1000000,
                "trading_hours": "24/7",
                "exchanges": ["binance", "coinbase", "kraken"]
            },
            "risk": {
                "max_portfolio_risk": 0.05,
                "max_single_trade_risk": 0.02,
                "risk_reward_ratio": 2.0,
                "use_trailing_stop": True,
                "trailing_stop_distance": 0.03,
                "max_drawdown": 0.1
            },
            "api": {
                "binance": {
                    "api_key": "",
                    "api_secret": "",
                    "testnet": True
                },
                "coinbase": {
                    "api_key": "",
                    "api_secret": "",
                    "passphrase": ""
                },
                "kraken": {
                    "api_key": "",
                    "api_secret": ""
                }
            }
        }
    
    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('AutomatedTrading')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('iagain_trading.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize_exchanges(self):
        """Initialize exchange connections"""
        for exchange_name in self.config['trading']['exchanges']:
            try:
                exchange_config = self.config['api'].get(exchange_name, {})
                
                if exchange_name == 'binance':
                    exchange = ccxt.binance({
                        'apiKey': exchange_config.get('api_key', ''),
                        'secret': exchange_config.get('api_secret', ''),
                        'sandbox': exchange_config.get('testnet', True),
                        'enableRateLimit': True,
                    })
                elif exchange_name == 'coinbase':
                    exchange = ccxt.coinbasepro({
                        'apiKey': exchange_config.get('api_key', ''),
                        'secret': exchange_config.get('api_secret', ''),
                        'password': exchange_config.get('passphrase', ''),
                        'enableRateLimit': True,
                    })
                elif exchange_name == 'kraken':
                    exchange = ccxt.kraken({
                        'apiKey': exchange_config.get('api_key', ''),
                        'secret': exchange_config.get('api_secret', ''),
                        'enableRateLimit': True,
                    })
                else:
                    continue
                
                await exchange.load_markets()
                self.exchanges[exchange_name] = exchange
                self.logger.info(f"Initialized {exchange_name} exchange")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {exchange_name}: {str(e)}")
    
    def generate_trading_signals(self, market_data) -> List[TradingSignal]:
        """Generate trading signals based on technical analysis"""
        signals = []
        
        for data in market_data:
            try:
                signal = self.analyze_market_conditions(data)
                if signal['signal'] != 'hold':
                    rr = float(self.config['risk'].get('risk_reward_ratio', 2.0))
                    base_sl = float(self.config['risk'].get('max_single_trade_risk', 0.02))
                    conf = float(signal['confidence']) if signal['confidence'] else 0.0
                    sl_pct = max(0.005, base_sl * (0.75 + max(0.0, 1.0 - conf) * 0.5))
                    tp_pct = sl_pct * rr
                    signals.append(TradingSignal(
                        symbol=data.symbol,
                        signal=signal['signal'],
                        confidence=signal['confidence'],
                        price=data.close,
                        stop_loss=data.close * (1 - sl_pct) if signal['signal'] == 'buy' else data.close * (1 + sl_pct),
                        take_profit=data.close * (1 + tp_pct) if signal['signal'] == 'buy' else data.close * (1 - tp_pct),
                        position_size=self.calculate_position_size(data),
                        reasoning=signal['reasoning']
                    ))
            except Exception as e:
                self.logger.error(f"Error generating signal for {data.symbol}: {str(e)}")
        
        return signals
    
    def analyze_market_conditions(self, data) -> Dict:
        """Analyze market conditions and generate signals"""
        score = 0
        reasons = []
        
        # RSI Analysis
        if data.rsi:
            if data.rsi < 30:
                score += 2
                reasons.append("RSI oversold")
            elif data.rsi > 70:
                score -= 2
                reasons.append("RSI overbought")
        
        # MACD Analysis
        if data.macd and data.macd_signal:
            if data.macd > data.macd_signal:
                score += 1
                reasons.append("MACD bullish")
            else:
                score -= 1
                reasons.append("MACD bearish")
        
        # Bollinger Bands Analysis
        if data.bb_upper and data.bb_lower:
            if data.close < data.bb_lower:
                score += 1
                reasons.append("Price below lower BB")
            elif data.close > data.bb_upper:
                score -= 1
                reasons.append("Price above upper BB")
        
        # EMA Analysis
        if data.ema_9 and data.ema_21:
            if data.ema_9 > data.ema_21:
                score += 1
                reasons.append("EMA9 > EMA21")
            else:
                score -= 1
                reasons.append("EMA9 < EMA21")
        
        # Volume Analysis
        if data.volume > self.config['trading']['min_volume_threshold']:
            score += 0.5
            reasons.append("Sufficient volume")
        
        # Determine signal
        if score >= 3:
            signal = 'buy'
            confidence = min(0.9, 0.5 + score * 0.1)
        elif score <= -3:
            signal = 'sell'
            confidence = min(0.9, 0.5 + abs(score) * 0.1)
        else:
            signal = 'hold'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': "; ".join(reasons)
        }
    
    def calculate_position_size(self, data) -> float:
        """Calculate position size based on risk management"""
        # Simple position sizing based on available balance and risk
        max_position_size = self.config['trading']['max_position_size']
        
        # Adjust position size based on volatility (using ATR if available)
        # For now, use a simple percentage of available balance
        position_size = max_position_size * 0.8  # Conservative approach
        
        return position_size
    
    async def execute_trades(self, predictions: List[Dict]):
        """Execute trades based on AI predictions"""
        self.logger.info("Starting trade execution...")
        
        # Reset daily trades counter if it's a new day
        if datetime.now().date() != self.last_trade_date:
            self.daily_trades = 0
            self.last_trade_date = datetime.now().date()
        
        # Check daily trade limit
        if self.daily_trades >= self.config['trading']['max_daily_trades']:
            self.logger.warning("Daily trade limit reached")
            return
        
        # Generate trading signals from predictions
        signals = self.generate_trading_signals(predictions)
        
        # Filter signals by confidence
        high_confidence_signals = [
            signal for signal in signals 
            if signal.confidence >= 0.7
        ]
        
        self.logger.info(f"Generated {len(signals)} signals, {len(high_confidence_signals)} high confidence")
        
        # Execute trades for high confidence signals
        for signal in high_confidence_signals:
            if 'system' in self.config and len(self.active_trades) >= int(self.config['system'].get('max_concurrent_trades', 5)):
                self.logger.warning("Max concurrent trades limit reached")
                break
            if self.daily_trades >= self.config['trading']['max_daily_trades']:
                break
            
            try:
                await self.execute_single_trade(signal)
                self.daily_trades += 1
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error executing trade for {signal.symbol}: {str(e)}")
                continue
    
    async def execute_single_trade(self, signal: TradingSignal):
        """Execute a single trade"""
        try:
            # Select best exchange for this symbol
            exchange = self.select_best_exchange(signal.symbol)
            if not exchange:
                self.logger.error(f"No exchange available for {signal.symbol}")
                return
            
            # Get current balance
            balance = await exchange.fetch_balance()
            available_balance = balance['free']['USDT'] if 'USDT' in balance['free'] else 0
            
            if available_balance < 10:  # Minimum balance check
                self.logger.error("Insufficient balance")
                return
            
            # Calculate trade amount
            trade_amount = min(
                signal.position_size * available_balance,
                available_balance * 0.95  # Keep 5% buffer
            )
            
            if trade_amount < 10:  # Minimum trade size
                self.logger.warning(f"Trade amount too small: {trade_amount}")
                return
            
            # Create order
            order_type = 'market'  # Use market orders for now
            side = signal.signal
            
            self.logger.info(f"Creating {side} order for {signal.symbol}: {trade_amount} @ {signal.price}")
            
            order = await exchange.create_order(
                symbol=signal.symbol,
                type=order_type,
                side=side,
                amount=trade_amount / signal.price,  # Convert USD to coin amount
                price=signal.price
            )
            
            # Create trade object
            trade = Trade(
                id=order['id'],
                symbol=signal.symbol,
                side=side,
                amount=order['amount'],
                price=order['price'],
                timestamp=datetime.now(),
                status='open',
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                trailing_stop=signal.price * (1 - self.config['risk']['trailing_stop_distance']) if self.config['risk']['use_trailing_stop'] else None
            )
            
            # Add to active trades
            self.active_trades[trade.id] = trade
            
            self.logger.info(f"Trade executed successfully: {trade.id}")
            
            # Monitor trade
            asyncio.create_task(self.monitor_trade(trade, exchange))
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
            raise
    
    def select_best_exchange(self, symbol: str) -> Optional[ccxt.Exchange]:
        """Select the best exchange for a given symbol"""
        for exchange_name, exchange in self.exchanges.items():
            try:
                if symbol in exchange.symbols:
                    return exchange
            except:
                continue
        return None
    
    async def monitor_trade(self, trade: Trade, exchange: ccxt.Exchange):
        """Monitor an active trade"""
        try:
            while trade.status == 'open':
                # Fetch current price
                ticker = await exchange.fetch_ticker(trade.symbol)
                current_price = ticker['last']
                
                # Update PnL
                if trade.side == 'buy':
                    trade.pnl = (current_price - trade.price) * trade.amount
                    
                    # Check stop loss
                    if trade.stop_loss and current_price <= trade.stop_loss:
                        self.logger.info(f"Stop loss triggered for {trade.symbol}")
                        await self.close_trade(trade, exchange, 'stop_loss')
                        break
                    
                    # Check take profit
                    if trade.take_profit and current_price >= trade.take_profit:
                        self.logger.info(f"Take profit triggered for {trade.symbol}")
                        await self.close_trade(trade, exchange, 'take_profit')
                        break
                    
                    # Update trailing stop
                    if trade.trailing_stop and current_price > trade.price:
                        new_trailing_stop = current_price * (1 - self.config['risk']['trailing_stop_distance'])
                        if new_trailing_stop > trade.trailing_stop:
                            trade.trailing_stop = new_trailing_stop
                            self.logger.info(f"Updated trailing stop for {trade.symbol}: {trade.trailing_stop}")
                    
                    # Check trailing stop
                    if trade.trailing_stop and current_price <= trade.trailing_stop:
                        self.logger.info(f"Trailing stop triggered for {trade.symbol}")
                        await self.close_trade(trade, exchange, 'trailing_stop')
                        break
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            self.logger.error(f"Error monitoring trade {trade.id}: {str(e)}")
    
    async def close_trade(self, trade: Trade, exchange: ccxt.Exchange, reason: str):
        """Close a trade"""
        try:
            # Create opposite order to close position
            close_side = 'sell' if trade.side == 'buy' else 'buy'
            
            order = await exchange.create_order(
                symbol=trade.symbol,
                type='market',
                side=close_side,
                amount=trade.amount
            )
            
            # Update trade status
            trade.status = 'closed'
            trade.fees = order.get('fee', {}).get('cost', 0)
            
            # Add to history
            self.trade_history.append(trade)
            
            # Remove from active trades
            if trade.id in self.active_trades:
                del self.active_trades[trade.id]
            
            self.logger.info(f"Trade {trade.id} closed due to {reason}. PnL: {trade.pnl:.4f}")
            
        except Exception as e:
            self.logger.error(f"Error closing trade {trade.id}: {str(e)}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        total_pnl = sum(trade.pnl for trade in self.trade_history)
        
        return {
            'active_trades': len(self.active_trades),
            'total_trades': len(self.trade_history),
            'total_pnl': total_pnl,
            'daily_trades': self.daily_trades,
            'win_rate': self.calculate_win_rate(),
            'average_pnl': total_pnl / len(self.trade_history) if self.trade_history else 0
        }
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate"""
        if not self.trade_history:
            return 0.0
        
        winning_trades = sum(1 for trade in self.trade_history if trade.pnl > 0)
        return winning_trades / len(self.trade_history)
    
    async def close(self):
        """Close all connections"""
        for exchange in self.exchanges.values():
            await exchange.close()

async def main():
    """Test the automated trading system"""
    trading_system = AutomatedTrading()
    await trading_system.initialize_exchanges()
    
    # Example usage
    print("Automated Trading System initialized")
    print(f"Portfolio summary: {trading_system.get_portfolio_summary()}")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await trading_system.close()

if __name__ == "__main__":
    asyncio.run(main())
