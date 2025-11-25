"""
Advanced Momentum Analysis Module
Provides sophisticated momentum indicators and analysis for trading decisions
"""

import numpy as np
import pandas as pd
import talib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MomentumSignal:
    """Represents a momentum trading signal"""
    symbol: str
    timestamp: datetime
    signal_type: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # 0.0 to 1.0
    timeframe: str
    indicators: Dict[str, float]
    confidence: float
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    time_horizon: str = "medium"  # 'short', 'medium', 'long'
    risk_level: str = "medium"  # 'low', 'medium', 'high'

class AdvancedMomentumAnalyzer:
    """
    Advanced momentum analysis with multiple indicators and ML enhancement
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self.get_default_config()
        self.scaler = StandardScaler()
        self.ml_model = None
        self.train_ml_model()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for momentum analysis"""
        return {
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'stochastic_k': 14,
            'stochastic_d': 3,
            'stochastic_smooth': 3,
            'adx_period': 14,
            'adx_strong': 25,
            'momentum_period': 10,
            'roc_period': 12,
            'cci_period': 20,
            'williams_r_period': 14,
            'ultimate_oscillator_periods': [7, 14, 28],
            'volume_mfi_period': 14,
            'price_rate_of_change_period': 12,
            'relative_strength_period': 14,
            'money_flow_index_period': 14,
            'commodity_channel_index_period': 20,
            'momentum_threshold': 0.3,
            'confidence_threshold': 0.6,
            'timeframes': ['1h', '4h', '1d', '1w'],
            'ml_lookback_period': 50,
            'ml_prediction_horizon': 5
        }
    
    def train_ml_model(self):
        """Train machine learning model for momentum prediction"""
        try:
            # Create synthetic training data for demonstration
            # In real implementation, would use historical data
            np.random.seed(42)
            n_samples = 1000
            
            # Generate synthetic features
            features = np.random.randn(n_samples, 20)
            features = self.scaler.fit_transform(features)
            
            # Generate synthetic targets (momentum direction and strength)
            targets = np.random.choice([-1, 0, 1], n_samples, p=[0.3, 0.4, 0.3])
            
            # Train Random Forest model
            self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.ml_model.fit(features, targets)
            
            logger.info("ML momentum model trained successfully")
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            self.ml_model = None
    
    def calculate_rsi_momentum(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate RSI-based momentum indicators"""
        try:
            rsi = talib.RSI(prices.values, timeperiod=self.config['rsi_period'])
            current_rsi = rsi[-1]
            
            # Calculate RSI momentum
            rsi_momentum = 0.0
            if current_rsi > self.config['rsi_overbought']:
                rsi_momentum = (current_rsi - self.config['rsi_overbought']) / (100 - self.config['rsi_overbought'])
            elif current_rsi < self.config['rsi_oversold']:
                rsi_momentum = (self.config['rsi_oversold'] - current_rsi) / self.config['rsi_oversold']
            
            # Calculate RSI divergence
            rsi_divergence = self.calculate_rsi_divergence(prices, rsi)
            
            return {
                'rsi': current_rsi,
                'rsi_momentum': rsi_momentum,
                'rsi_signal': 'overbought' if current_rsi > self.config['rsi_overbought'] else 
                             'oversold' if current_rsi < self.config['rsi_oversold'] else 'neutral',
                'rsi_divergence': rsi_divergence,
                'rsi_strength': min(abs(current_rsi - 50) / 50, 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error calculating RSI momentum: {e}")
            return {'rsi': 50, 'rsi_momentum': 0, 'rsi_signal': 'neutral', 'rsi_divergence': 0, 'rsi_strength': 0}
    
    def calculate_macd_momentum(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate MACD-based momentum indicators"""
        try:
            macd, signal, histogram = talib.MACD(
                prices.values, 
                fastperiod=self.config['macd_fast'],
                slowperiod=self.config['macd_slow'],
                signalperiod=self.config['macd_signal']
            )
            
            current_macd = macd[-1]
            current_signal = signal[-1]
            current_histogram = histogram[-1]
            
            # MACD signal
            macd_signal = 0
            if current_macd > current_signal and current_histogram > 0:
                macd_signal = 1
            elif current_macd < current_signal and current_histogram < 0:
                macd_signal = -1
            
            # MACD momentum strength
            histogram_range = max(abs(histogram)) if len(histogram) > 0 else 1
            macd_strength = abs(current_histogram) / histogram_range if histogram_range > 0 else 0
            
            return {
                'macd': current_macd,
                'macd_signal': current_signal,
                'macd_histogram': current_histogram,
                'macd_signal_direction': macd_signal,
                'macd_strength': macd_strength,
                'macd_trend': 'bullish' if macd_signal > 0 else 'bearish' if macd_signal < 0 else 'neutral'
            }
            
        except Exception as e:
            logger.error(f"Error calculating MACD momentum: {e}")
            return {'macd': 0, 'macd_signal': 0, 'macd_histogram': 0, 'macd_signal_direction': 0, 'macd_strength': 0, 'macd_trend': 'neutral'}
    
    def calculate_stochastic_momentum(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, float]:
        """Calculate Stochastic-based momentum indicators"""
        try:
            k, d = talib.STOCH(
                high.values, low.values, close.values,
                fastk_period=self.config['stochastic_k'],
                slowk_period=self.config['stochastic_d'],
                slowd_period=self.config['stochastic_smooth']
            )
            
            current_k = k[-1]
            current_d = d[-1]
            
            # Stochastic signal
            stochastic_signal = 0
            if current_k > 80 and current_k > current_d:
                stochastic_signal = -1  # Overbought
            elif current_k < 20 and current_k < current_d:
                stochastic_signal = 1   # Oversold
            
            return {
                'stochastic_k': current_k,
                'stochastic_d': current_d,
                'stochastic_signal': stochastic_signal,
                'stochastic_overbought': current_k > 80,
                'stochastic_oversold': current_k < 20,
                'stochastic_strength': abs(current_k - 50) / 50
            }
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic momentum: {e}")
            return {'stochastic_k': 50, 'stochastic_d': 50, 'stochastic_signal': 0, 'stochastic_overbought': False, 'stochastic_oversold': False, 'stochastic_strength': 0}
    
    def calculate_adx_momentum(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, float]:
        """Calculate ADX-based momentum indicators"""
        try:
            adx = talib.ADX(high.values, low.values, close.values, timeperiod=self.config['adx_period'])
            plus_di = talib.PLUS_DI(high.values, low.values, close.values, timeperiod=self.config['adx_period'])
            minus_di = talib.MINUS_DI(high.values, low.values, close.values, timeperiod=self.config['adx_period'])
            
            current_adx = adx[-1]
            current_plus_di = plus_di[-1]
            current_minus_di = minus_di[-1]
            
            # ADX signal
            adx_signal = 0
            if current_adx > self.config['adx_strong']:
                if current_plus_di > current_minus_di:
                    adx_signal = 1  # Strong uptrend
                elif current_minus_di > current_plus_di:
                    adx_signal = -1  # Strong downtrend
            
            return {
                'adx': current_adx,
                'plus_di': current_plus_di,
                'minus_di': current_minus_di,
                'adx_signal': adx_signal,
                'adx_strength': min(current_adx / 50, 1.0),  # Normalize to 0-1
                'adx_trend': 'strong_trend' if current_adx > self.config['adx_strong'] else 'weak_trend'
            }
            
        except Exception as e:
            logger.error(f"Error calculating ADX momentum: {e}")
            return {'adx': 0, 'plus_di': 0, 'minus_di': 0, 'adx_signal': 0, 'adx_strength': 0, 'adx_trend': 'weak_trend'}
    
    def calculate_volume_momentum(self, volume: pd.Series, close: pd.Series) -> Dict[str, float]:
        """Calculate volume-based momentum indicators"""
        try:
            # Volume Rate of Change
            volume_roc = talib.ROC(volume.values, timeperiod=self.config['roc_period'])
            
            # Money Flow Index
            mfi = talib.MFI(
                high=close.values, low=close.values, close=close.values, 
                volume=volume.values, timeperiod=self.config['volume_mfi_period']
            )
            
            # On Balance Volume
            obv = talib.OBV(close.values, volume.values)
            
            current_volume_roc = volume_roc[-1] if len(volume_roc) > 0 else 0
            current_mfi = mfi[-1] if len(mfi) > 0 else 50
            current_obv = obv[-1] if len(obv) > 0 else 0
            
            # Volume momentum signal
            volume_signal = 0
            if current_mfi > 80 and current_volume_roc > 0:
                volume_signal = 1  # Strong buying pressure
            elif current_mfi < 20 and current_volume_roc < 0:
                volume_signal = -1  # Strong selling pressure
            
            return {
                'volume_roc': current_volume_roc,
                'money_flow_index': current_mfi,
                'on_balance_volume': current_obv,
                'volume_signal': volume_signal,
                'volume_strength': abs(current_mfi - 50) / 50
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume momentum: {e}")
            return {'volume_roc': 0, 'money_flow_index': 50, 'on_balance_volume': 0, 'volume_signal': 0, 'volume_strength': 0}
    
    def calculate_ultimate_oscillator_momentum(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, float]:
        """Calculate Ultimate Oscillator momentum"""
        try:
            periods = self.config['ultimate_oscillator_periods']
            ultimate = talib.ULTOSC(
                high.values, low.values, close.values,
                timeperiod1=periods[0], timeperiod2=periods[1], timeperiod3=periods[2]
            )
            
            current_ultimate = ultimate[-1] if len(ultimate) > 0 else 50
            
            # Ultimate oscillator signal
            ultimate_signal = 0
            if current_ultimate > 70:
                ultimate_signal = -1  # Overbought
            elif current_ultimate < 30:
                ultimate_signal = 1   # Oversold
            
            return {
                'ultimate_oscillator': current_ultimate,
                'ultimate_signal': ultimate_signal,
                'ultimate_strength': abs(current_ultimate - 50) / 50
            }
            
        except Exception as e:
            logger.error(f"Error calculating Ultimate Oscillator momentum: {e}")
            return {'ultimate_oscillator': 50, 'ultimate_signal': 0, 'ultimate_strength': 0}
    
    def calculate_williams_r_momentum(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Dict[str, float]:
        """Calculate Williams %R momentum"""
        try:
            williams_r = talib.WILLR(
                high.values, low.values, close.values,
                timeperiod=self.config['williams_r_period']
            )
            
            current_williams_r = williams_r[-1] if len(williams_r) > 0 else -50
            
            # Williams %R signal
            williams_signal = 0
            if current_williams_r > -20:
                williams_signal = -1  # Overbought
            elif current_williams_r < -80:
                williams_signal = 1   # Oversold
            
            return {
                'williams_r': current_williams_r,
                'williams_signal': williams_signal,
                'williams_strength': abs(current_williams_r + 50) / 50
            }
            
        except Exception as e:
            logger.error(f"Error calculating Williams %R momentum: {e}")
            return {'williams_r': -50, 'williams_signal': 0, 'williams_strength': 0}
    
    def calculate_rsi_divergence(self, prices: pd.Series, rsi: np.ndarray) -> float:
        """Calculate RSI divergence"""
        try:
            # Simple divergence detection
            if len(prices) < 20 or len(rsi) < 20:
                return 0.0
            
            # Check for bullish divergence (price lower low, RSI higher low)
            price_trend = np.polyfit(range(10), prices[-10:], 1)[0]
            rsi_trend = np.polyfit(range(10), rsi[-10:], 1)[0]
            
            if price_trend < -0.1 and rsi_trend > 0.1:
                return 1.0  # Bullish divergence
            elif price_trend > 0.1 and rsi_trend < -0.1:
                return -1.0  # Bearish divergence
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating RSI divergence: {e}")
            return 0.0
    
    def calculate_ml_momentum_score(self, indicators: Dict[str, float]) -> float:
        """Calculate ML-based momentum score"""
        try:
            if self.ml_model is None:
                return 0.0
            
            # Prepare features from indicators
            feature_values = list(indicators.values())
            if len(feature_values) < 20:
                # Pad with zeros if needed
                feature_values.extend([0.0] * (20 - len(feature_values)))
            
            features = np.array(feature_values[:20]).reshape(1, -1)
            features_scaled = self.scaler.transform(features)
            
            # Get prediction
            prediction = self.ml_model.predict(features_scaled)[0]
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Error calculating ML momentum score: {e}")
            return 0.0
    
    def calculate_composite_momentum_score(self, indicators: Dict[str, float]) -> float:
        """Calculate composite momentum score from all indicators"""
        try:
            # Weight different indicators
            weights = {
                'rsi_momentum': 0.15,
                'macd_signal_direction': 0.15,
                'adx_signal': 0.10,
                'stochastic_signal': 0.10,
                'volume_signal': 0.10,
                'ultimate_signal': 0.10,
                'williams_signal': 0.10,
                'rsi_divergence': 0.10,
                'ml_momentum_score': 0.10
            }
            
            composite_score = 0.0
            total_weight = 0.0
            
            for indicator, weight in weights.items():
                if indicator in indicators:
                    composite_score += indicators[indicator] * weight
                    total_weight += weight
            
            # Normalize to -1 to 1 range
            if total_weight > 0:
                composite_score /= total_weight
            
            return max(-1.0, min(1.0, composite_score))
            
        except Exception as e:
            logger.error(f"Error calculating composite momentum score: {e}")
            return 0.0
    
    def analyze_momentum(self, data: Dict[str, pd.Series], symbol: str, timeframe: str = '1h') -> MomentumSignal:
        """
        Perform comprehensive momentum analysis
        
        Args:
            data: Dictionary with 'open', 'high', 'low', 'close', 'volume' series
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            MomentumSignal object with analysis results
        """
        try:
            # Extract price data
            high = data['high']
            low = data['low']
            close = data['close']
            volume = data.get('volume', pd.Series([1.0] * len(close)))
            
            # Calculate all momentum indicators
            indicators = {}
            
            # RSI momentum
            rsi_data = self.calculate_rsi_momentum(close)
            indicators.update(rsi_data)
            
            # MACD momentum
            macd_data = self.calculate_macd_momentum(close)
            indicators.update(macd_data)
            
            # Stochastic momentum
            stochastic_data = self.calculate_stochastic_momentum(high, low, close)
            indicators.update(stochastic_data)
            
            # ADX momentum
            adx_data = self.calculate_adx_momentum(high, low, close)
            indicators.update(adx_data)
            
            # Volume momentum
            volume_data = self.calculate_volume_momentum(volume, close)
            indicators.update(volume_data)
            
            # Ultimate Oscillator
            ultimate_data = self.calculate_ultimate_oscillator_momentum(high, low, close)
            indicators.update(ultimate_data)
            
            # Williams %R
            williams_data = self.calculate_williams_r_momentum(high, low, close)
            indicators.update(williams_data)
            
            # ML momentum score
            ml_score = self.calculate_ml_momentum_score(indicators)
            indicators['ml_momentum_score'] = ml_score
            
            # Calculate composite momentum score
            composite_score = self.calculate_composite_momentum_score(indicators)
            indicators['composite_momentum'] = composite_score
            
            # Determine signal type and strength
            signal_type = 'neutral'
            strength = abs(composite_score)
            
            if composite_score > self.config['momentum_threshold']:
                signal_type = 'bullish'
            elif composite_score < -self.config['momentum_threshold']:
                signal_type = 'bearish'
            
            # Calculate confidence based on multiple factors
            confidence = self.calculate_confidence(indicators, strength)
            
            # Calculate price targets and stop loss
            price_target, stop_loss = self.calculate_price_targets(close, signal_type, strength)
            
            # Determine time horizon and risk level
            time_horizon = self.determine_time_horizon(indicators)
            risk_level = self.determine_risk_level(indicators, strength)
            
            return MomentumSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type=signal_type,
                strength=strength,
                timeframe=timeframe,
                indicators=indicators,
                confidence=confidence,
                price_target=price_target,
                stop_loss=stop_loss,
                time_horizon=time_horizon,
                risk_level=risk_level
            )
            
        except Exception as e:
            logger.error(f"Error analyzing momentum for {symbol}: {e}")
            return MomentumSignal(
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type='neutral',
                strength=0.0,
                timeframe=timeframe,
                indicators={},
                confidence=0.0,
                time_horizon='medium',
                risk_level='medium'
            )
    
    def calculate_confidence(self, indicators: Dict[str, float], strength: float) -> float:
        """Calculate confidence level for momentum signal"""
        try:
            confidence_factors = []
            
            # RSI confidence
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                rsi_confidence = abs(rsi - 50) / 50
                confidence_factors.append(rsi_confidence)
            
            # MACD confidence
            if 'macd_strength' in indicators:
                confidence_factors.append(indicators['macd_strength'])
            
            # ADX confidence
            if 'adx_strength' in indicators:
                confidence_factors.append(indicators['adx_strength'])
            
            # Volume confidence
            if 'volume_strength' in indicators:
                confidence_factors.append(indicators['volume_strength'])
            
            # ML confidence
            if 'ml_momentum_score' in indicators:
                ml_confidence = abs(indicators['ml_momentum_score'])
                confidence_factors.append(ml_confidence)
            
            # Calculate average confidence
            if confidence_factors:
                avg_confidence = np.mean(confidence_factors)
                # Weight with signal strength
                final_confidence = (avg_confidence * 0.7 + strength * 0.3)
                return min(1.0, max(0.0, final_confidence))
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def calculate_price_targets(self, close: pd.Series, signal_type: str, strength: float) -> Tuple[Optional[float], Optional[float]]:
        """Calculate price targets and stop loss levels"""
        try:
            current_price = close.iloc[-1]
            volatility = np.std(close.tail(20)) / np.mean(close.tail(20))
            
            # Calculate target based on signal strength and volatility
            target_multiplier = strength * volatility * 2
            
            if signal_type == 'bullish':
                price_target = current_price * (1 + target_multiplier)
                stop_loss = current_price * (1 - target_multiplier * 0.5)
            elif signal_type == 'bearish':
                price_target = current_price * (1 - target_multiplier)
                stop_loss = current_price * (1 + target_multiplier * 0.5)
            else:
                price_target = None
                stop_loss = None
            
            return price_target, stop_loss
            
        except Exception as e:
            logger.error(f"Error calculating price targets: {e}")
            return None, None
    
    def determine_time_horizon(self, indicators: Dict[str, float]) -> str:
        """Determine appropriate time horizon for signal"""
        try:
            # Use ADX to determine trend strength and time horizon
            if 'adx' in indicators and indicators['adx'] > 30:
                return 'long'
            elif 'adx' in indicators and indicators['adx'] < 20:
                return 'short'
            else:
                return 'medium'
                
        except Exception as e:
            logger.error(f"Error determining time horizon: {e}")
            return 'medium'
    
    def determine_risk_level(self, indicators: Dict[str, float], strength: float) -> str:
        """Determine risk level for signal"""
        try:
            risk_factors = []
            
            # Volatility-based risk
            if strength > 0.7:
                risk_factors.append('high')
            elif strength < 0.3:
                risk_factors.append('low')
            else:
                risk_factors.append('medium')
            
            # ADX-based risk
            if 'adx' in indicators:
                if indicators['adx'] < 20:
                    risk_factors.append('high')  # Weak trend
                elif indicators['adx'] > 40:
                    risk_factors.append('low')   # Strong trend
            
            # Return most common risk level
            if risk_factors:
                return max(set(risk_factors), key=risk_factors.count)
            
            return 'medium'
            
        except Exception as e:
            logger.error(f"Error determining risk level: {e}")
            return 'medium'
    
    def scan_momentum_opportunities(self, market_data: Dict[str, Dict[str, pd.Series]], 
                                   min_confidence: float = 0.6) -> List[MomentumSignal]:
        """
        Scan multiple symbols for momentum trading opportunities
        
        Args:
            market_data: Dictionary of symbol -> OHLCV data
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of momentum signals meeting criteria
        """
        opportunities = []
        
        try:
            for symbol, data in market_data.items():
                # Analyze momentum for each symbol
                signal = self.analyze_momentum(data, symbol)
                
                # Filter by confidence and signal strength
                if signal.confidence >= min_confidence and signal.strength >= self.config['momentum_threshold']:
                    opportunities.append(signal)
            
            # Sort by confidence and strength
            opportunities.sort(key=lambda x: (x.confidence, x.strength), reverse=True)
            
            logger.info(f"Found {len(opportunities)} momentum opportunities with confidence >= {min_confidence}")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scanning momentum opportunities: {e}")
            return []
    
    def get_momentum_heatmap(self, symbols: List[str], timeframes: List[str] = None) -> Dict[str, Dict[str, float]]:
        """
        Generate momentum heatmap for multiple symbols and timeframes
        
        Args:
            symbols: List of trading symbols
            timeframes: List of timeframes (default: ['1h', '4h', '1d'])
            
        Returns:
            Nested dictionary: symbol -> timeframe -> momentum_score
        """
        if timeframes is None:
            timeframes = ['1h', '4h', '1d']
        
        heatmap = {}
        
        try:
            # This is a placeholder implementation
            # In real usage, would fetch actual market data for each symbol/timeframe
            for symbol in symbols:
                heatmap[symbol] = {}
                for timeframe in timeframes:
                    # Generate synthetic momentum score for demonstration
                    momentum_score = np.random.uniform(-1.0, 1.0)
                    heatmap[symbol][timeframe] = momentum_score
            
            return heatmap
            
        except Exception as e:
            logger.error(f"Error generating momentum heatmap: {e}")
            return {}

# Example usage and testing
def example_usage():
    """
    Example usage of the Advanced Momentum Analyzer
    """
    
    # Create analyzer
    analyzer = AdvancedMomentumAnalyzer()
    
    # Generate sample market data
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
    
    # Generate synthetic OHLCV data
    base_price = 100.0
    prices = [base_price]
    
    for i in range(1, 100):
        change = np.random.normal(0, 0.02)  # 2% daily volatility
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    prices = pd.Series(prices, index=dates)
    
    # Create OHLCV data
    high = prices * (1 + np.abs(np.random.normal(0, 0.01, 100)))
    low = prices * (1 - np.abs(np.random.normal(0, 0.01, 100)))
    close = prices
    open_prices = prices.shift(1).fillna(prices.iloc[0])
    volume = pd.Series(np.random.randint(1000, 10000, 100), index=dates)
    
    market_data = {
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }
    
    # Analyze momentum
    print("Analyzing momentum for sample data...")
    signal = analyzer.analyze_momentum(market_data, "BTCUSDT", "1h")
    
    print(f"\nMomentum Analysis Results:")
    print(f"Symbol: {signal.symbol}")
    print(f"Signal Type: {signal.signal_type}")
    print(f"Strength: {signal.strength:.3f}")
    print(f"Confidence: {signal.confidence:.3f}")
    print(f"Time Horizon: {signal.time_horizon}")
    print(f"Risk Level: {signal.risk_level}")
    
    if signal.price_target:
        print(f"Price Target: {signal.price_target:.2f}")
    if signal.stop_loss:
        print(f"Stop Loss: {signal.stop_loss:.2f}")
    
    print(f"\nKey Indicators:")
    for key, value in list(signal.indicators.items())[:10]:  # Show first 10 indicators
        print(f"  {key}: {value:.3f}")
    
    # Scan multiple symbols
    print("\n" + "="*50)
    print("Scanning momentum opportunities...")
    
    # Create sample market data for multiple symbols
    market_data_multi = {}
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT"]
    
    for symbol in symbols:
        # Generate different price patterns for each symbol
        base_price = np.random.uniform(50, 50000)
        prices = [base_price]
        
        for i in range(1, 100):
            trend = np.random.uniform(-0.001, 0.001)  # Different trends
            noise = np.random.normal(0, 0.02)
            new_price = prices[-1] * (1 + trend + noise)
            prices.append(new_price)
        
        prices_series = pd.Series(prices, index=dates)
        
        market_data_multi[symbol] = {
            'open': prices_series.shift(1).fillna(prices_series.iloc[0]),
            'high': prices_series * (1 + np.abs(np.random.normal(0, 0.01, 100))),
            'low': prices_series * (1 - np.abs(np.random.normal(0, 0.01, 100))),
            'close': prices_series,
            'volume': pd.Series(np.random.randint(1000, 10000, 100), index=dates)
        }
    
    # Scan for opportunities
    opportunities = analyzer.scan_momentum_opportunities(market_data_multi, min_confidence=0.5)
    
    print(f"\nFound {len(opportunities)} momentum opportunities:")
    for i, opp in enumerate(opportunities[:5]):  # Show top 5
        print(f"  {i+1}. {opp.symbol}: {opp.signal_type} (strength: {opp.strength:.3f}, confidence: {opp.confidence:.3f})")
    
    # Generate momentum heatmap
    print("\n" + "="*50)
    print("Generating momentum heatmap...")
    
    heatmap = analyzer.get_momentum_heatmap(symbols)
    
    print("\nMomentum Heatmap:")
    print("Symbol\t\t1h\t\t4h\t\t1d")
    print("-" * 50)
    for symbol, timeframes in heatmap.items():
        print(f"{symbol:<12}\t{timeframes.get('1h', 0):.3f}\t{timeframes.get('4h', 0):.3f}\t{timeframes.get('1d', 0):.3f}")

if __name__ == "__main__":
    example_usage()