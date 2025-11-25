"""
Analisador de Mercado Forex para IA GAIN
Análise técnica e fundamentalista específica para forex
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from loguru import logger

class ForexSignal(Enum):
    """Sinais de trading forex"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

@dataclass
class ForexAnalysis:
    """Resultado da análise forex"""
    symbol: str
    signal: ForexSignal
    confidence: float
    entry_price: float
    stop_loss_pips: float
    take_profit_pips: float
    risk_reward_ratio: float
    strength_score: float
    correlation_score: float
    volatility_score: float
    fundamental_score: float
    technical_score: float
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'signal': self.signal.value,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss_pips': self.stop_loss_pips,
            'take_profit_pips': self.take_profit_pips,
            'risk_reward_ratio': self.risk_reward_ratio,
            'strength_score': self.strength_score,
            'correlation_score': self.correlation_score,
            'volatility_score': self.volatility_score,
            'fundamental_score': self.fundamental_score,
            'technical_score': self.technical_score,
            'timestamp': self.timestamp.isoformat()
        }

class ForexAnalyzer:
    """Analisador de mercado forex"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logger.bind(component="ForexAnalyzer")
        
        # Configurações padrão
        self.rsi_period = self.config.get('rsi_period', 14)
        self.rsi_overbought = self.config.get('rsi_overbought', 70)
        self.rsi_oversold = self.config.get('rsi_oversold', 30)
        
        self.macd_fast = self.config.get('macd_fast', 12)
        self.macd_slow = self.config.get('macd_slow', 26)
        self.macd_signal = self.config.get('macd_signal', 9)
        
        self.bb_period = self.config.get('bb_period', 20)
        self.bb_std = self.config.get('bb_std', 2)
        
        self.atr_period = self.config.get('atr_period', 14)
        self.adx_period = self.config.get('adx_period', 14)
        self.stoch_period = self.config.get('stoch_period', 14)
        
        # Limites de risco
        self.max_spread = self.config.get('max_spread', 0.005)  # 5 pips
        self.min_volatility = self.config.get('min_volatility', 0.005)
        self.max_volatility = self.config.get('max_volatility', 0.02)
    
    def calculate_pips(self, symbol: str, price_change: float) -> float:
        """Calcular pips para um par forex"""
        # Para pares com JPY, 1 pip = 0.01
        if 'JPY' in symbol:
            return price_change * 100
        else:
            return price_change * 10000
    
    def calculate_pip_value(self, symbol: str, lot_size: float = 0.1) -> float:
        """Calcular valor do pip"""
        # Valor aproximado do pip em USD
        pip_values = {
            'EUR/USD': 1.0, 'GBP/USD': 1.0, 'AUD/USD': 1.0, 'NZD/USD': 1.0,
            'USD/JPY': 0.9, 'USD/CHF': 1.1, 'USD/CAD': 0.8,
            'EUR/GBP': 1.3, 'EUR/JPY': 0.9, 'GBP/JPY': 0.9
        }
        
        base_value = pip_values.get(symbol, 1.0)
        return base_value * lot_size * 10  # Multiplicar por 10 para lotes padrão
    
    def analyze_technical_indicators(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Análise técnica específica forex"""
        try:
            # RSI
            rsi = self.calculate_rsi(df['close'])
            current_rsi = rsi.iloc[-1]
            
            # MACD
            macd, macd_signal = self.calculate_macd(df['close'])
            current_macd = macd.iloc[-1]
            current_macd_signal = macd_signal.iloc[-1]
            macd_crossover = current_macd > current_macd_signal
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df['close'])
            current_price = df['close'].iloc[-1]
            bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
            
            # ATR (Average True Range)
            atr = self.calculate_atr(df)
            current_atr = atr.iloc[-1]
            
            # ADX (Average Directional Index)
            adx = self.calculate_adx(df)
            current_adx = adx.iloc[-1]
            
            # Stochastic
            stoch_k, stoch_d = self.calculate_stochastic(df)
            current_stoch_k = stoch_k.iloc[-1]
            current_stoch_d = stoch_d.iloc[-1]
            
            # Análise de tendência
            ema_20 = df['close'].ewm(span=20).mean()
            ema_50 = df['close'].ewm(span=50).mean()
            trend_bullish = ema_20.iloc[-1] > ema_50.iloc[-1]
            
            # Calcular scores
            technical_score = 0
            
            # RSI Score
            if current_rsi < self.rsi_oversold:
                technical_score += 2  # Sobrevenda
            elif current_rsi > self.rsi_overbought:
                technical_score -= 2  # Sobrecompra
            
            # MACD Score
            if macd_crossover and current_macd > 0:
                technical_score += 2
            elif not macd_crossover and current_macd < 0:
                technical_score -= 2
            
            # Bollinger Score
            if bb_position < 0.2:  # Próximo da banda inferior
                technical_score += 1
            elif bb_position > 0.8:  # Próximo da banda superior
                technical_score -= 1
            
            # ADX Score (força da tendência)
            if current_adx > 25:
                if trend_bullish:
                    technical_score += 1
                else:
                    technical_score -= 1
            
            # Stochastic Score
            if current_stoch_k < 20 and current_stoch_d < 20:
                technical_score += 1
            elif current_stoch_k > 80 and current_stoch_d > 80:
                technical_score -= 1
            
            return {
                'score': technical_score,
                'rsi': current_rsi,
                'macd': current_macd,
                'macd_signal': current_macd_signal,
                'bb_position': bb_position,
                'atr': current_atr,
                'adx': current_adx,
                'stoch_k': current_stoch_k,
                'stoch_d': current_stoch_d,
                'trend_bullish': trend_bullish,
                'price_vs_ema20': (current_price - ema_20.iloc[-1]) / ema_20.iloc[-1]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise técnica para {symbol}: {str(e)}")
            return {'score': 0}
    
    def analyze_fundamental_factors(self, symbol: str) -> Dict:
        """Análise fundamentalista forex (simplificada)"""
        try:
            # Fatores fundamentais para pares principais
            fundamental_scores = {
                'EUR/USD': 0.5,    # Euro relativamente forte
                'GBP/USD': 0.3,    # Libra com volatilidade política
                'USD/JPY': 0.7,    # Iene como safe haven
                'USD/CHF': 0.8,    # Franco suíço safe haven
                'AUD/USD': 0.4,    # Dólar australiano commodity-linked
                'USD/CAD': 0.6,    # Dólar canadense commodity-linked
                'NZD/USD': 0.3     # Dólar neozelandês menor liquidez
            }
            
            base_score = fundamental_scores.get(symbol, 0.5)
            
            # Adicionar variação temporal (simulação)
            time_factor = np.sin(datetime.now().timestamp() / 86400) * 0.1
            final_score = base_score + time_factor
            
            return {
                'score': final_score,
                'base_score': base_score,
                'time_factor': time_factor,
                'economic_strength': 'strong' if final_score > 0.6 else 'weak' if final_score < 0.4 else 'neutral'
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise fundamental para {symbol}: {str(e)}")
            return {'score': 0.5}
    
    def analyze_correlation(self, symbol: str, market_data: Dict) -> Dict:
        """Análise de correlação entre pares forex"""
        try:
            # Correlações típicas entre pares forex
            correlations = {
                'EUR/USD': {'positive': ['GBP/USD', 'AUD/USD'], 'negative': ['USD/CHF']},
                'GBP/USD': {'positive': ['EUR/USD', 'AUD/USD'], 'negative': ['USD/JPY']},
                'USD/JPY': {'positive': ['USD/CHF'], 'negative': ['EUR/USD', 'GBP/USD']},
                'USD/CHF': {'positive': ['USD/JPY'], 'negative': ['EUR/USD', 'GBP/USD']},
                'AUD/USD': {'positive': ['EUR/USD', 'GBP/USD'], 'negative': ['USD/CAD']},
                'USD/CAD': {'positive': ['USD/JPY'], 'negative': ['AUD/USD']}
            }
            
            symbol_correlations = correlations.get(symbol, {'positive': [], 'negative': []})
            
            # Simular análise de correlação (em produção, usar dados históricos)
            correlation_risk = len(symbol_correlations['positive']) * 0.1
            correlation_opportunity = len(symbol_correlations['negative']) * 0.05
            
            return {
                'score': correlation_opportunity - correlation_risk,
                'positive_correlations': symbol_correlations['positive'],
                'negative_correlations': symbol_correlations['negative'],
                'diversification_potential': 'high' if correlation_opportunity > correlation_risk else 'low'
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise de correlação para {symbol}: {str(e)}")
            return {'score': 0}
    
    def calculate_volatility_score(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Análise de volatilidade forex"""
        try:
            # Calcular volatilidade histórica
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Volatilidade anualizada
            
            # Converter para pips
            volatility_pips = self.calculate_pips(symbol, volatility)
            
            # Score baseado na volatilidade
            if volatility_pips < self.min_volatility * 10000:
                volatility_score = -1  # Muito baixa volatilidade
            elif volatility_pips > self.max_volatility * 10000:
                volatility_score = -2  # Muito alta volatilidade
            else:
                volatility_score = 1  # Volatilidade ideal
            
            return {
                'score': volatility_score,
                'volatility_pips': volatility_pips,
                'volatility_percentage': volatility * 100,
                'volatility_category': 'low' if volatility_pips < 50 else 'high' if volatility_pips > 200 else 'optimal'
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise de volatilidade para {symbol}: {str(e)}")
            return {'score': 0}
    
    def generate_signal(self, analysis_results: Dict, symbol: str, current_price: float) -> ForexAnalysis:
        """Gerar sinal de trading baseado na análise"""
        try:
            # Combinar todos os scores
            technical_score = analysis_results['technical']['score']
            fundamental_score = analysis_results['fundamental']['score'] * 2  # Ponderar fundamental
            correlation_score = analysis_results['correlation']['score']
            volatility_score = analysis_results['volatility']['score']
            
            total_score = technical_score + fundamental_score + correlation_score + volatility_score
            
            # Determinar sinal
            if total_score >= 4:
                signal = ForexSignal.STRONG_BUY
                confidence = 0.8
            elif total_score >= 2:
                signal = ForexSignal.BUY
                confidence = 0.6
            elif total_score <= -4:
                signal = ForexSignal.STRONG_SELL
                confidence = 0.8
            elif total_score <= -2:
                signal = ForexSignal.SELL
                confidence = 0.6
            else:
                signal = ForexSignal.HOLD
                confidence = 0.3
            
            # Calcular níveis de entrada e saída
            atr = analysis_results['technical'].get('atr', 0.001)
            stop_loss_pips = self.calculate_pips(symbol, atr * 2)  # 2x ATR
            
            if signal in [ForexSignal.BUY, ForexSignal.STRONG_BUY]:
                take_profit_pips = stop_loss_pips * 2  # R:R 1:2
            elif signal in [ForexSignal.SELL, ForexSignal.STRONG_SELL]:
                take_profit_pips = stop_loss_pips * 2
            else:
                stop_loss_pips = 0
                take_profit_pips = 0
            
            risk_reward_ratio = take_profit_pips / stop_loss_pips if stop_loss_pips > 0 else 0
            
            return ForexAnalysis(
                symbol=symbol,
                signal=signal,
                confidence=confidence,
                entry_price=current_price,
                stop_loss_pips=stop_loss_pips,
                take_profit_pips=take_profit_pips,
                risk_reward_ratio=risk_reward_ratio,
                strength_score=total_score,
                correlation_score=correlation_score,
                volatility_score=volatility_score,
                fundamental_score=fundamental_score,
                technical_score=technical_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar sinal para {symbol}: {str(e)}")
            return ForexAnalysis(
                symbol=symbol,
                signal=ForexSignal.HOLD,
                confidence=0.1,
                entry_price=current_price,
                stop_loss_pips=0,
                take_profit_pips=0,
                risk_reward_ratio=0,
                strength_score=0,
                correlation_score=0,
                volatility_score=0,
                fundamental_score=0,
                technical_score=0,
                timestamp=datetime.now()
            )
    
    async def analyze_forex_pair(self, symbol: str, df: pd.DataFrame) -> ForexAnalysis:
        """Análise completa de um par forex"""
        try:
            self.logger.info(f"Analisando par forex: {symbol}")
            
            # Verificar dados
            if df.empty or len(df) < 50:
                self.logger.warning(f"Dados insuficientes para {symbol}")
                return self.generate_signal({}, symbol, 0)
            
            current_price = df['close'].iloc[-1]
            
            # Realizar todas as análises
            technical_analysis = self.analyze_technical_indicators(df, symbol)
            fundamental_analysis = self.analyze_fundamental_factors(symbol)
            correlation_analysis = self.analyze_correlation(symbol, {})
            volatility_analysis = self.calculate_volatility_score(df, symbol)
            
            # Combinar resultados
            analysis_results = {
                'technical': technical_analysis,
                'fundamental': fundamental_analysis,
                'correlation': correlation_analysis,
                'volatility': volatility_analysis
            }
            
            # Gerar sinal final
            forex_analysis = self.generate_signal(analysis_results, symbol, current_price)
            
            self.logger.info(f"Análise forex concluída para {symbol}: {forex_analysis.signal.value} (confiança: {forex_analysis.confidence:.2f})")
            
            return forex_analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise forex para {symbol}: {str(e)}")
            return ForexAnalysis(
                symbol=symbol,
                signal=ForexSignal.HOLD,
                confidence=0.1,
                entry_price=0,
                stop_loss_pips=0,
                take_profit_pips=0,
                risk_reward_ratio=0,
                strength_score=0,
                correlation_score=0,
                volatility_score=0,
                fundamental_score=0,
                technical_score=0,
                timestamp=datetime.now()
            )
    
    # Métodos auxiliares (já implementados no DataCollector)
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        return true_range.rolling(window=period).mean()
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=d_period).mean()
        
        return k, d