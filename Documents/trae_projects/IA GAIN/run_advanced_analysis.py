#!/usr/bin/env python3
"""
Advanced AI Analysis Execution Script
Combines momentum, pattern recognition, and sentiment analysis
"""

import asyncio
import logging
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from analysis.momentum_analyzer import AdvancedMomentumAnalyzer
from analysis.pattern_recognition import AdvancedPatternRecognition
from ml.generative_sentiment_analyzer import GenerativeSentimentAnalyzer
from exchange.metatrader5_integration import MetaTrader5Integration
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/advanced_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedAnalysisBot:
    """Advanced AI analysis bot combining multiple analysis techniques"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = ConfigManager(config_path)
        self.momentum_analyzer = AdvancedMomentumAnalyzer()
        self.pattern_recognizer = AdvancedPatternRecognition()
        self.sentiment_analyzer = GenerativeSentimentAnalyzer()
        self.mt5_integration = MetaTrader5Integration()
        
        self.analysis_results = {}
        self.signal_history = []
        self.performance_metrics = {}
        
    async def initialize(self):
        """Initialize advanced analysis system"""
        logger.info("Initializing advanced analysis system...")
        
        try:
            # Connect to MetaTrader 5
            if not await self.mt5_integration.connect():
                logger.error("Failed to connect to MetaTrader 5")
                return False
            
            # Initialize AI models
            await self.initialize_ai_models()
            
            logger.info("Advanced analysis system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing advanced analysis system: {e}")
            return False
    
    async def initialize_ai_models(self):
        """Initialize AI models for analysis"""
        try:
            # Train pattern recognition model
            logger.info("Training pattern recognition model...")
            await self.pattern_recognizer.train_model()
            
            # Initialize sentiment analyzer
            logger.info("Initializing sentiment analyzer...")
            self.sentiment_analyzer.initialize_database()
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
    
    async def perform_comprehensive_analysis(self, symbols: List[str], timeframe: str = 'H1') -> Dict:
        """Perform comprehensive AI analysis on multiple symbols"""
        logger.info(f"Performing comprehensive analysis on {len(symbols)} symbols...")
        
        analysis_results = {}
        
        try:
            for symbol in symbols:
                try:
                    logger.info(f"Analyzing {symbol}...")
                    
                    # Get historical data
                    historical_data = await self.get_historical_data(symbol, timeframe)
                    if historical_data is None or len(historical_data) < 100:
                        logger.warning(f"Insufficient data for {symbol}")
                        continue
                    
                    # Perform multi-dimensional analysis
                    symbol_analysis = await self.analyze_symbol(symbol, historical_data, timeframe)
                    
                    if symbol_analysis:
                        analysis_results[symbol] = symbol_analysis
                        
                    # Rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
                    continue
            
            # Generate overall market analysis
            market_analysis = self.generate_market_overview(analysis_results)
            
            return {
                'timestamp': datetime.now(),
                'symbols': analysis_results,
                'market_overview': market_analysis,
                'top_opportunities': self.identify_top_opportunities(analysis_results),
                'risk_assessment': self.assess_overall_risk(analysis_results)
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {}
    
    async def get_historical_data(self, symbol: str, timeframe: str, bars: int = 5000) -> Optional[pd.DataFrame]:
        """Get historical data from MetaTrader 5"""
        try:
            # Get historical data
            data = await self.mt5_integration.get_historical_data(symbol, timeframe, bars)
            
            if data is None or len(data) < 100:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
            
            # Calculate additional indicators
            df = self.calculate_additional_indicators(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def calculate_additional_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate additional technical indicators"""
        try:
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price momentum
            df['price_change'] = df['close'].pct_change()
            df['price_momentum'] = df['price_change'].rolling(window=10).mean()
            
            # Volatility
            df['volatility'] = df['price_change'].rolling(window=20).std()
            
            # Price position in daily range
            df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating additional indicators: {e}")
            return df
    
    async def analyze_symbol(self, symbol: str, data: pd.DataFrame, timeframe: str) -> Dict:
        """Perform comprehensive analysis on a single symbol"""
        try:
            # Momentum analysis
            momentum_analysis = await self.momentum_analyzer.analyze_momentum(data)
            
            # Pattern recognition
            pattern_analysis = await self.pattern_recognizer.analyze_patterns(data)
            
            # Sentiment analysis
            sentiment_analysis = await self.sentiment_analyzer.get_sentiment_summary(symbol, hours_back=168)
            
            # Market structure analysis
            market_structure = self.analyze_market_structure(data)
            
            # Risk analysis
            risk_analysis = self.analyze_symbol_risk(data)
            
            # Generate trading signal
            trading_signal = self.generate_trading_signal(
                momentum_analysis, 
                pattern_analysis, 
                sentiment_analysis, 
                market_structure, 
                risk_analysis
            )
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now(),
                'momentum': momentum_analysis,
                'patterns': pattern_analysis,
                'sentiment': sentiment_analysis,
                'market_structure': market_structure,
                'risk': risk_analysis,
                'trading_signal': trading_signal,
                'confidence_score': self.calculate_confidence_score(
                    momentum_analysis, pattern_analysis, sentiment_analysis, risk_analysis
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")
            return {}
    
    def analyze_market_structure(self, data: pd.DataFrame) -> Dict:
        """Analyze market structure"""
        try:
            if len(data) < 50:
                return {}
            
            # Support and resistance levels
            support_resistance = self.find_support_resistance_levels(data)
            
            # Trend analysis
            trend_analysis = self.analyze_trend_structure(data)
            
            # Market regime
            market_regime = self.identify_market_regime(data)
            
            # Liquidity analysis
            liquidity_analysis = self.analyze_liquidity(data)
            
            return {
                'support_levels': support_resistance['support'],
                'resistance_levels': support_resistance['resistance'],
                'trend': trend_analysis,
                'market_regime': market_regime,
                'liquidity': liquidity_analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}")
            return {}
    
    def find_support_resistance_levels(self, data: pd.DataFrame, window: int = 20) -> Dict:
        """Find support and resistance levels"""
        try:
            # Find local minima (support) and maxima (resistance)
            highs = data['high'].rolling(window=window, center=True).max() == data['high']
            lows = data['low'].rolling(window=window, center=True).min() == data['low']
            
            # Get recent levels
            recent_highs = data[highs]['high'].tail(10).values
            recent_lows = data[lows]['low'].tail(10).values
            
            # Cluster levels
            resistance_levels = self.cluster_price_levels(recent_highs)
            support_levels = self.cluster_price_levels(recent_lows)
            
            return {
                'support': support_levels,
                'resistance': resistance_levels
            }
            
        except Exception as e:
            logger.error(f"Error finding support/resistance levels: {e}")
            return {'support': [], 'resistance': []}
    
    def cluster_price_levels(self, levels: np.ndarray, threshold: float = 0.01) -> List[float]:
        """Cluster price levels"""
        try:
            if len(levels) == 0:
                return []
            
            # Sort levels
            levels = np.sort(levels)
            
            # Cluster levels within threshold
            clusters = []
            current_cluster = [levels[0]]
            
            for level in levels[1:]:
                if abs(level - np.mean(current_cluster)) / np.mean(current_cluster) <= threshold:
                    current_cluster.append(level)
                else:
                    clusters.append(np.mean(current_cluster))
                    current_cluster = [level]
            
            clusters.append(np.mean(current_cluster))
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error clustering price levels: {e}")
            return []
    
    def analyze_trend_structure(self, data: pd.DataFrame) -> Dict:
        """Analyze trend structure"""
        try:
            # Multiple timeframe trend analysis
            trends = {}
            
            # Short-term trend (10 periods)
            short_trend = self.calculate_trend_direction(data['close'].tail(10))
            trends['short_term'] = short_trend
            
            # Medium-term trend (50 periods)
            medium_trend = self.calculate_trend_direction(data['close'].tail(50))
            trends['medium_term'] = medium_trend
            
            # Long-term trend (200 periods)
            long_trend = self.calculate_trend_direction(data['close'].tail(200))
            trends['long_term'] = long_trend
            
            # Trend strength
            trend_strength = self.calculate_trend_strength(data)
            
            return {
                'trends': trends,
                'strength': trend_strength,
                'alignment': self.calculate_trend_alignment(trends)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend structure: {e}")
            return {}
    
    def calculate_trend_direction(self, prices: pd.Series) -> str:
        """Calculate trend direction"""
        try:
            if len(prices) < 5:
                return 'neutral'
            
            # Linear regression slope
            x = np.arange(len(prices))
            slope, _ = np.polyfit(x, prices, 1)
            
            # Calculate percentage change
            pct_change = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100
            
            if slope > 0 and pct_change > 2:
                return 'strong_up'
            elif slope > 0 and pct_change > 0:
                return 'up'
            elif slope < 0 and pct_change < -2:
                return 'strong_down'
            elif slope < 0 and pct_change < 0:
                return 'down'
            else:
                return 'sideways'
                
        except Exception as e:
            logger.error(f"Error calculating trend direction: {e}")
            return 'neutral'
    
    def calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Calculate trend strength"""
        try:
            # Use ADX-like calculation
            highs = data['high']
            lows = data['low']
            closes = data['close']
            
            # Calculate directional movement
            plus_dm = np.where((highs > highs.shift(1)) & (highs - highs.shift(1) > lows.shift(1) - lows), highs - highs.shift(1), 0)
            minus_dm = np.where((lows < lows.shift(1)) & (lows.shift(1) - lows > highs - highs.shift(1)), lows.shift(1) - lows, 0)
            
            # Calculate true range
            tr1 = highs - lows
            tr2 = np.abs(highs - closes.shift(1))
            tr3 = np.abs(lows - closes.shift(1))
            true_range = np.maximum(np.maximum(tr1, tr2), tr3)
            
            # Calculate directional indicators
            plus_di = 100 * pd.Series(plus_dm).rolling(14).sum() / pd.Series(true_range).rolling(14).sum()
            minus_di = 100 * pd.Series(minus_dm).rolling(14).sum() / pd.Series(true_range).rolling(14).sum()
            
            # Calculate DX
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
            
            # Return recent average
            return dx.tail(14).mean() if len(dx) >= 14 else 0
            
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 0.0
    
    def calculate_trend_alignment(self, trends: Dict) -> str:
        """Calculate trend alignment across timeframes"""
        try:
            trend_values = list(trends.values())
            
            # Count bullish vs bearish trends
            bullish = sum(1 for t in trend_values if 'up' in t)
            bearish = sum(1 for t in trend_values if 'down' in t)
            
            if bullish == len(trend_values):
                return 'all_bullish'
            elif bearish == len(trend_values):
                return 'all_bearish'
            elif bullish > bearish:
                return 'mostly_bullish'
            elif bearish > bullish:
                return 'mostly_bearish'
            else:
                return 'mixed'
                
        except Exception as e:
            logger.error(f"Error calculating trend alignment: {e}")
            return 'mixed'
    
    def identify_market_regime(self, data: pd.DataFrame) -> str:
        """Identify current market regime"""
        try:
            if len(data) < 50:
                return 'unknown'
            
            # Calculate volatility
            volatility = data['close'].pct_change().rolling(20).std().iloc[-1]
            
            # Calculate trend
            trend = self.calculate_trend_direction(data['close'].tail(50))
            
            # Determine regime
            if volatility < 0.01:  # Low volatility
                if 'up' in trend:
                    return 'low_vol_uptrend'
                elif 'down' in trend:
                    return 'low_vol_downtrend'
                else:
                    return 'low_vol_range'
            elif volatility > 0.03:  # High volatility
                return 'high_volatile'
            else:  # Medium volatility
                if 'up' in trend:
                    return 'medium_vol_uptrend'
                elif 'down' in trend:
                    return 'medium_vol_downtrend'
                else:
                    return 'medium_vol_range'
                    
        except Exception as e:
            logger.error(f"Error identifying market regime: {e}")
            return 'unknown'
    
    def analyze_liquidity(self, data: pd.DataFrame) -> Dict:
        """Analyze market liquidity"""
        try:
            if len(data) < 20:
                return {}
            
            # Volume-based liquidity
            avg_volume = data['volume'].tail(20).mean()
            volume_std = data['volume'].tail(20).std()
            
            # Spread-based liquidity (approximation)
            avg_spread = (data['high'] - data['low']).tail(20).mean()
            
            # Price impact (simplified)
            price_changes = data['close'].pct_change().abs()
            avg_price_change = price_changes.tail(20).mean()
            
            return {
                'avg_volume': avg_volume,
                'volume_consistency': avg_volume / volume_std if volume_std > 0 else 0,
                'avg_spread': avg_spread,
                'avg_price_change': avg_price_change,
                'liquidity_score': self.calculate_liquidity_score(avg_volume, avg_spread, avg_price_change)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing liquidity: {e}")
            return {}
    
    def calculate_liquidity_score(self, avg_volume: float, avg_spread: float, avg_price_change: float) -> float:
        """Calculate liquidity score (0-100, higher is better)"""
        try:
            # Volume component (0-40 points)
            volume_score = min(avg_volume / 1000000 * 40, 40)  # Normalize to millions
            
            # Spread component (0-30 points)
            spread_score = max(0, (0.01 - avg_spread) / 0.01 * 30)  # Lower spread is better
            
            # Price change component (0-30 points)
            price_score = max(0, (0.005 - avg_price_change) / 0.005 * 30)  # Lower change is better
            
            return volume_score + spread_score + price_score
            
        except Exception as e:
            logger.error(f"Error calculating liquidity score: {e}")
            return 0.0
    
    def analyze_symbol_risk(self, data: pd.DataFrame) -> Dict:
        """Analyze symbol-specific risk"""
        try:
            if len(data) < 20:
                return {}
            
            # Volatility risk
            volatility = data['close'].pct_change().rolling(20).std().iloc[-1]
            
            # Drawdown risk
            recent_high = data['high'].tail(20).max()
            current_price = data['close'].iloc[-1]
            drawdown = (recent_high - current_price) / recent_high * 100
            
            # Gap risk (simplified)
            gaps = np.abs(data['open'] - data['close'].shift(1))
            avg_gap = gaps.tail(20).mean()
            
            # Liquidity risk
            liquidity = self.analyze_liquidity(data)
            
            return {
                'volatility_risk': volatility * 100,
                'drawdown_risk': drawdown,
                'gap_risk': avg_gap / current_price * 100,
                'liquidity_risk': 100 - liquidity.get('liquidity_score', 50),
                'overall_risk_score': self.calculate_overall_risk_score(volatility, drawdown, avg_gap, current_price)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing symbol risk: {e}")
            return {}
    
    def calculate_overall_risk_score(self, volatility: float, drawdown: float, avg_gap: float, current_price: float) -> float:
        """Calculate overall risk score (0-100, lower is better)"""
        try:
            # Volatility component (0-40 points)
            vol_score = min(volatility * 100 * 2, 40)
            
            # Drawdown component (0-30 points)
            dd_score = min(drawdown / 2, 30)
            
            # Gap component (0-30 points)
            gap_score = min(avg_gap / current_price * 100 * 5, 30)
            
            return vol_score + dd_score + gap_score
            
        except Exception as e:
            logger.error(f"Error calculating overall risk score: {e}")
            return 100.0
    
    def generate_trading_signal(self, momentum: Dict, patterns: Dict, sentiment: Dict, 
                              market_structure: Dict, risk: Dict) -> Dict:
        """Generate trading signal based on all analysis"""
        try:
            # Initialize signal components
            signal_components = {}
            
            # Momentum component
            momentum_score = self.evaluate_momentum_signal(momentum)
            signal_components['momentum'] = momentum_score
            
            # Pattern component
            pattern_score = self.evaluate_pattern_signal(patterns)
            signal_components['patterns'] = pattern_score
            
            # Sentiment component
            sentiment_score = self.evaluate_sentiment_signal(sentiment)
            signal_components['sentiment'] = sentiment_score
            
            # Market structure component
            structure_score = self.evaluate_market_structure_signal(market_structure)
            signal_components['market_structure'] = structure_score
            
            # Risk component (negative weight)
            risk_score = -risk.get('overall_risk_score', 50) / 100
            signal_components['risk'] = risk_score
            
            # Calculate overall signal
            weights = {
                'momentum': 0.25,
                'patterns': 0.20,
                'sentiment': 0.15,
                'market_structure': 0.25,
                'risk': 0.15
            }
            
            overall_score = sum(score * weights[component] for component, score in signal_components.items())
            
            # Generate signal
            if overall_score >= 0.6:
                signal = 'STRONG_BUY'
            elif overall_score >= 0.3:
                signal = 'BUY'
            elif overall_score <= -0.6:
                signal = 'STRONG_SELL'
            elif overall_score <= -0.3:
                signal = 'SELL'
            else:
                signal = 'NEUTRAL'
            
            return {
                'signal': signal,
                'score': overall_score,
                'components': signal_components,
                'confidence': self.calculate_signal_confidence(signal_components),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating trading signal: {e}")
            return {'signal': 'NEUTRAL', 'score': 0.0, 'components': {}, 'confidence': 0.0}
    
    def evaluate_momentum_signal(self, momentum: Dict) -> float:
        """Evaluate momentum signal"""
        try:
            if not momentum:
                return 0.0
            
            # Get momentum score
            momentum_score = momentum.get('composite_score', 0)
            
            # Normalize to -1 to 1 range
            return max(-1, min(1, momentum_score / 100))
            
        except Exception as e:
            logger.error(f"Error evaluating momentum signal: {e}")
            return 0.0
    
    def evaluate_pattern_signal(self, patterns: Dict) -> float:
        """Evaluate pattern signal"""
        try:
            if not patterns:
                return 0.0
            
            # Get pattern predictions
            ml_prediction = patterns.get('ml_prediction', {})
            pattern_matches = patterns.get('patterns', [])
            
            # Calculate pattern score
            ml_score = ml_prediction.get('bullish_probability', 0.5) - 0.5
            
            # Add pattern match scores
            pattern_score = 0.0
            for pattern in pattern_matches:
                if pattern.get('reliability', 0) > 0.7:
                    if pattern.get('type') == 'bullish':
                        pattern_score += 0.2
                    elif pattern.get('type') == 'bearish':
                        pattern_score -= 0.2
            
            return max(-1, min(1, ml_score + pattern_score))
            
        except Exception as e:
            logger.error(f"Error evaluating pattern signal: {e}")
            return 0.0
    
    def evaluate_sentiment_signal(self, sentiment: Dict) -> float:
        """Evaluate sentiment signal"""
        try:
            if not sentiment or sentiment.get('status') != 'success':
                return 0.0
            
            # Get sentiment score
            aggregation = sentiment.get('aggregation', {})
            overall_score = aggregation.get('overall_score', 0)
            
            # Normalize to -1 to 1 range
            return overall_score / 100
            
        except Exception as e:
            logger.error(f"Error evaluating sentiment signal: {e}")
            return 0.0
    
    def evaluate_market_structure_signal(self, market_structure: Dict) -> float:
        """Evaluate market structure signal"""
        try:
            if not market_structure:
                return 0.0
            
            # Trend alignment
            trends = market_structure.get('trend', {}).get('alignment', 'mixed')
            trend_scores = {
                'all_bullish': 1.0,
                'mostly_bullish': 0.5,
                'mixed': 0.0,
                'mostly_bearish': -0.5,
                'all_bearish': -1.0
            }
            
            trend_score = trend_scores.get(trends, 0.0)
            
            # Market regime
            regime = market_structure.get('market_regime', 'unknown')
            regime_scores = {
                'low_vol_uptrend': 0.8,
                'medium_vol_uptrend': 0.6,
                'low_vol_range': 0.2,
                'medium_vol_range': 0.0,
                'medium_vol_downtrend': -0.6,
                'low_vol_downtrend': -0.8,
                'high_volatile': 0.0
            }
            
            regime_score = regime_scores.get(regime, 0.0)
            
            return (trend_score + regime_score) / 2
            
        except Exception as e:
            logger.error(f"Error evaluating market structure signal: {e}")
            return 0.0
    
    def calculate_signal_confidence(self, components: Dict) -> float:
        """Calculate signal confidence"""
        try:
            # Calculate confidence based on component agreement
            scores = list(components.values())
            
            if len(scores) == 0:
                return 0.0
            
            # Agreement measure (lower variance = higher confidence)
            variance = np.var(scores)
            agreement_score = max(0, 1 - variance)
            
            # Component strength (higher average absolute score = higher confidence)
            avg_strength = np.mean(np.abs(scores))
            strength_score = avg_strength
            
            # Final confidence
            confidence = (agreement_score + strength_score) / 2
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Error calculating signal confidence: {e}")
            return 0.0
    
    def calculate_confidence_score(self, momentum: Dict, patterns: Dict, sentiment: Dict, risk: Dict) -> float:
        """Calculate overall confidence score"""
        try:
            # Data quality scores
            momentum_quality = 1.0 if momentum else 0.0
            pattern_quality = 1.0 if patterns else 0.0
            sentiment_quality = 1.0 if sentiment and sentiment.get('status') == 'success' else 0.0
            risk_quality = 1.0 if risk else 0.0
            
            # Calculate weighted confidence
            weights = [0.3, 0.25, 0.2, 0.25]  # momentum, patterns, sentiment, risk
            qualities = [momentum_quality, pattern_quality, sentiment_quality, risk_quality]
            
            confidence = np.average(qualities, weights=weights)
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.0
    
    def generate_market_overview(self, analysis_results: Dict) -> Dict:
        """Generate overall market overview"""
        try:
            if not analysis_results:
                return {}
            
            # Count signals
            signals = {'BUY': 0, 'SELL': 0, 'NEUTRAL': 0, 'STRONG_BUY': 0, 'STRONG_SELL': 0}
            
            for symbol_analysis in analysis_results.values():
                signal = symbol_analysis.get('trading_signal', {}).get('signal', 'NEUTRAL')
                signals[signal] = signals.get(signal, 0) + 1
            
            # Calculate market sentiment
            total_symbols = len(analysis_results)
            bullish_ratio = (signals.get('BUY', 0) + signals.get('STRONG_BUY', 0)) / total_symbols
            bearish_ratio = (signals.get('SELL', 0) + signals.get('STRONG_SELL', 0)) / total_symbols
            
            # Average confidence
            avg_confidence = np.mean([
                analysis.get('confidence_score', 0) 
                for analysis in analysis_results.values()
            ])
            
            return {
                'total_symbols': total_symbols,
                'signal_distribution': signals,
                'bullish_ratio': bullish_ratio,
                'bearish_ratio': bearish_ratio,
                'market_sentiment': 'bullish' if bullish_ratio > bearish_ratio else 'bearish' if bearish_ratio > bullish_ratio else 'neutral',
                'average_confidence': avg_confidence,
                'analysis_timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating market overview: {e}")
            return {}
    
    def identify_top_opportunities(self, analysis_results: Dict) -> List[Dict]:
        """Identify top trading opportunities"""
        try:
            opportunities = []
            
            for symbol, analysis in analysis_results.items():
                signal = analysis.get('trading_signal', {})
                confidence = analysis.get('confidence_score', 0)
                
                # Score opportunities based on signal strength and confidence
                signal_strength = {
                    'STRONG_BUY': 2.0,
                    'BUY': 1.0,
                    'NEUTRAL': 0.0,
                    'SELL': -1.0,
                    'STRONG_SELL': -2.0
                }.get(signal.get('signal', 'NEUTRAL'), 0)
                
                opportunity_score = signal_strength * confidence
                
                opportunities.append({
                    'symbol': symbol,
                    'signal': signal.get('signal', 'NEUTRAL'),
                    'confidence': confidence,
                    'score': opportunity_score,
                    'momentum_score': signal.get('components', {}).get('momentum', 0),
                    'risk_score': analysis.get('risk', {}).get('overall_risk_score', 50)
                })
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: abs(x['score']), reverse=True)
            
            return opportunities[:10]  # Top 10 opportunities
            
        except Exception as e:
            logger.error(f"Error identifying top opportunities: {e}")
            return []
    
    def assess_overall_risk(self, analysis_results: Dict) -> Dict:
        """Assess overall market risk"""
        try:
            if not analysis_results:
                return {}
            
            # Aggregate risk metrics
            risk_scores = []
            volatility_scores = []
            drawdown_scores = []
            
            for analysis in analysis_results.values():
                risk = analysis.get('risk', {})
                risk_scores.append(risk.get('overall_risk_score', 50))
                volatility_scores.append(risk.get('volatility_risk', 50))
                drawdown_scores.append(risk.get('drawdown_risk', 50))
            
            avg_risk = np.mean(risk_scores)
            max_risk = np.max(risk_scores)
            risk_volatility = np.std(risk_scores)
            
            return {
                'average_risk': avg_risk,
                'maximum_risk': max_risk,
                'risk_volatility': risk_volatility,
                'risk_level': self.categorize_risk_level(avg_risk),
                'correlation_risk': self.assess_correlation_risk(analysis_results),
                'systemic_risk': self.assess_systemic_risk(analysis_results)
            }
            
        except Exception as e:
            logger.error(f"Error assessing overall risk: {e}")
            return {}
    
    def categorize_risk_level(self, avg_risk: float) -> str:
        """Categorize risk level"""
        try:
            if avg_risk < 30:
                return 'low'
            elif avg_risk < 50:
                return 'medium'
            elif avg_risk < 70:
                return 'high'
            else:
                return 'extreme'
                
        except Exception as e:
            logger.error(f"Error categorizing risk level: {e}")
            return 'unknown'
    
    def assess_correlation_risk(self, analysis_results: Dict) -> float:
        """Assess correlation risk"""
        try:
            # Simple correlation risk based on signal agreement
            signals = []
            for analysis in analysis_results.values():
                signal = analysis.get('trading_signal', {}).get('signal', 'NEUTRAL')
                signal_score = {'STRONG_BUY': 2, 'BUY': 1, 'NEUTRAL': 0, 'SELL': -1, 'STRONG_SELL': -2}.get(signal, 0)
                signals.append(signal_score)
            
            # High correlation when most signals agree
            if len(signals) < 3:
                return 0.0
            
            agreement = np.std(signals) < 0.5
            correlation_risk = 1.0 if agreement else 0.0
            
            return correlation_risk
            
        except Exception as e:
            logger.error(f"Error assessing correlation risk: {e}")
            return 0.0
    
    def assess_systemic_risk(self, analysis_results: Dict) -> float:
        """Assess systemic risk"""
        try:
            # Simple systemic risk based on market sentiment and volatility
            market_sentiments = []
            volatilities = []
            
            for analysis in analysis_results.values():
                market_structure = analysis.get('market_structure', {})
                market_sentiments.append(market_structure.get('market_regime', 'unknown'))
                
                risk = analysis.get('risk', {})
                volatilities.append(risk.get('volatility_risk', 50))
            
            # High systemic risk when many symbols are in volatile regime
            volatile_count = sum(1 for s in market_sentiments if 'volatile' in s)
            high_vol_count = sum(1 for v in volatilities if v > 50)
            
            systemic_risk = (volatile_count + high_vol_count) / (len(market_sentiments) * 2)
            
            return systemic_risk
            
        except Exception as e:
            logger.error(f"Error assessing systemic risk: {e}")
            return 0.0
    
    def create_visualization(self, analysis_results: Dict, save_path: str = None):
        """Create comprehensive visualization of analysis results"""
        try:
            # Create figure with subplots
            fig = plt.figure(figsize=(20, 16))
            
            # Signal distribution
            ax1 = plt.subplot(3, 3, 1)
            self.plot_signal_distribution(analysis_results, ax1)
            
            # Top opportunities
            ax2 = plt.subplot(3, 3, 2)
            self.plot_top_opportunities(analysis_results, ax2)
            
            # Risk heatmap
            ax3 = plt.subplot(3, 3, 3)
            self.plot_risk_heatmap(analysis_results, ax3)
            
            # Momentum scatter plot
            ax4 = plt.subplot(3, 3, 4)
            self.plot_momentum_scatter(analysis_results, ax4)
            
            # Pattern frequency
            ax5 = plt.subplot(3, 3, 5)
            self.plot_pattern_frequency(analysis_results, ax5)
            
            # Sentiment timeline
            ax6 = plt.subplot(3, 3, 6)
            self.plot_sentiment_timeline(analysis_results, ax6)
            
            # Market regime distribution
            ax7 = plt.subplot(3, 3, 7)
            self.plot_market_regime_distribution(analysis_results, ax7)
            
            # Confidence vs Signal strength
            ax8 = plt.subplot(3, 3, 8)
            self.plot_confidence_vs_signal(analysis_results, ax8)
            
            # Performance metrics
            ax9 = plt.subplot(3, 3, 9)
            self.plot_performance_metrics(analysis_results, ax9)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Visualization saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
    
    def plot_signal_distribution(self, analysis_results: Dict, ax):
        """Plot signal distribution"""
        try:
            signals = []
            for analysis in analysis_results.values():
                signal = analysis.get('trading_signal', {}).get('signal', 'NEUTRAL')
                signals.append(signal)
            
            signal_counts = pd.Series(signals).value_counts()
            
            colors = {'STRONG_BUY': 'green', 'BUY': 'lightgreen', 'NEUTRAL': 'gray', 
                     'SELL': 'lightcoral', 'STRONG_SELL': 'red'}
            
            signal_counts.plot(kind='bar', ax=ax, color=[colors.get(s, 'gray') for s in signal_counts.index])
            ax.set_title('Signal Distribution')
            ax.set_ylabel('Count')
            ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            logger.error(f"Error plotting signal distribution: {e}")
    
    def plot_top_opportunities(self, analysis_results: Dict, ax):
        """Plot top opportunities"""
        try:
            opportunities = self.identify_top_opportunities(analysis_results)
            
            if not opportunities:
                ax.text(0.5, 0.5, 'No opportunities', ha='center', va='center')
                return
            
            symbols = [opp['symbol'] for opp in opportunities[:10]]
            scores = [opp['score'] for opp in opportunities[:10]]
            
            colors = ['green' if s > 0 else 'red' for s in scores]
            
            ax.barh(symbols, scores, color=colors)
            ax.set_title('Top 10 Opportunities')
            ax.set_xlabel('Opportunity Score')
            
        except Exception as e:
            logger.error(f"Error plotting top opportunities: {e}")
    
    def plot_risk_heatmap(self, analysis_results: Dict, ax):
        """Plot risk heatmap"""
        try:
            symbols = []
            risk_data = []
            
            for symbol, analysis in analysis_results.items():
                symbols.append(symbol)
                risk = analysis.get('risk', {})
                risk_data.append([
                    risk.get('volatility_risk', 0),
                    risk.get('drawdown_risk', 0),
                    risk.get('gap_risk', 0),
                    risk.get('liquidity_risk', 0)
                ])
            
            if not symbols:
                ax.text(0.5, 0.5, 'No risk data', ha='center', va='center')
                return
            
            risk_df = pd.DataFrame(risk_data, index=symbols, 
                                 columns=['Volatility', 'Drawdown', 'Gap', 'Liquidity'])
            
            sns.heatmap(risk_df, annot=True, fmt='.1f', cmap='Reds', ax=ax)
            ax.set_title('Risk Heatmap')
            
        except Exception as e:
            logger.error(f"Error plotting risk heatmap: {e}")
    
    def plot_momentum_scatter(self, analysis_results: Dict, ax):
        """Plot momentum scatter plot"""
        try:
            symbols = []
            momentum_scores = []
            confidence_scores = []
            
            for symbol, analysis in analysis_results.items():
                symbols.append(symbol)
                momentum = analysis.get('momentum', {})
                momentum_scores.append(momentum.get('composite_score', 0))
                confidence_scores.append(analysis.get('confidence_score', 0))
            
            if not symbols:
                ax.text(0.5, 0.5, 'No momentum data', ha='center', va='center')
                return
            
            scatter = ax.scatter(momentum_scores, confidence_scores, 
                               c=momentum_scores, cmap='RdYlGn', s=100, alpha=0.7)
            
            for i, symbol in enumerate(symbols):
                ax.annotate(symbol, (momentum_scores[i], confidence_scores[i]), 
                          xytext=(5, 5), textcoords='offset points', fontsize=8)
            
            ax.set_xlabel('Momentum Score')
            ax.set_ylabel('Confidence Score')
            ax.set_title('Momentum vs Confidence')
            plt.colorbar(scatter, ax=ax)
            
        except Exception as e:
            logger.error(f"Error plotting momentum scatter: {e}")
    
    def plot_pattern_frequency(self, analysis_results: Dict, ax):
        """Plot pattern frequency"""
        try:
            pattern_counts = {}
            
            for analysis in analysis_results.values():
                patterns = analysis.get('patterns', {}).get('patterns', [])
                for pattern in patterns:
                    pattern_type = pattern.get('name', 'Unknown')
                    pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
            
            if not pattern_counts:
                ax.text(0.5, 0.5, 'No patterns found', ha='center', va='center')
                return
            
            patterns = list(pattern_counts.keys())
            counts = list(pattern_counts.values())
            
            ax.bar(patterns, counts, color='skyblue')
            ax.set_title('Pattern Frequency')
            ax.set_ylabel('Count')
            ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            logger.error(f"Error plotting pattern frequency: {e}")
    
    def plot_sentiment_timeline(self, analysis_results: Dict, ax):
        """Plot sentiment timeline"""
        try:
            # This would require historical sentiment data
            # For now, show current sentiment distribution
            sentiments = []
            
            for analysis in analysis_results.values():
                sentiment = analysis.get('sentiment', {})
                if sentiment.get('status') == 'success':
                    aggregation = sentiment.get('aggregation', {})
                    sentiments.append(aggregation.get('overall_score', 0))
            
            if not sentiments:
                ax.text(0.5, 0.5, 'No sentiment data', ha='center', va='center')
                return
            
            ax.hist(sentiments, bins=10, color='lightblue', alpha=0.7)
            ax.set_title('Sentiment Score Distribution')
            ax.set_xlabel('Sentiment Score')
            ax.set_ylabel('Frequency')
            
        except Exception as e:
            logger.error(f"Error plotting sentiment timeline: {e}")
    
    def plot_market_regime_distribution(self, analysis_results: Dict, ax):
        """Plot market regime distribution"""
        try:
            regimes = []
            
            for analysis in analysis_results.values():
                market_structure = analysis.get('market_structure', {})
                regimes.append(market_structure.get('market_regime', 'unknown'))
            
            if not regimes:
                ax.text(0.5, 0.5, 'No regime data', ha='center', va='center')
                return
            
            regime_counts = pd.Series(regimes).value_counts()
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(regime_counts)))
            ax.pie(regime_counts.values, labels=regime_counts.index, autopct='%1.1f%%', 
                  colors=colors, startangle=90)
            ax.set_title('Market Regime Distribution')
            
        except Exception as e:
            logger.error(f"Error plotting market regime distribution: {e}")
    
    def plot_confidence_vs_signal(self, analysis_results: Dict, ax):
        """Plot confidence vs signal strength"""
        try:
            signals = []
            confidences = []
            
            for analysis in analysis_results.values():
                trading_signal = analysis.get('trading_signal', {})
                signal_strength = {'STRONG_BUY': 2, 'BUY': 1, 'NEUTRAL': 0, 'SELL': -1, 'STRONG_SELL': -2}
                signal = signal_strength.get(trading_signal.get('signal', 'NEUTRAL'), 0)
                confidence = analysis.get('confidence_score', 0)
                
                signals.append(signal)
                confidences.append(confidence)
            
            if not signals:
                ax.text(0.5, 0.5, 'No signal data', ha='center', va='center')
                return
            
            ax.scatter(signals, confidences, alpha=0.6)
            ax.set_xlabel('Signal Strength')
            ax.set_ylabel('Confidence Score')
            ax.set_title('Confidence vs Signal Strength')
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logger.error(f"Error plotting confidence vs signal: {e}")
    
    def plot_performance_metrics(self, analysis_results: Dict, ax):
        """Plot performance metrics"""
        try:
            # This would require historical performance data
            # For now, show basic statistics
            total_symbols = len(analysis_results)
            
            if total_symbols == 0:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center')
                return
            
            # Calculate basic metrics
            signals = [analysis.get('trading_signal', {}).get('signal', 'NEUTRAL') 
                      for analysis in analysis_results.values()]
            
            strong_signals = sum(1 for s in signals if 'STRONG' in s)
            regular_signals = sum(1 for s in signals if s in ['BUY', 'SELL'])
            
            metrics = ['Strong Signals', 'Regular Signals', 'Neutral Signals']
            values = [strong_signals, regular_signals, total_symbols - strong_signals - regular_signals]
            
            ax.bar(metrics, values, color=['darkgreen', 'green', 'gray'])
            ax.set_title('Signal Quality Distribution')
            ax.set_ylabel('Count')
            
        except Exception as e:
            logger.error(f"Error plotting performance metrics: {e}")
    
    async def run_analysis_cycle(self, symbols: List[str] = None):
        """Run complete analysis cycle"""
        try:
            # Default symbols if not provided
            if symbols is None:
                symbols = [
                    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
                    'BTCUSD', 'ETHUSD', 'XAUUSD', 'XAGUSD'
                ]
            
            logger.info(f"Starting analysis cycle for {len(symbols)} symbols...")
            
            # Perform comprehensive analysis
            analysis_results = await self.perform_comprehensive_analysis(symbols)
            
            if not analysis_results:
                logger.error("Analysis produced no results")
                return
            
            # Store results
            self.analysis_results = analysis_results
            
            # Generate reports
            await self.generate_analysis_report(analysis_results)
            
            # Create visualization
            viz_path = f"reports/analysis_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.create_visualization(analysis_results, viz_path)
            
            logger.info("Analysis cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in analysis cycle: {e}")
    
    async def generate_analysis_report(self, analysis_results: Dict):
        """Generate detailed analysis report"""
        try:
            report = {
                'timestamp': datetime.now(),
                'market_overview': analysis_results.get('market_overview', {}),
                'top_opportunities': analysis_results.get('top_opportunities', []),
                'risk_assessment': analysis_results.get('risk_assessment', {}),
                'symbol_details': {}
            }
            
            # Add detailed symbol analysis
            for symbol, analysis in analysis_results.get('symbols', {}).items():
                report['symbol_details'][symbol] = {
                    'signal': analysis.get('trading_signal', {}).get('signal', 'NEUTRAL'),
                    'confidence': analysis.get('confidence_score', 0),
                    'momentum_score': analysis.get('momentum', {}).get('composite_score', 0),
                    'risk_score': analysis.get('risk', {}).get('overall_risk_score', 50),
                    'market_regime': analysis.get('market_structure', {}).get('market_regime', 'unknown')
                }
            
            # Save report
            report_path = Path('reports/advanced_analysis')
            report_path.mkdir(exist_ok=True)
            
            report_file = report_path / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, default=str, indent=2)
            
            logger.info(f"Analysis report saved to {report_file}")
            
            # Generate summary
            self.print_analysis_summary(report)
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {e}")
    
    def print_analysis_summary(self, report: Dict):
        """Print analysis summary"""
        try:
            logger.info("=== Advanced Analysis Summary ===")
            
            market_overview = report.get('market_overview', {})
            logger.info(f"Market Sentiment: {market_overview.get('market_sentiment', 'unknown')}")
            logger.info(f"Total Symbols Analyzed: {market_overview.get('total_symbols', 0)}")
            logger.info(f"Average Confidence: {market_overview.get('average_confidence', 0):.2f}")
            
            top_opportunities = report.get('top_opportunities', [])
            logger.info(f"\nTop 5 Opportunities:")
            for i, opp in enumerate(top_opportunities[:5], 1):
                logger.info(f"{i}. {opp['symbol']}: {opp['signal']} (Score: {opp['score']:.2f}, Confidence: {opp['confidence']:.2f})")
            
            risk_assessment = report.get('risk_assessment', {})
            logger.info(f"\nRisk Assessment:")
            logger.info(f"Average Risk: {risk_assessment.get('average_risk', 0):.1f}/100")
            logger.info(f"Risk Level: {risk_assessment.get('risk_level', 'unknown')}")
            logger.info(f"Correlation Risk: {risk_assessment.get('correlation_risk', 0):.2f}")
            
        except Exception as e:
            logger.error(f"Error printing analysis summary: {e}")
    
    async def run(self):
        """Main analysis loop"""
        logger.info("Starting advanced analysis bot...")
        
        if not await self.initialize():
            logger.error("Failed to initialize advanced analysis system")
            return
        
        try:
            # Run analysis cycle
            await self.run_analysis_cycle()
            
            # Schedule periodic analysis
            analysis_interval = self.config.get('advanced_analysis.interval_hours', 6)
            logger.info(f"Analysis will run every {analysis_interval} hours")
            
            while True:
                await asyncio.sleep(analysis_interval * 3600)  # Convert hours to seconds
                await self.run_analysis_cycle()
                
        except KeyboardInterrupt:
            logger.info("Advanced analysis bot stopped by user")
        except Exception as e:
            logger.error(f"Error in main analysis loop: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown analysis system"""
        logger.info("Shutting down advanced analysis system...")
        
        try:
            # Disconnect from MT5
            await self.mt5_integration.disconnect()
            logger.info("Disconnected from MetaTrader 5")
            
            logger.info("Advanced analysis system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main entry point"""
    # Create reports directory
    Path('reports').mkdir(exist_ok=True)
    
    # Create analysis bot
    bot = AdvancedAnalysisBot()
    
    # Run analysis bot
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script error: {e}")