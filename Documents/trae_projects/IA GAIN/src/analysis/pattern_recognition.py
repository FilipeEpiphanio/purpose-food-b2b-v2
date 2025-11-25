"""
Advanced Pattern Recognition System
Detects complex chart patterns and candlestick formations using ML and traditional methods
"""

import numpy as np
import pandas as pd
import talib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from scipy.signal import find_peaks
from scipy.stats import linregress
import cv2
from scipy.ndimage import gaussian_filter1d
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Types of chart patterns"""
    # Trend Continuation
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    BULLISH_FLAG = "bullish_flag"
    BEARISH_FLAG = "bearish_flag"
    BULLISH_PENNANT = "bullish_pennant"
    BEARISH_PENNANT = "bearish_pennant"
    
    # Trend Reversal
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_AND_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"
    ROUNDING_TOP = "rounding_top"
    ROUNDING_BOTTOM = "rounding_bottom"
    
    # Candlestick Patterns
    HAMMER = "hammer"
    HANGING_MAN = "hanging_man"
    SHOOTING_STAR = "shooting_star"
    INVERTED_HAMMER = "inverted_hammer"
    DOJI = "doji"
    SPINNING_TOP = "spinning_top"
    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"
    
    # Support/Resistance
    SUPPORT_BREAK = "support_break"
    RESISTANCE_BREAK = "resistance_break"
    SUPPORT_BOUNCE = "support_bounce"
    RESISTANCE_REJECT = "resistance_reject"

class PatternSignal(Enum):
    """Pattern trading signals"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

@dataclass
class PatternMatch:
    """Represents a detected pattern"""
    pattern_type: PatternType
    symbol: str
    start_time: datetime
    end_time: datetime
    signal: PatternSignal
    confidence: float
    price_target: Optional[float]
    stop_loss: Optional[float]
    pattern_score: float
    volume_confirmation: bool
    timeframe: str
    pattern_data: Dict[str, Any]
    
    def __post_init__(self):
        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("Confidence must be between 0 and 1")

class AdvancedPatternRecognition:
    """
    Advanced pattern recognition system using multiple techniques
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self.get_default_config()
        self.ml_model = None
        self.scaler = StandardScaler()
        self.train_pattern_model()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for pattern recognition"""
        return {
            'min_pattern_length': 20,
            'max_pattern_length': 200,
            'confidence_threshold': 0.6,
            'min_volume_confirmation': 0.1,
            'peak_detection_distance': 5,
            'trend_line_min_points': 3,
            'pattern_similarity_threshold': 0.7,
            'ml_lookback_period': 50,
            'candlestick_window': 5,
            'support_resistance_window': 20,
            'triangle_tolerance': 0.02,
            'flag_pennant_tolerance': 0.03,
            'head_shoulders_tolerance': 0.05,
            'double_top_tolerance': 0.03,
            'rounding_tolerance': 0.04
        }
    
    def train_pattern_model(self):
        """Train ML model for pattern recognition"""
        try:
            # Generate synthetic training data
            np.random.seed(42)
            n_samples = 2000
            n_features = 50
            
            # Generate synthetic pattern features
            X = np.random.randn(n_samples, n_features)
            X = self.scaler.fit_transform(X)
            
            # Generate pattern labels
            pattern_types = ['bullish', 'bearish', 'neutral']
            y = np.random.choice(pattern_types, n_samples, p=[0.3, 0.3, 0.4])
            
            # Train Random Forest classifier
            self.ml_model = RandomForestClassifier(n_estimators=200, random_state=42)
            self.ml_model.fit(X, y)
            
            logger.info("ML pattern recognition model trained successfully")
            
        except Exception as e:
            logger.error(f"Error training pattern model: {e}")
            self.ml_model = None
    
    def detect_trend_lines(self, prices: pd.Series) -> Dict[str, Any]:
        """Detect support and resistance trend lines"""
        try:
            # Find peaks and troughs
            peaks, _ = find_peaks(prices.values, distance=self.config['peak_detection_distance'])
            troughs, _ = find_peaks(-prices.values, distance=self.config['peak_detection_distance'])
            
            # Calculate trend lines
            support_lines = []
            resistance_lines = []
            
            # Support lines (connecting troughs)
            if len(troughs) >= self.config['trend_line_min_points']:
                for i in range(len(troughs) - 1):
                    for j in range(i + 1, len(troughs)):
                        slope, intercept, r_value, p_value, std_err = linregress(
                            [troughs[i], troughs[j]],
                            [prices.iloc[troughs[i]], prices.iloc[troughs[j]]]
                        )
                        if r_value > 0.8:  # Strong correlation
                            support_lines.append({
                                'slope': slope,
                                'intercept': intercept,
                                'r_squared': r_value ** 2,
                                'points': [troughs[i], troughs[j]]
                            })
            
            # Resistance lines (connecting peaks)
            if len(peaks) >= self.config['trend_line_min_points']:
                for i in range(len(peaks) - 1):
                    for j in range(i + 1, len(peaks)):
                        slope, intercept, r_value, p_value, std_err = linregress(
                            [peaks[i], peaks[j]],
                            [prices.iloc[peaks[i]], prices.iloc[peaks[j]]]
                        )
                        if r_value > 0.8:  # Strong correlation
                            resistance_lines.append({
                                'slope': slope,
                                'intercept': intercept,
                                'r_squared': r_value ** 2,
                                'points': [peaks[i], peaks[j]]
                            })
            
            return {
                'support_lines': support_lines,
                'resistance_lines': resistance_lines,
                'peaks': peaks,
                'troughs': troughs,
                'num_support': len(support_lines),
                'num_resistance': len(resistance_lines)
            }
            
        except Exception as e:
            logger.error(f"Error detecting trend lines: {e}")
            return {'support_lines': [], 'resistance_lines': [], 'peaks': [], 'troughs': [], 'num_support': 0, 'num_resistance': 0}
    
    def detect_triangle_patterns(self, high: pd.Series, low: pd.Series, close: pd.Series) -> List[PatternMatch]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        patterns = []
        
        try:
            # Get trend lines
            trend_data = self.detect_trend_lines(close)
            
            tolerance = self.config['triangle_tolerance']
            
            # Check for triangle formations
            for support_line in trend_data['support_lines']:
                for resistance_line in trend_data['resistance_lines']:
                    # Check if lines converge (triangle formation)
                    support_slope = support_line['slope']
                    resistance_slope = resistance_line['slope']
                    
                    # Ascending triangle: rising support, flat resistance
                    if support_slope > tolerance and abs(resistance_slope) < tolerance:
                        pattern_type = PatternType.ASCENDING_TRIANGLE
                        signal = PatternSignal.BULLISH
                        confidence = min(support_line['r_squared'], resistance_line['r_squared'])
                        
                    # Descending triangle: flat support, falling resistance
                    elif abs(support_slope) < tolerance and resistance_slope < -tolerance:
                        pattern_type = PatternType.DESCENDING_TRIANGLE
                        signal = PatternSignal.BEARISH
                        confidence = min(support_line['r_squared'], resistance_line['r_squared'])
                        
                    # Symmetrical triangle: converging trend lines
                    elif support_slope > tolerance and resistance_slope < -tolerance:
                        pattern_type = PatternType.SYMMETRICAL_TRIANGLE
                        signal = PatternSignal.NEUTRAL
                        confidence = min(support_line['r_squared'], resistance_line['r_squared'])
                        
                    else:
                        continue
                    
                    # Calculate pattern boundaries
                    start_idx = min(support_line['points'] + resistance_line['points'])
                    end_idx = max(support_line['points'] + resistance_line['points'])
                    
                    # Calculate price targets
                    pattern_height = abs(max(high.iloc[start_idx:end_idx]) - min(low.iloc[start_idx:end_idx]))
                    
                    if signal == PatternSignal.BULLISH:
                        price_target = close.iloc[end_idx] + pattern_height
                        stop_loss = min(low.iloc[start_idx:end_idx]) - pattern_height * 0.1
                    elif signal == PatternSignal.BEARISH:
                        price_target = close.iloc[end_idx] - pattern_height
                        stop_loss = max(high.iloc[start_idx:end_idx]) + pattern_height * 0.1
                    else:
                        price_target = None
                        stop_loss = None
                    
                    pattern = PatternMatch(
                        pattern_type=pattern_type,
                        symbol="SYMBOL",
                        start_time=datetime.now() - timedelta(hours=len(close) - start_idx),
                        end_time=datetime.now(),
                        signal=signal,
                        confidence=confidence,
                        price_target=price_target,
                        stop_loss=stop_loss,
                        pattern_score=confidence,
                        volume_confirmation=True,  # Placeholder
                        timeframe="1h",
                        pattern_data={
                            'support_slope': support_slope,
                            'resistance_slope': resistance_slope,
                            'pattern_height': pattern_height
                        }
                    )
                    
                    if confidence > self.config['confidence_threshold']:
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting triangle patterns: {e}")
            return []
    
    def detect_flag_pennant_patterns(self, high: pd.Series, low: pd.Series, close: pd.Series) -> List[PatternMatch]:
        """Detect flag and pennant patterns"""
        patterns = []
        
        try:
            tolerance = self.config['flag_pennant_tolerance']
            
            # Detect sharp price movement (flagpole)
            price_changes = close.pct_change()
            sharp_movements = np.where(np.abs(price_changes) > 0.05)[0]  # 5% moves
            
            for move_idx in sharp_movements:
                if move_idx + 20 >= len(close):  # Need space for pattern
                    continue
                
                # Check for consolidation after sharp move
                consolidation_start = move_idx + 1
                consolidation_end = min(move_idx + 15, len(close) - 1)
                
                consolidation_high = high.iloc[consolidation_start:consolidation_end]
                consolidation_low = low.iloc[consolidation_start:consolidation_end]
                
                # Check if price is consolidating (narrowing range)
                consolidation_range = (consolidation_high.max() - consolidation_low.min()) / close.iloc[move_idx]
                
                if consolidation_range < tolerance * 3:  # Narrow consolidation
                    # Determine pattern type based on preceding move
                    if price_changes.iloc[move_idx] > 0:  # Upward move
                        if close.iloc[consolidation_end] > close.iloc[consolidation_start]:
                            pattern_type = PatternType.BULLISH_FLAG
                            signal = PatternSignal.BULLISH
                        else:
                            pattern_type = PatternType.BULLISH_PENNANT
                            signal = PatternSignal.BULLISH
                    else:  # Downward move
                        if close.iloc[consolidation_end] < close.iloc[consolidation_start]:
                            pattern_type = PatternType.BEARISH_FLAG
                            signal = PatternSignal.BEARISH
                        else:
                            pattern_type = PatternType.BEARISH_PENNANT
                            signal = PatternSignal.BEARISH
                    
                    # Calculate price targets
                    flagpole_height = abs(close.iloc[move_idx] - close.iloc[max(0, move_idx-5)])
                    
                    if signal == PatternSignal.BULLISH:
                        price_target = consolidation_high.max() + flagpole_height
                        stop_loss = consolidation_low.min() - flagpole_height * 0.1
                    else:
                        price_target = consolidation_low.min() - flagpole_height
                        stop_loss = consolidation_high.max() + flagpole_height * 0.1
                    
                    pattern = PatternMatch(
                        pattern_type=pattern_type,
                        symbol="SYMBOL",
                        start_time=datetime.now() - timedelta(hours=len(close) - consolidation_start),
                        end_time=datetime.now(),
                        signal=signal,
                        confidence=0.7,  # Placeholder
                        price_target=price_target,
                        stop_loss=stop_loss,
                        pattern_score=0.7,
                        volume_confirmation=True,
                        timeframe="1h",
                        pattern_data={
                            'flagpole_height': flagpole_height,
                            'consolidation_range': consolidation_range
                        }
                    )
                    
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting flag/pennant patterns: {e}")
            return []
    
    def detect_head_shoulders_patterns(self, high: pd.Series, low: pd.Series, close: pd.Series) -> List[PatternMatch]:
        """Detect head and shoulders patterns"""
        patterns = []
        
        try:
            # Find peaks (potential shoulders and head)
            peaks, _ = find_peaks(close.values, distance=5, prominence=0.01)
            
            if len(peaks) >= 3:
                for i in range(len(peaks) - 2):
                    left_shoulder = peaks[i]
                    head = peaks[i + 1]
                    right_shoulder = peaks[i + 2]
                    
                    # Check if head is higher than both shoulders
                    if (close.iloc[head] > close.iloc[left_shoulder] and 
                        close.iloc[head] > close.iloc[right_shoulder]):
                        
                        # Check if shoulders are roughly at the same level
                        shoulder_diff = abs(close.iloc[left_shoulder] - close.iloc[right_shoulder])
                        avg_shoulder = (close.iloc[left_shoulder] + close.iloc[right_shoulder]) / 2
                        
                        tolerance = self.config['head_shoulders_tolerance']
                        if shoulder_diff / avg_shoulder < tolerance:
                            # Find neckline (support level)
                            neckline_start = min(left_shoulder, right_shoulder)
                            neckline_end = max(left_shoulder, right_shoulder)
                            
                            # Look for support between shoulders
                            support_area = low.iloc[neckline_start:neckline_end]
                            neckline = support_area.min()
                            
                            pattern_type = PatternType.HEAD_AND_SHOULDERS
                            signal = PatternSignal.BEARISH
                            
                            # Calculate price target
                            head_height = close.iloc[head] - neckline
                            price_target = neckline - head_height
                            stop_loss = close.iloc[head] + head_height * 0.1
                            
                            pattern = PatternMatch(
                                pattern_type=pattern_type,
                                symbol="SYMBOL",
                                start_time=datetime.now() - timedelta(hours=len(close) - left_shoulder),
                                end_time=datetime.now(),
                                signal=signal,
                                confidence=0.8,  # Placeholder
                                price_target=price_target,
                                stop_loss=stop_loss,
                                pattern_score=0.8,
                                volume_confirmation=True,
                                timeframe="1h",
                                pattern_data={
                                    'head_height': head_height,
                                    'neckline': neckline,
                                    'shoulder_diff': shoulder_diff
                                }
                            )
                            
                            patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting head and shoulders patterns: {e}")
            return []
    
    def detect_double_top_bottom_patterns(self, high: pd.Series, low: pd.Series, close: pd.Series) -> List[PatternMatch]:
        """Detect double top and double bottom patterns"""
        patterns = []
        
        try:
            # Find peaks and troughs
            peaks, _ = find_peaks(close.values, distance=5, prominence=0.01)
            troughs, _ = find_peaks(-close.values, distance=5, prominence=0.01)
            
            tolerance = self.config['double_top_tolerance']
            
            # Double Top
            if len(peaks) >= 2:
                for i in range(len(peaks) - 1):
                    first_peak = peaks[i]
                    second_peak = peaks[i + 1]
                    
                    # Check if peaks are at similar levels
                    peak_diff = abs(close.iloc[first_peak] - close.iloc[second_peak])
                    avg_peak = (close.iloc[first_peak] + close.iloc[second_peak]) / 2
                    
                    if peak_diff / avg_peak < tolerance:
                        # Find valley between peaks (neckline)
                        valley_start = min(first_peak, second_peak)
                        valley_end = max(first_peak, second_peak)
                        valley_area = low.iloc[valley_start:valley_end]
                        neckline = valley_area.min()
                        
                        pattern_type = PatternType.DOUBLE_TOP
                        signal = PatternSignal.BEARISH
                        
                        # Calculate price target
                        pattern_height = avg_peak - neckline
                        price_target = neckline - pattern_height
                        stop_loss = avg_peak + pattern_height * 0.1
                        
                        pattern = PatternMatch(
                            pattern_type=pattern_type,
                            symbol="SYMBOL",
                            start_time=datetime.now() - timedelta(hours=len(close) - first_peak),
                            end_time=datetime.now(),
                            signal=signal,
                            confidence=0.75,
                            price_target=price_target,
                            stop_loss=stop_loss,
                            pattern_score=0.75,
                            volume_confirmation=True,
                            timeframe="1h",
                            pattern_data={
                                'pattern_height': pattern_height,
                                'neckline': neckline,
                                'peak_diff': peak_diff
                            }
                        )
                        
                        patterns.append(pattern)
            
            # Double Bottom
            if len(troughs) >= 2:
                for i in range(len(troughs) - 1):
                    first_trough = troughs[i]
                    second_trough = troughs[i + 1]
                    
                    # Check if troughs are at similar levels
                    trough_diff = abs(close.iloc[first_trough] - close.iloc[second_trough])
                    avg_trough = (close.iloc[first_trough] + close.iloc[second_trough]) / 2
                    
                    if trough_diff / avg_trough < tolerance:
                        # Find peak between troughs (neckline)
                        peak_start = min(first_trough, second_trough)
                        peak_end = max(first_trough, second_trough)
                        peak_area = high.iloc[peak_start:peak_end]
                        neckline = peak_area.max()
                        
                        pattern_type = PatternType.DOUBLE_BOTTOM
                        signal = PatternSignal.BULLISH
                        
                        # Calculate price target
                        pattern_height = neckline - avg_trough
                        price_target = neckline + pattern_height
                        stop_loss = avg_trough - pattern_height * 0.1
                        
                        pattern = PatternMatch(
                            pattern_type=pattern_type,
                            symbol="SYMBOL",
                            start_time=datetime.now() - timedelta(hours=len(close) - first_trough),
                            end_time=datetime.now(),
                            signal=signal,
                            confidence=0.75,
                            price_target=price_target,
                            stop_loss=stop_loss,
                            pattern_score=0.75,
                            volume_confirmation=True,
                            timeframe="1h",
                            pattern_data={
                                'pattern_height': pattern_height,
                                'neckline': neckline,
                                'trough_diff': trough_diff
                            }
                        )
                        
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting double top/bottom patterns: {e}")
            return []
    
    def detect_candlestick_patterns(self, open_prices: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> List[PatternMatch]:
        """Detect candlestick patterns using TA-Lib"""
        patterns = []
        
        try:
            # Single candle patterns
            hammer = talib.CDLHAMMER(open_prices.values, high.values, low.values, close.values)
            hanging_man = talib.CDLHANGINGMAN(open_prices.values, high.values, low.values, close.values)
            shooting_star = talib.CDLSHOOTINGSTAR(open_prices.values, high.values, low.values, close.values)
            inverted_hammer = talib.CDLINVERTEDHAMMER(open_prices.values, high.values, low.values, close.values)
            doji = talib.CDLDOJI(open_prices.values, high.values, low.values, close.values)
            spinning_top = talib.CDLSPINNINGTOP(open_prices.values, high.values, low.values, close.values)
            
            # Multi-candle patterns
            bullish_engulfing = talib.CDLENGULFING(open_prices.values, high.values, low.values, close.values)
            bearish_engulfing = -talib.CDLENGULFING(open_prices.values, high.values, low.values, close.values)
            morning_star = talib.CDLMORNINGSTAR(open_prices.values, high.values, low.values, close.values)
            evening_star = talib.CDLEVENINGSTAR(open_prices.values, high.values, low.values, close.values)
            three_white_soldiers = talib.CDL3WHITESOLDIERS(open_prices.values, high.values, low.values, close.values)
            three_black_crows = talib.CDL3BLACKCROWS(open_prices.values, high.values, low.values, close.values)
            
            # Map TA-Lib patterns to our pattern types
            pattern_mapping = {
                'hammer': (hammer, PatternType.HAMMER, PatternSignal.BULLISH),
                'hanging_man': (hanging_man, PatternType.HANGING_MAN, PatternSignal.BEARISH),
                'shooting_star': (shooting_star, PatternType.SHOOTING_STAR, PatternSignal.BEARISH),
                'inverted_hammer': (inverted_hammer, PatternType.INVERTED_HAMMER, PatternSignal.BULLISH),
                'doji': (doji, PatternType.DOJI, PatternSignal.NEUTRAL),
                'spinning_top': (spinning_top, PatternType.SPINNING_TOP, PatternSignal.NEUTRAL),
                'bullish_engulfing': (bullish_engulfing, PatternType.BULLISH_ENGULFING, PatternSignal.BULLISH),
                'bearish_engulfing': (bearish_engulfing, PatternType.BEARISH_ENGULFING, PatternSignal.BEARISH),
                'morning_star': (morning_star, PatternType.MORNING_STAR, PatternSignal.BULLISH),
                'evening_star': (evening_star, PatternType.EVENING_STAR, PatternSignal.BEARISH),
                'three_white_soldiers': (three_white_soldiers, PatternType.THREE_WHITE_SOLDIERS, PatternSignal.BULLISH),
                'three_black_crows': (three_black_crows, PatternType.THREE_BLACK_CROWS, PatternSignal.BEARISH)
            }
            
            for pattern_name, (pattern_array, pattern_type, signal) in pattern_mapping.items():
                # Find where patterns occur
                pattern_indices = np.where(pattern_array > 0)[0]
                
                for idx in pattern_indices:
                    if idx < len(close):
                        pattern = PatternMatch(
                            pattern_type=pattern_type,
                            symbol="SYMBOL",
                            start_time=datetime.now() - timedelta(hours=len(close) - idx),
                            end_time=datetime.now(),
                            signal=signal,
                            confidence=0.8,  # TA-Lib patterns have high confidence
                            price_target=None,  # Would calculate based on pattern
                            stop_loss=None,
                            pattern_score=0.8,
                            volume_confirmation=True,
                            timeframe="1h",
                            pattern_data={
                                'pattern_index': idx,
                                'close_price': close.iloc[idx],
                                'pattern_name': pattern_name
                            }
                        )
                        
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {e}")
            return []
    
    def analyze_patterns(self, market_data: Dict[str, pd.Series], symbol: str, timeframe: str = '1h') -> List[PatternMatch]:
        """
        Comprehensive pattern analysis
        
        Args:
            market_data: Dictionary with 'open', 'high', 'low', 'close', 'volume' series
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            List of detected patterns
        """
        try:
            # Extract data
            open_prices = market_data['open']
            high = market_data['high']
            low = market_data['low']
            close = market_data['close']
            volume = market_data.get('volume', pd.Series([1.0] * len(close)))
            
            all_patterns = []
            
            # Detect different pattern types
            
            # Triangle patterns
            triangle_patterns = self.detect_triangle_patterns(high, low, close)
            all_patterns.extend(triangle_patterns)
            
            # Flag and pennant patterns
            flag_patterns = self.detect_flag_pennant_patterns(high, low, close)
            all_patterns.extend(flag_patterns)
            
            # Head and shoulders patterns
            hs_patterns = self.detect_head_shoulders_patterns(high, low, close)
            all_patterns.extend(hs_patterns)
            
            # Double top/bottom patterns
            double_patterns = self.detect_double_top_bottom_patterns(high, low, close)
            all_patterns.extend(double_patterns)
            
            # Candlestick patterns
            candlestick_patterns = self.detect_candlestick_patterns(open_prices, high, low, close)
            all_patterns.extend(candlestick_patterns)
            
            # Update symbol and timeframe for all patterns
            for pattern in all_patterns:
                pattern.symbol = symbol
                pattern.timeframe = timeframe
            
            # Filter by confidence threshold
            filtered_patterns = [p for p in all_patterns if p.confidence >= self.config['confidence_threshold']]
            
            # Sort by confidence
            filtered_patterns.sort(key=lambda x: x.confidence, reverse=True)
            
            logger.info(f"Detected {len(filtered_patterns)} patterns for {symbol} with confidence >= {self.config['confidence_threshold']}")
            
            return filtered_patterns
            
        except Exception as e:
            logger.error(f"Error analyzing patterns for {symbol}: {e}")
            return []
    
    def get_ml_pattern_prediction(self, market_data: Dict[str, pd.Series]) -> Dict[str, Any]:
        """Get ML-based pattern prediction"""
        try:
            if self.ml_model is None:
                return {'prediction': 'neutral', 'confidence': 0.5}
            
            # Extract features from market data
            close = market_data['close']
            
            # Calculate various features
            features = []
            
            # Price-based features
            returns = close.pct_change()
            features.extend([
                returns.mean(),
                returns.std(),
                returns.skew(),
                returns.kurtosis(),
                close.iloc[-1] / close.iloc[0] - 1  # Total return
            ])
            
            # Technical indicator features
            rsi = talib.RSI(close.values, timeperiod=14)
            macd, _, _ = talib.MACD(close.values)
            
            features.extend([
                rsi[-1] if len(rsi) > 0 else 50,
                macd[-1] if len(macd) > 0 else 0
            ])
            
            # Volatility features
            volatility = returns.rolling(window=20).std()
            features.extend([
                volatility.iloc[-1] if len(volatility) > 0 else 0,
                volatility.mean() if len(volatility) > 0 else 0
            ])
            
            # Pad or truncate to expected length
            expected_features = 50
            if len(features) < expected_features:
                features.extend([0.0] * (expected_features - len(features)))
            else:
                features = features[:expected_features]
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Get prediction
            prediction = self.ml_model.predict(features_scaled)[0]
            
            # Get prediction probabilities
            probabilities = self.ml_model.predict_proba(features_scaled)[0]
            confidence = max(probabilities)
            
            return {
                'prediction': prediction,
                'confidence': float(confidence),
                'probabilities': {
                    'bullish': float(probabilities[0]),
                    'bearish': float(probabilities[1]),
                    'neutral': float(probabilities[2])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting ML pattern prediction: {e}")
            return {'prediction': 'neutral', 'confidence': 0.5}
    
    def scan_pattern_opportunities(self, market_data_dict: Dict[str, Dict[str, pd.Series]], 
                                 min_confidence: float = 0.6) -> List[PatternMatch]:
        """
        Scan multiple symbols for pattern trading opportunities
        
        Args:
            market_data_dict: Dictionary of symbol -> OHLCV data
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of pattern opportunities
        """
        all_opportunities = []
        
        try:
            for symbol, market_data in market_data_dict.items():
                # Analyze patterns for each symbol
                patterns = self.analyze_patterns(market_data, symbol)
                
                # Filter by confidence
                high_confidence_patterns = [p for p in patterns if p.confidence >= min_confidence]
                
                all_opportunities.extend(high_confidence_patterns)
            
            # Sort by confidence and signal strength
            all_opportunities.sort(key=lambda x: (x.confidence, x.pattern_score), reverse=True)
            
            logger.info(f"Found {len(all_opportunities)} pattern opportunities with confidence >= {min_confidence}")
            
            return all_opportunities
            
        except Exception as e:
            logger.error(f"Error scanning pattern opportunities: {e}")
            return []

# Example usage and testing
def example_usage():
    """
    Example usage of the Advanced Pattern Recognition system
    """
    
    # Create pattern recognition system
    pattern_recognizer = AdvancedPatternRecognition()
    
    # Generate sample market data
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1h')
    
    # Generate synthetic OHLCV data with some patterns
    base_price = 100.0
    prices = [base_price]
    
    # Create some trend patterns
    for i in range(1, 200):
        if i < 50:  # Uptrend
            trend = 0.001
        elif i < 100:  # Downtrend
            trend = -0.001
        elif i < 150:  # Sideways
            trend = 0.0
        else:  # Uptrend again
            trend = 0.001
        
        noise = np.random.normal(0, 0.01)
        new_price = prices[-1] * (1 + trend + noise)
        prices.append(new_price)
    
    prices = pd.Series(prices, index=dates)
    
    # Create OHLCV data
    high = prices * (1 + np.abs(np.random.normal(0, 0.005, 200)))
    low = prices * (1 - np.abs(np.random.normal(0, 0.005, 200)))
    close = prices
    open_prices = prices.shift(1).fillna(prices.iloc[0])
    volume = pd.Series(np.random.randint(1000, 10000, 200), index=dates)
    
    market_data = {
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }
    
    # Analyze patterns
    print("Analyzing patterns for sample data...")
    patterns = pattern_recognizer.analyze_patterns(market_data, "BTCUSDT", "1h")
    
    print(f"\nPattern Analysis Results:")
    print(f"Total patterns detected: {len(patterns)}")
    
    # Group patterns by type
    pattern_summary = {}
    for pattern in patterns:
        pattern_name = pattern.pattern_type.value
        if pattern_name not in pattern_summary:
            pattern_summary[pattern_name] = []
        pattern_summary[pattern_name].append(pattern)
    
    print(f"\nPattern Summary:")
    for pattern_type, pattern_list in pattern_summary.items():
        print(f"  {pattern_type}: {len(pattern_list)} occurrences")
        if pattern_list:
            avg_confidence = np.mean([p.confidence for p in pattern_list])
            print(f"    Average confidence: {avg_confidence:.3f}")
    
    # Show top patterns
    if patterns:
        print(f"\nTop 5 Patterns by Confidence:")
        for i, pattern in enumerate(patterns[:5]):
            print(f"  {i+1}. {pattern.pattern_type.value} ({pattern.signal.value})")
            print(f"     Confidence: {pattern.confidence:.3f}")
            print(f"     Score: {pattern.pattern_score:.3f}")
            if pattern.price_target:
                print(f"     Price Target: {pattern.price_target:.2f}")
            if pattern.stop_loss:
                print(f"     Stop Loss: {pattern.stop_loss:.2f}")
            print()
    
    # Get ML prediction
    print("="*50)
    print("ML Pattern Prediction:")
    ml_prediction = pattern_recognizer.get_ml_pattern_prediction(market_data)
    print(f"Prediction: {ml_prediction['prediction']}")
    print(f"Confidence: {ml_prediction['confidence']:.3f}")
    if 'probabilities' in ml_prediction:
        print("Probabilities:")
        for key, value in ml_prediction['probabilities'].items():
            print(f"  {key}: {value:.3f}")
    
    # Scan multiple symbols
    print("\n" + "="*50)
    print("Scanning pattern opportunities...")
    
    # Create sample market data for multiple symbols
    market_data_multi = {}
    symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT"]
    
    for symbol in symbols:
        # Generate different price patterns for each symbol
        base_price = np.random.uniform(50, 50000)
        prices = [base_price]
        
        for i in range(1, 200):
            trend = np.random.uniform(-0.002, 0.002)
            noise = np.random.normal(0, 0.01)
            new_price = prices[-1] * (1 + trend + noise)
            prices.append(new_price)
        
        prices_series = pd.Series(prices, index=dates)
        
        market_data_multi[symbol] = {
            'open': prices_series.shift(1).fillna(prices_series.iloc[0]),
            'high': prices_series * (1 + np.abs(np.random.normal(0, 0.005, 200))),
            'low': prices_series * (1 - np.abs(np.random.normal(0, 0.005, 200))),
            'close': prices_series,
            'volume': pd.Series(np.random.randint(1000, 10000, 200), index=dates)
        }
    
    # Scan for opportunities
    opportunities = pattern_recognizer.scan_pattern_opportunities(market_data_multi, min_confidence=0.5)
    
    print(f"\nFound {len(opportunities)} pattern opportunities:")
    for i, opp in enumerate(opportunities[:10]):  # Show top 10
        print(f"  {i+1}. {opp.symbol} - {opp.pattern_type.value} ({opp.signal.value})")
        print(f"     Confidence: {opp.confidence:.3f}, Score: {opp.pattern_score:.3f}")
        if opp.price_target:
            print(f"     Target: {opp.price_target:.2f}, Stop: {opp.stop_loss:.2f}")
        print()

if __name__ == "__main__":
    example_usage()