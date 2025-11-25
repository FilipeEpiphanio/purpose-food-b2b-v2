#!/usr/bin/env python3
"""
MetaTrader 5 Trading Execution Script
Integrates with MetaTrader 5 platform for automated trading
"""

import asyncio
import logging
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from exchange.metatrader5_integration import MetaTrader5Integration
from analysis.momentum_analyzer import AdvancedMomentumAnalyzer
from analysis.pattern_recognition import AdvancedPatternRecognition
from ml.generative_sentiment_analyzer import GenerativeSentimentAnalyzer
from trading.risk_manager import RiskManager
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/metatrader_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MetaTraderTradingBot:
    """Advanced MetaTrader 5 trading bot with AI integration"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = ConfigManager(config_path)
        self.mt5_integration = MetaTrader5Integration()
        self.momentum_analyzer = AdvancedMomentumAnalyzer()
        self.pattern_recognition = AdvancedPatternRecognition()
        self.sentiment_analyzer = GenerativeSentimentAnalyzer()
        self.risk_manager = RiskManager()
        
        self.running = False
        self.trades_executed = 0
        self.daily_pnl = 0.0
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing MetaTrader 5 trading bot...")
        
        try:
            # Connect to MetaTrader 5
            if not await self.mt5_integration.connect():
                logger.error("Failed to connect to MetaTrader 5")
                return False
            
            # Verify account
            account_info = await self.mt5_integration.get_account_info()
            if not account_info:
                logger.error("Failed to get account info")
                return False
            
            logger.info(f"Connected to MetaTrader 5 - Account: {account_info.login}")
            logger.info(f"Balance: ${account_info.balance:.2f}, Equity: ${account_info.equity:.2f}")
            
            # Initialize AI components
            await self.initialize_ai_components()
            
            logger.info("MetaTrader 5 trading bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing trading bot: {e}")
            return False
    
    async def initialize_ai_components(self):
        """Initialize AI analysis components"""
        logger.info("Initializing AI components...")
        
        try:
            # Load ML models
            self.pattern_recognition.load_models()
            logger.info("Pattern recognition models loaded")
            
            # Configure sentiment analyzer
            sentiment_config = self.config.get('sentiment_analysis', {})
            self.sentiment_analyzer.config.update(sentiment_config)
            logger.info("Sentiment analyzer configured")
            
        except Exception as e:
            logger.error(f"Error initializing AI components: {e}")
    
    async def analyze_market_conditions(self, symbol: str) -> Dict:
        """Comprehensive market analysis"""
        try:
            logger.info(f"Analyzing market conditions for {symbol}...")
            
            # Get historical data
            rates = await self.mt5_integration.get_rates(symbol, 100)
            if not rates:
                logger.warning(f"No historical data available for {symbol}")
                return {}
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Momentum analysis
            momentum_signals = self.momentum_analyzer.analyze(df)
            
            # Pattern recognition
            patterns = self.pattern_recognition.analyze(df)
            
            # Sentiment analysis
            sentiment_summary = await self.sentiment_analyzer.get_sentiment_summary(symbol, hours_back=24)
            
            # Combine analysis results
            analysis = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'momentum': momentum_signals,
                'patterns': patterns,
                'sentiment': sentiment_summary,
                'current_price': df['close'].iloc[-1],
                'price_change_24h': ((df['close'].iloc[-1] - df['close'].iloc[-24]) / df['close'].iloc[-24]) * 100 if len(df) >= 24 else 0
            }
            
            # Generate trading signal
            signal = self.generate_trading_signal(analysis)
            analysis['signal'] = signal
            
            logger.info(f"Market analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions for {symbol}: {e}")
            return {}
    
    def generate_trading_signal(self, analysis: Dict) -> Dict:
        """Generate trading signal based on comprehensive analysis"""
        try:
            signal_strength = 0.0
            reasons = []
            
            # Momentum signals
            if analysis.get('momentum'):
                momentum = analysis['momentum']
                if momentum.get('composite_score'):
                    signal_strength += momentum['composite_score'] * 0.3
                    reasons.append(f"Momentum: {momentum['composite_score']:.2f}")
            
            # Pattern signals
            if analysis.get('patterns'):
                patterns = analysis['patterns']
                if patterns.get('overall_signal'):
                    pattern_signal = patterns['overall_signal']
                    if pattern_signal in ['STRONG_BUY', 'BUY']:
                        signal_strength += 0.2
                        reasons.append(f"Pattern: {pattern_signal}")
                    elif pattern_signal in ['STRONG_SELL', 'SELL']:
                        signal_strength -= 0.2
                        reasons.append(f"Pattern: {pattern_signal}")
            
            # Sentiment signals
            if analysis.get('sentiment') and analysis['sentiment'].get('status') == 'success':
                sentiment = analysis['sentiment']['aggregation']
                sentiment_score = sentiment.overall_score
                
                if sentiment.overall_category in [SentimentCategory.VERY_BULLISH, SentimentCategory.BULLISH]:
                    signal_strength += sentiment_score * 0.25
                    reasons.append(f"Sentiment: {sentiment.overall_category.value}")
                elif sentiment.overall_category in [SentimentCategory.VERY_BEARISH, SentimentCategory.BEARISH]:
                    signal_strength += sentiment_score * 0.25
                    reasons.append(f"Sentiment: {sentiment.overall_category.value}")
            
            # Price momentum
            price_change = analysis.get('price_change_24h', 0)
            if abs(price_change) > 2:  # Significant price movement
                if price_change > 0:
                    signal_strength += 0.1
                    reasons.append(f"Price momentum: +{price_change:.1f}%")
                else:
                    signal_strength -= 0.1
                    reasons.append(f"Price momentum: {price_change:.1f}%")
            
            # Determine signal
            if signal_strength > 0.5:
                signal = 'STRONG_BUY'
            elif signal_strength > 0.2:
                signal = 'BUY'
            elif signal_strength < -0.5:
                signal = 'STRONG_SELL'
            elif signal_strength < -0.2:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            return {
                'signal': signal,
                'strength': abs(signal_strength),
                'confidence': min(abs(signal_strength) + 0.3, 1.0),
                'reasons': reasons,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating trading signal: {e}")
            return {'signal': 'HOLD', 'strength': 0.0, 'confidence': 0.0, 'reasons': [], 'timestamp': datetime.now()}
    
    async def execute_trade(self, symbol: str, signal: Dict, analysis: Dict) -> bool:
        """Execute trade based on signal"""
        try:
            if signal['signal'] in ['HOLD', 'STRONG_HOLD']:
                return False
            
            # Get current market info
            symbol_info = await self.mt5_integration.get_symbol_info(symbol)
            if not symbol_info:
                logger.error(f"Failed to get symbol info for {symbol}")
                return False
            
            # Risk assessment
            risk_assessment = self.risk_manager.assess_trade_risk({
                'symbol': symbol,
                'signal': signal,
                'current_price': analysis['current_price'],
                'account_balance': (await self.mt5_integration.get_account_info()).balance
            })
            
            if not risk_assessment['approved']:
                logger.info(f"Trade rejected by risk manager: {risk_assessment['reason']}")
                return False
            
            # Determine trade parameters
            trade_type = 'BUY' if 'BUY' in signal['signal'] else 'SELL'
            volume = self.calculate_position_size(symbol, signal, risk_assessment)
            
            # Set stop loss and take profit
            sl_price, tp_price = self.calculate_sl_tp(symbol_info, analysis['current_price'], trade_type)
            
            # Execute trade
            order_result = await self.mt5_integration.place_market_order(
                symbol=symbol,
                order_type=trade_type,
                volume=volume,
                price=analysis['current_price'],
                sl=sl_price,
                tp=tp_price,
                comment=f"AI_{signal['signal']}_{int(signal['strength']*100)}"
            )
            
            if order_result and order_result.retcode == 10009:  # TRADE_RETCODE_DONE
                logger.info(f"Trade executed successfully: {trade_type} {volume} {symbol}")
                self.trades_executed += 1
                return True
            else:
                logger.error(f"Trade execution failed: {order_result.retcode if order_result else 'Unknown'}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return False
    
    def calculate_position_size(self, symbol: str, signal: Dict, risk_assessment: Dict) -> float:
        """Calculate optimal position size"""
        try:
            # Base position size (1% of account balance)
            account_info = asyncio.run(self.mt5_integration.get_account_info())
            base_size = (account_info.balance * 0.01) / signal.get('current_price', 1000)
            
            # Adjust based on signal strength
            strength_multiplier = 0.5 + (signal['strength'] * 0.5)
            
            # Adjust based on confidence
            confidence_multiplier = signal['confidence']
            
            # Risk adjustment
            risk_multiplier = risk_assessment.get('size_multiplier', 1.0)
            
            # Calculate final size
            final_size = base_size * strength_multiplier * confidence_multiplier * risk_multiplier
            
            # Ensure minimum and maximum limits
            final_size = max(0.01, min(final_size, 1.0))  # Between 0.01 and 1.0 lots
            
            return round(final_size, 2)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.1  # Default size
    
    def calculate_sl_tp(self, symbol_info, current_price: float, trade_type: str) -> tuple:
        """Calculate stop loss and take profit levels"""
        try:
            # Calculate based on ATR or fixed percentage
            sl_distance = current_price * 0.02  # 2% stop loss
            tp_distance = current_price * 0.04  # 4% take profit
            
            if trade_type == 'BUY':
                sl_price = current_price - sl_distance
                tp_price = current_price + tp_distance
            else:  # SELL
                sl_price = current_price + sl_distance
                tp_price = current_price - tp_distance
            
            # Round to symbol's tick size
            tick_size = symbol_info.point
            sl_price = round(sl_price / tick_size) * tick_size
            tp_price = round(tp_price / tick_size) * tick_size
            
            return sl_price, tp_price
            
        except Exception as e:
            logger.error(f"Error calculating SL/TP: {e}")
            return None, None
    
    async def trading_cycle(self):
        """Main trading cycle"""
        try:
            # Get configured symbols
            symbols = self.config.get('metatrader.symbols', ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD'])
            
            logger.info(f"Starting trading cycle for {len(symbols)} symbols...")
            
            for symbol in symbols:
                try:
                    # Analyze market conditions
                    analysis = await self.analyze_market_conditions(symbol)
                    if not analysis:
                        continue
                    
                    # Generate and execute signal
                    signal = analysis.get('signal', {})
                    if signal.get('signal') not in ['HOLD', 'STRONG_HOLD']:
                        await self.execute_trade(symbol, signal, analysis)
                    
                    # Log analysis results
                    self.log_analysis_results(symbol, analysis)
                    
                    # Small delay between symbols
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue
            
            logger.info("Trading cycle completed")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    def log_analysis_results(self, symbol: str, analysis: Dict):
        """Log analysis results for review"""
        try:
            signal = analysis.get('signal', {})
            sentiment = analysis.get('sentiment', {})
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'current_price': analysis.get('current_price', 0),
                'price_change_24h': analysis.get('price_change_24h', 0),
                'signal': signal.get('signal', 'HOLD'),
                'signal_strength': signal.get('strength', 0),
                'signal_confidence': signal.get('confidence', 0),
                'sentiment_score': sentiment.get('aggregation', {}).overall_score if sentiment.get('aggregation') else 0,
                'sentiment_category': sentiment.get('aggregation', {}).overall_category.value if sentiment.get('aggregation') else 'NEUTRAL'
            }
            
            # Save to analysis log
            analysis_log_path = Path('logs/analysis_log.jsonl')
            analysis_log_path.parent.mkdir(exist_ok=True)
            
            with open(analysis_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Error logging analysis results: {e}")
    
    async def monitor_positions(self):
        """Monitor open positions and manage risk"""
        try:
            positions = await self.mt5_integration.get_positions()
            if not positions:
                return
            
            logger.info(f"Monitoring {len(positions)} open positions...")
            
            for position in positions:
                try:
                    # Check if position needs adjustment
                    current_price = await self.mt5_integration.get_current_price(position.symbol)
                    if not current_price:
                        continue
                    
                    # Risk management check
                    risk_check = self.risk_manager.monitor_position(position, current_price)
                    if risk_check['action'] == 'CLOSE':
                        await self.mt5_integration.close_position(position.ticket)
                        logger.info(f"Position {position.ticket} closed by risk manager: {risk_check['reason']}")
                    
                except Exception as e:
                    logger.error(f"Error monitoring position {position.ticket}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    async def run(self):
        """Main trading loop"""
        logger.info("Starting MetaTrader 5 trading bot...")
        
        if not await self.initialize():
            logger.error("Failed to initialize trading bot")
            return
        
        self.running = True
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                logger.info(f"Starting trading cycle #{cycle_count}")
                
                # Trading cycle
                await self.trading_cycle()
                
                # Position monitoring
                await self.monitor_positions()
                
                # Daily summary
                if cycle_count % 24 == 0:  # Every 24 cycles
                    await self.daily_summary()
                
                # Wait for next cycle
                cycle_interval = self.config.get('metatrader.cycle_interval_minutes', 60)
                logger.info(f"Waiting {cycle_interval} minutes for next cycle...")
                await asyncio.sleep(cycle_interval * 60)
                
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Error in main trading loop: {e}")
        finally:
            await self.shutdown()
    
    async def daily_summary(self):
        """Generate daily trading summary"""
        try:
            account_info = await self.mt5_integration.get_account_info()
            if not account_info:
                return
            
            # Calculate daily P&L
            current_pnl = account_info.profit
            daily_change = current_pnl - self.daily_pnl
            self.daily_pnl = current_pnl
            
            logger.info(f"Daily Summary:")
            logger.info(f"  Balance: ${account_info.balance:.2f}")
            logger.info(f"  Equity: ${account_info.equity:.2f}")
            logger.info(f"  Daily P&L: ${daily_change:.2f}")
            logger.info(f"  Total P&L: ${current_pnl:.2f}")
            logger.info(f"  Trades Executed Today: {self.trades_executed}")
            
            # Reset daily counter
            self.trades_executed = 0
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
    
    async def shutdown(self):
        """Shutdown trading bot"""
        logger.info("Shutting down MetaTrader 5 trading bot...")
        
        try:
            # Close all positions if configured
            if self.config.get('metatrader.close_on_shutdown', False):
                positions = await self.mt5_integration.get_positions()
                for position in positions:
                    await self.mt5_integration.close_position(position.ticket)
                logger.info(f"Closed {len(positions)} positions on shutdown")
            
            # Disconnect from MT5
            await self.mt5_integration.disconnect()
            logger.info("Disconnected from MetaTrader 5")
            
            logger.info("Trading bot shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main entry point"""
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    # Create trading bot
    bot = MetaTraderTradingBot()
    
    # Run trading bot
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script error: {e}")