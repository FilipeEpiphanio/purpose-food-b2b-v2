#!/usr/bin/env python3
"""
Copy Trading System Execution Script
Manages master/slave copy trading functionality
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

from trading.copy_trading import CopyTradingAPI, TradeCopier, CopyMode
from exchange.metatrader5_integration import MetaTrader5Integration
from analysis.momentum_analyzer import AdvancedMomentumAnalyzer
from ml.generative_sentiment_analyzer import GenerativeSentimentAnalyzer
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/copy_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CopyTradingBot:
    """Advanced copy trading bot with AI-enhanced signal filtering"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = ConfigManager(config_path)
        self.copy_trading_api = CopyTradingAPI()
        self.trade_copier = TradeCopier()
        self.mt5_integration = MetaTrader5Integration()
        self.momentum_analyzer = AdvancedMomentumAnalyzer()
        self.sentiment_analyzer = GenerativeSentimentAnalyzer()
        
        self.running = False
        self.trades_copied = 0
        self.total_volume_copied = 0.0
        self.active_masters = set()
        
    async def initialize(self):
        """Initialize copy trading system"""
        logger.info("Initializing copy trading system...")
        
        try:
            # Initialize copy trading database
            await self.copy_trading_api.initialize_database()
            logger.info("Copy trading database initialized")
            
            # Connect to MetaTrader 5
            if not await self.mt5_integration.connect():
                logger.error("Failed to connect to MetaTrader 5")
                return False
            
            # Load master accounts
            await self.load_master_accounts()
            
            # Initialize AI components
            await self.initialize_ai_components()
            
            logger.info("Copy trading system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing copy trading system: {e}")
            return False
    
    async def load_master_accounts(self):
        """Load configured master accounts"""
        try:
            master_configs = self.config.get('copy_trading.masters', [])
            
            for master_config in master_configs:
                master_id = await self.copy_trading_api.add_master_account(
                    name=master_config['name'],
                    account_id=master_config['account_id'],
                    broker=master_config.get('broker', 'MetaTrader'),
                    description=master_config.get('description', ''),
                    performance_fee=master_config.get('performance_fee', 0.0),
                    minimum_investment=master_config.get('minimum_investment', 1000)
                )
                
                self.active_masters.add(master_id)
                logger.info(f"Loaded master account: {master_config['name']} (ID: {master_id})")
            
            logger.info(f"Loaded {len(self.active_masters)} master accounts")
            
        except Exception as e:
            logger.error(f"Error loading master accounts: {e}")
    
    async def initialize_ai_components(self):
        """Initialize AI analysis components"""
        try:
            # Configure sentiment analyzer
            sentiment_config = self.config.get('sentiment_analysis', {})
            self.sentiment_analyzer.config.update(sentiment_config)
            
            logger.info("AI components initialized for copy trading")
            
        except Exception as e:
            logger.error(f"Error initializing AI components: {e}")
    
    async def analyze_master_performance(self, master_id: str) -> Dict:
        """Analyze master account performance and risk"""
        try:
            # Get master account info
            master = await self.copy_trading_api.get_master_account(master_id)
            if not master:
                return {}
            
            # Get recent trades
            recent_trades = await self.copy_trading_api.get_master_trades(
                master_id, 
                days_back=30
            )
            
            if not recent_trades:
                return {'status': 'no_trades'}
            
            # Calculate performance metrics
            performance = self.calculate_performance_metrics(recent_trades)
            
            # Risk analysis
            risk_metrics = self.analyze_risk_metrics(recent_trades)
            
            # AI-enhanced analysis
            ai_analysis = await self.ai_enhanced_analysis(master, recent_trades)
            
            return {
                'master_id': master_id,
                'master_name': master.name,
                'performance': performance,
                'risk': risk_metrics,
                'ai_analysis': ai_analysis,
                'recommendation': self.generate_master_recommendation(performance, risk_metrics, ai_analysis),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing master performance: {e}")
            return {}
    
    def calculate_performance_metrics(self, trades: List) -> Dict:
        """Calculate performance metrics from trade history"""
        try:
            if not trades:
                return {}
            
            # Calculate basic metrics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t.profit > 0])
            losing_trades = len([t for t in trades if t.profit < 0])
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate returns
            total_profit = sum(t.profit for t in trades)
            total_return = (total_profit / 10000) * 100  # Assuming $10k base
            
            # Calculate average metrics
            avg_win = np.mean([t.profit for t in trades if t.profit > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([t.profit for t in trades if t.profit < 0]) if losing_trades > 0 else 0
            
            # Calculate Sharpe ratio (simplified)
            returns = [t.profit for t in trades]
            sharpe_ratio = np.mean(returns) / np.std(returns) if len(returns) > 1 and np.std(returns) > 0 else 0
            
            return {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'total_return': total_return,
                'total_profit': total_profit,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'sharpe_ratio': sharpe_ratio,
                'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def analyze_risk_metrics(self, trades: List) -> Dict:
        """Analyze risk metrics"""
        try:
            if not trades:
                return {}
            
            # Calculate drawdown
            cumulative_returns = []
            cumulative = 0
            for trade in trades:
                cumulative += trade.profit
                cumulative_returns.append(cumulative)
            
            peak = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - peak) / peak * 100
            max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
            
            # Calculate volatility
            returns = [t.profit for t in trades]
            volatility = np.std(returns) if len(returns) > 1 else 0
            
            # Risk-adjusted return
            risk_adjusted_return = np.mean(returns) / volatility if volatility > 0 else 0
            
            return {
                'max_drawdown': max_drawdown,
                'volatility': volatility,
                'risk_adjusted_return': risk_adjusted_return,
                'consecutive_losses': self.calculate_consecutive_losses(trades),
                'avg_trade_duration': np.mean([t.duration for t in trades if hasattr(t, 'duration')]) if trades else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing risk metrics: {e}")
            return {}
    
    def calculate_consecutive_losses(self, trades: List) -> int:
        """Calculate maximum consecutive losses"""
        try:
            max_consecutive = 0
            current_consecutive = 0
            
            for trade in trades:
                if trade.profit < 0:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            return max_consecutive
            
        except Exception as e:
            logger.error(f"Error calculating consecutive losses: {e}")
            return 0
    
    async def ai_enhanced_analysis(self, master, trades: List) -> Dict:
        """AI-enhanced analysis of master performance"""
        try:
            # Analyze trading patterns
            pattern_analysis = self.analyze_trading_patterns(trades)
            
            # Sentiment correlation analysis
            sentiment_correlation = await self.analyze_sentiment_correlation(master, trades)
            
            # Market condition analysis
            market_analysis = await self.analyze_market_conditions_during_trades(trades)
            
            # Predictive analysis
            prediction = self.predict_future_performance(trades)
            
            return {
                'pattern_analysis': pattern_analysis,
                'sentiment_correlation': sentiment_correlation,
                'market_analysis': market_analysis,
                'performance_prediction': prediction,
                'ai_score': self.calculate_ai_score(pattern_analysis, sentiment_correlation, market_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error in AI-enhanced analysis: {e}")
            return {}
    
    def analyze_trading_patterns(self, trades: List) -> Dict:
        """Analyze trading patterns using AI"""
        try:
            if len(trades) < 10:
                return {'status': 'insufficient_data'}
            
            # Analyze time patterns
            trade_hours = [t.open_time.hour for t in trades if hasattr(t, 'open_time')]
            hour_distribution = pd.Series(trade_hours).value_counts().to_dict()
            
            # Analyze day of week patterns
            trade_days = [t.open_time.weekday() for t in trades if hasattr(t, 'open_time')]
            day_distribution = pd.Series(trade_days).value_counts().to_dict()
            
            # Analyze symbol preferences
            symbol_distribution = pd.Series([t.symbol for t in trades]).value_counts().to_dict()
            
            # Analyze trade duration patterns
            durations = [t.duration for t in trades if hasattr(t, 'duration')]
            avg_duration = np.mean(durations) if durations else 0
            
            return {
                'preferred_trading_hours': hour_distribution,
                'preferred_trading_days': day_distribution,
                'preferred_symbols': symbol_distribution,
                'avg_trade_duration': avg_duration,
                'pattern_score': self.calculate_pattern_score(hour_distribution, day_distribution, symbol_distribution)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trading patterns: {e}")
            return {}
    
    async def analyze_sentiment_correlation(self, master, trades: List) -> Dict:
        """Analyze correlation with market sentiment"""
        try:
            # Get symbols traded by master
            symbols = list(set([t.symbol for t in trades]))
            
            sentiment_correlations = {}
            
            for symbol in symbols:
                # Get sentiment data for the period
                symbol_trades = [t for t in trades if t.symbol == symbol]
                if not symbol_trades:
                    continue
                
                # Get sentiment summary for the period
                sentiment_summary = await self.sentiment_analyzer.get_sentiment_summary(
                    symbol, 
                    hours_back=168  # 1 week
                )
                
                if sentiment_summary['status'] == 'success':
                    sentiment_correlations[symbol] = {
                        'sentiment_score': sentiment_summary['aggregation'].overall_score,
                        'trade_performance': np.mean([t.profit for t in symbol_trades]),
                        'correlation': self.calculate_correlation(sentiment_summary, symbol_trades)
                    }
            
            return {
                'symbol_correlations': sentiment_correlations,
                'overall_sentiment_alignment': np.mean([c['correlation'] for c in sentiment_correlations.values()]) if sentiment_correlations else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment correlation: {e}")
            return {}
    
    def calculate_correlation(self, sentiment_summary: Dict, trades: List) -> float:
        """Calculate correlation between sentiment and trade performance"""
        try:
            # Simplified correlation calculation
            sentiment_score = sentiment_summary['aggregation'].overall_score
            avg_trade_profit = np.mean([t.profit for t in trades])
            
            # Simple correlation (would be more sophisticated in real implementation)
            if sentiment_score > 0 and avg_trade_profit > 0:
                return 0.8
            elif sentiment_score < 0 and avg_trade_profit < 0:
                return 0.8
            elif sentiment_score == 0 and abs(avg_trade_profit) < 0.1:
                return 0.5
            else:
                return -0.3
                
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    async def analyze_market_conditions_during_trades(self, trades: List) -> Dict:
        """Analyze market conditions during trades"""
        try:
            # This would analyze market volatility, trends, etc. during trade periods
            # For now, return simplified analysis
            return {
                'avg_volatility': np.random.uniform(0.1, 0.3),
                'market_trend': np.random.choice(['bullish', 'bearish', 'sideways']),
                'market_regime': np.random.choice(['trending', 'ranging', 'volatile'])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return {}
    
    def predict_future_performance(self, trades: List) -> Dict:
        """Predict future performance based on historical data"""
        try:
            if len(trades) < 20:
                return {'status': 'insufficient_data'}
            
            # Simple prediction based on recent performance
            recent_trades = trades[-10:]  # Last 10 trades
            recent_win_rate = len([t for t in recent_trades if t.profit > 0]) / len(recent_trades)
            recent_avg_profit = np.mean([t.profit for t in recent_trades])
            
            # Trend analysis
            profit_trend = self.analyze_profit_trend(trades)
            
            return {
                'predicted_win_rate': recent_win_rate * 0.9,  # Conservative estimate
                'predicted_avg_profit': recent_avg_profit * 0.8,
                'confidence': min(len(trades) / 100, 1.0),  # Higher confidence with more data
                'profit_trend': profit_trend
            }
            
        except Exception as e:
            logger.error(f"Error predicting future performance: {e}")
            return {}
    
    def analyze_profit_trend(self, trades: List) -> str:
        """Analyze profit trend"""
        try:
            if len(trades) < 5:
                return 'insufficient_data'
            
            # Simple trend analysis
            recent_profits = [t.profit for t in trades[-10:]]
            older_profits = [t.profit for t in trades[:-10]] if len(trades) > 10 else []
            
            if not older_profits:
                return 'stable'
            
            recent_avg = np.mean(recent_profits)
            older_avg = np.mean(older_profits)
            
            if recent_avg > older_avg * 1.1:
                return 'improving'
            elif recent_avg < older_avg * 0.9:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error analyzing profit trend: {e}")
            return 'error'
    
    def calculate_pattern_score(self, hour_dist: Dict, day_dist: Dict, symbol_dist: Dict) -> float:
        """Calculate pattern consistency score"""
        try:
            # Higher score for consistent patterns
            hour_consistency = max(hour_dist.values()) / sum(hour_dist.values()) if hour_dist else 0
            day_consistency = max(day_dist.values()) / sum(day_dist.values()) if day_dist else 0
            symbol_consistency = max(symbol_dist.values()) / sum(symbol_dist.values()) if symbol_dist else 0
            
            return (hour_consistency + day_consistency + symbol_consistency) / 3
            
        except Exception as e:
            logger.error(f"Error calculating pattern score: {e}")
            return 0.0
    
    def calculate_ai_score(self, pattern_analysis: Dict, sentiment_corr: Dict, market_analysis: Dict) -> float:
        """Calculate overall AI score"""
        try:
            pattern_score = pattern_analysis.get('pattern_score', 0) if pattern_analysis else 0
            sentiment_score = abs(sentiment_corr.get('overall_sentiment_alignment', 0)) if sentiment_corr else 0
            market_score = 0.5  # Placeholder for market analysis score
            
            return (pattern_score + sentiment_score + market_score) / 3
            
        except Exception as e:
            logger.error(f"Error calculating AI score: {e}")
            return 0.0
    
    def generate_master_recommendation(self, performance: Dict, risk: Dict, ai_analysis: Dict) -> str:
        """Generate recommendation for master account"""
        try:
            # Weighted scoring
            performance_score = 0.0
            if performance:
                performance_score += (performance.get('win_rate', 0) / 100) * 0.3
                performance_score += min(performance.get('sharpe_ratio', 0) / 2, 1) * 0.2
                performance_score += (performance.get('profit_factor', 1) - 1) / 2 * 0.2
            
            risk_score = 0.0
            if risk:
                risk_score += max(0, 1 - abs(risk.get('max_drawdown', 0)) / 50) * 0.3  # Penalize >50% drawdown
                risk_score += max(0, 1 - risk.get('volatility', 0) / 2) * 0.2  # Penalize high volatility
            
            ai_score = ai_analysis.get('ai_score', 0) if ai_analysis else 0
            
            total_score = performance_score + risk_score + ai_score
            
            if total_score >= 0.8:
                return 'STRONG_BUY'
            elif total_score >= 0.6:
                return 'BUY'
            elif total_score >= 0.4:
                return 'HOLD'
            elif total_score >= 0.2:
                return 'CAUTION'
            else:
                return 'AVOID'
                
        except Exception as e:
            logger.error(f"Error generating master recommendation: {e}")
            return 'ERROR'
    
    async def copy_trading_cycle(self):
        """Main copy trading cycle"""
        try:
            logger.info("Starting copy trading cycle...")
            
            # Analyze all master accounts
            master_analyses = {}
            for master_id in self.active_masters:
                analysis = await self.analyze_master_performance(master_id)
                if analysis:
                    master_analyses[master_id] = analysis
            
            # Filter masters based on AI analysis
            recommended_masters = []
            for master_id, analysis in master_analyses.items():
                if analysis.get('recommendation') in ['BUY', 'STRONG_BUY']:
                    recommended_masters.append(master_id)
            
            logger.info(f"Recommended masters: {len(recommended_masters)} out of {len(self.active_masters)}")
            
            # Copy trades from recommended masters
            for master_id in recommended_masters:
                try:
                    await self.copy_master_trades(master_id)
                    await asyncio.sleep(1)  # Delay between masters
                except Exception as e:
                    logger.error(f"Error copying trades from master {master_id}: {e}")
                    continue
            
            logger.info("Copy trading cycle completed")
            
        except Exception as e:
            logger.error(f"Error in copy trading cycle: {e}")
    
    async def copy_master_trades(self, master_id: str):
        """Copy trades from a specific master"""
        try:
            # Get master's recent trades
            recent_trades = await self.copy_trading_api.get_master_trades(master_id, days_back=1)
            
            if not recent_trades:
                return
            
            # Get slave accounts for this master
            slave_accounts = await self.copy_trading_api.get_slave_accounts(master_id)
            
            if not slave_accounts:
                return
            
            # Copy each trade
            copied_count = 0
            for trade in recent_trades:
                if trade.status != 'ACTIVE':
                    continue
                
                # Copy to each slave
                for slave in slave_accounts:
                    try:
                        success = await self.copy_trade_to_slave(trade, master_id, slave.id)
                        if success:
                            copied_count += 1
                            
                    except Exception as e:
                        logger.error(f"Error copying trade to slave {slave.id}: {e}")
                        continue
            
            if copied_count > 0:
                logger.info(f"Copied {copied_count} trades from master {master_id}")
                self.trades_copied += copied_count
            
        except Exception as e:
            logger.error(f"Error copying master trades: {e}")
    
    async def copy_trade_to_slave(self, master_trade, master_id: str, slave_id: str) -> bool:
        """Copy a specific trade to slave account"""
        try:
            # Get slave account info
            slave = await self.copy_trading_api.get_slave_account(slave_id)
            if not slave:
                return False
            
            # Calculate copy parameters
            copy_params = self.calculate_copy_parameters(master_trade, master_id, slave)
            
            # Execute copy trade
            copy_trade = await self.trade_copier.copy_trade(
                master_trade=master_trade,
                slave_account=slave,
                copy_ratio=copy_params['ratio'],
                max_slippage=copy_params['max_slippage'],
                copy_mode=copy_params['mode']
            )
            
            if copy_trade:
                # Record copy trade
                await self.copy_trading_api.record_copy_trade(
                    master_trade_id=master_trade.id,
                    slave_trade_id=copy_trade.id,
                    copy_ratio=copy_params['ratio'],
                    slave_account_id=slave_id
                )
                
                self.total_volume_copied += copy_trade.volume
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error copying trade to slave: {e}")
            return False
    
    def calculate_copy_parameters(self, master_trade, master_id: str, slave) -> Dict:
        """Calculate copy parameters based on slave settings and risk"""
        try:
            # Get master account
            master = self.copy_trading_api.masters.get(master_id)
            if not master:
                return {'ratio': 1.0, 'max_slippage': 2.0, 'mode': CopyMode.FULL_COPY}
            
            # Calculate copy ratio based on account sizes
            master_balance = master.balance
            slave_balance = slave.balance
            
            if master_balance > 0:
                ratio = (slave_balance / master_balance) * slave.copy_multiplier
            else:
                ratio = slave.copy_multiplier
            
            # Apply risk limits
            max_ratio = slave.max_copy_ratio
            ratio = min(ratio, max_ratio)
            
            return {
                'ratio': ratio,
                'max_slippage': slave.max_slippage,
                'mode': slave.copy_mode
            }
            
        except Exception as e:
            logger.error(f"Error calculating copy parameters: {e}")
            return {'ratio': 1.0, 'max_slippage': 2.0, 'mode': CopyMode.FULL_COPY}
    
    async def monitor_copy_trades(self):
        """Monitor copied trades and manage risk"""
        try:
            # Get all active copy trades
            active_copies = await self.copy_trading_api.get_active_copy_trades()
            
            if not active_copies:
                return
            
            logger.info(f"Monitoring {len(active_copies)} active copy trades...")
            
            for copy_trade in active_copies:
                try:
                    # Check if trade needs adjustment or closure
                    await self.monitor_copy_trade(copy_trade)
                    
                except Exception as e:
                    logger.error(f"Error monitoring copy trade {copy_trade.id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error monitoring copy trades: {e}")
    
    async def monitor_copy_trade(self, copy_trade):
        """Monitor individual copy trade"""
        try:
            # Get current market price
            current_price = await self.mt5_integration.get_current_price(copy_trade.symbol)
            if not current_price:
                return
            
            # Check if trade should be closed based on master trade
            master_trade = await self.copy_trading_api.get_master_trade(copy_trade.master_trade_id)
            if not master_trade:
                return
            
            # If master trade is closed, close copy trade
            if master_trade.status == 'CLOSED' and copy_trade.status == 'ACTIVE':
                await self.trade_copier.close_copy_trade(copy_trade)
                logger.info(f"Closed copy trade {copy_trade.id} following master closure")
                return
            
            # Risk monitoring
            risk_check = await self.perform_copy_trade_risk_check(copy_trade, current_price)
            if risk_check['should_close']:
                await self.trade_copier.close_copy_trade(copy_trade)
                logger.info(f"Closed copy trade {copy_trade.id} due to risk: {risk_check['reason']}")
            
        except Exception as e:
            logger.error(f"Error monitoring copy trade: {e}")
    
    async def perform_copy_trade_risk_check(self, copy_trade, current_price: float) -> Dict:
        """Perform risk check on copy trade"""
        try:
            # Calculate current P&L
            if copy_trade.trade_type == 'BUY':
                current_pnl = (current_price - copy_trade.open_price) * copy_trade.volume
            else:  # SELL
                current_pnl = (copy_trade.open_price - current_price) * copy_trade.volume
            
            # Check against stop loss
            if current_pnl <= -copy_trade.stop_loss:
                return {'should_close': True, 'reason': 'Stop loss reached'}
            
            # Check against take profit
            if current_pnl >= copy_trade.take_profit:
                return {'should_close': True, 'reason': 'Take profit reached'}
            
            # Check against maximum loss
            max_loss = copy_trade.volume * copy_trade.open_price * 0.05  # 5% max loss
            if current_pnl <= -max_loss:
                return {'should_close': True, 'reason': 'Maximum loss exceeded'}
            
            return {'should_close': False, 'reason': ''}
            
        except Exception as e:
            logger.error(f"Error performing risk check: {e}")
            return {'should_close': False, 'reason': 'error'}
    
    async def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        try:
            # Get overall statistics
            stats = await self.copy_trading_api.get_copy_trading_statistics()
            
            # Get master performance summaries
            master_summaries = {}
            for master_id in self.active_masters:
                analysis = await self.analyze_master_performance(master_id)
                if analysis:
                    master_summaries[master_id] = analysis
            
            # Calculate overall performance
            overall_performance = self.calculate_overall_performance(master_summaries)
            
            return {
                'timestamp': datetime.now(),
                'overall_stats': stats,
                'master_summaries': master_summaries,
                'overall_performance': overall_performance,
                'trades_copied_today': self.trades_copied,
                'volume_copied_today': self.total_volume_copied
            }
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {}
    
    def calculate_overall_performance(self, master_summaries: Dict) -> Dict:
        """Calculate overall copy trading performance"""
        try:
            if not master_summaries:
                return {}
            
            # Aggregate performance metrics
            total_return = np.mean([s['performance'].get('total_return', 0) for s in master_summaries.values()])
            avg_win_rate = np.mean([s['performance'].get('win_rate', 0) for s in master_summaries.values()])
            avg_sharpe = np.mean([s['performance'].get('sharpe_ratio', 0) for s in master_summaries.values()])
            avg_max_dd = np.mean([s['risk'].get('max_drawdown', 0) for s in master_summaries.values()])
            
            return {
                'total_return': total_return,
                'avg_win_rate': avg_win_rate,
                'avg_sharpe_ratio': avg_sharpe,
                'avg_max_drawdown': avg_max_dd,
                'risk_score': self.calculate_risk_score(avg_max_dd, avg_sharpe)
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall performance: {e}")
            return {}
    
    def calculate_risk_score(self, max_drawdown: float, sharpe_ratio: float) -> float:
        """Calculate risk score (0-100, lower is better)"""
        try:
            # Drawdown component (0-50 points)
            dd_score = min(abs(max_drawdown) / 2, 50)
            
            # Sharpe ratio component (0-50 points)
            sharpe_score = max(0, (2 - sharpe_ratio) / 2 * 50) if sharpe_ratio < 2 else 0
            
            return dd_score + sharpe_score
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 100.0
    
    async def run(self):
        """Main copy trading loop"""
        logger.info("Starting copy trading bot...")
        
        if not await self.initialize():
            logger.error("Failed to initialize copy trading system")
            return
        
        self.running = True
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                logger.info(f"Starting copy trading cycle #{cycle_count}")
                
                # Copy trading cycle
                await self.copy_trading_cycle()
                
                # Monitor existing copies
                await self.monitor_copy_trades()
                
                # Generate periodic reports
                if cycle_count % 24 == 0:  # Every 24 cycles (daily)
                    report = await self.generate_performance_report()
                    self.log_performance_report(report)
                
                # Reset daily counters
                if cycle_count % 24 == 0:
                    self.trades_copied = 0
                    self.total_volume_copied = 0.0
                
                # Wait for next cycle
                cycle_interval = self.config.get('copy_trading.cycle_interval_minutes', 60)
                logger.info(f"Waiting {cycle_interval} minutes for next cycle...")
                await asyncio.sleep(cycle_interval * 60)
                
        except KeyboardInterrupt:
            logger.info("Copy trading bot stopped by user")
        except Exception as e:
            logger.error(f"Error in main copy trading loop: {e}")
        finally:
            await self.shutdown()
    
    def log_performance_report(self, report: Dict):
        """Log performance report"""
        try:
            if not report:
                return
            
            logger.info("=== Copy Trading Performance Report ===")
            logger.info(f"Timestamp: {report.get('timestamp', 'N/A')}")
            
            overall_performance = report.get('overall_performance', {})
            if overall_performance:
                logger.info(f"Overall Return: {overall_performance.get('total_return', 0):.2f}%")
                logger.info(f"Average Win Rate: {overall_performance.get('avg_win_rate', 0):.1f}%")
                logger.info(f"Average Sharpe Ratio: {overall_performance.get('avg_sharpe_ratio', 0):.2f}")
                logger.info(f"Average Max Drawdown: {overall_performance.get('avg_max_drawdown', 0):.2f}%")
                logger.info(f"Risk Score: {overall_performance.get('risk_score', 0):.1f}/100")
            
            logger.info(f"Trades Copied Today: {report.get('trades_copied_today', 0)}")
            logger.info(f"Volume Copied Today: {report.get('volume_copied_today', 0):.2f}")
            
            # Save report to file
            report_path = Path('logs/copy_trading_reports')
            report_path.mkdir(exist_ok=True)
            
            report_file = report_path / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, default=str, indent=2)
            
            logger.info(f"Performance report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Error logging performance report: {e}")
    
    async def shutdown(self):
        """Shutdown copy trading system"""
        logger.info("Shutting down copy trading system...")
        
        try:
            # Close all active copy trades if configured
            if self.config.get('copy_trading.close_on_shutdown', False):
                active_copies = await self.copy_trading_api.get_active_copy_trades()
                for copy_trade in active_copies:
                    await self.trade_copier.close_copy_trade(copy_trade)
                logger.info(f"Closed {len(active_copies)} copy trades on shutdown")
            
            # Disconnect from MT5
            await self.mt5_integration.disconnect()
            logger.info("Disconnected from MetaTrader 5")
            
            # Generate final report
            final_report = await self.generate_performance_report()
            self.log_performance_report(final_report)
            
            logger.info("Copy trading system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main entry point"""
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    
    # Create copy trading bot
    bot = CopyTradingBot()
    
    # Run copy trading bot
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script error: {e}")