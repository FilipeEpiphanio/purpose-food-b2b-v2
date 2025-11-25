#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - TESTE EM TEMPO REAL MERCADO
Validacao avancada para execucao de trades em mercado real
"""

import MetaTrader5 as mt5
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple
import threading
import signal
import sys

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_time_trading_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IA_GAIN_RealTimeTest:
    """Teste em tempo real com validacao avancada de mercado"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        self.running = True
        self.trades_executed = 0
        
        # Parametros CONSERVADORES para teste real
        self.max_positions = 3  # Reduzido para teste
        self.max_risk_per_trade = 0.005  # 0.5% risco por trade (ultra conservador)
        self.min_confidence = 0.60  # 60% confianca minima
        self.risk_reward_ratio = 2.0  # 1:2 ratio
        self.volume_base = 0.01  # Volume minimo
        
        # Filtros rigorosos para mercado real
        self.filters = {
            'max_spread': 30,  # Spread maximo 30 pontos
            'min_volatility': 0.0002,  # Volatilidade minima
            'max_volatility': 0.015,  # Volatilidade maxima
            'volume_threshold': 2.0,  # Volume 2x acima da media
            'trend_confirmation_periods': 3,  # 3 periodos de confirmacao
        }
        
        # Pares principais para teste
        self.trading_symbols = [
            'EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm'
        ]
        
        # Estatisticas em tempo real
        self.session_stats = {
            'trades_executed': 0,
            'trades_won': 0,
            'trades_lost': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'start_balance': 0.0,
            'start_time': datetime.now()
        }
        
        self.operation_history = []
        self.active_positions = {}
        
        # Configurar sinal de interrupcao
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para interrupcao graceful"""
        logger.info("Recebido sinal de interrupcao, finalizando...")
        self.running = False
    
    def connect_to_mt5(self) -> bool:
        """Conecta ao MetaTrader 5 com validacao"""
        try:
            logger.info("Conectando ao MetaTrader 5 (Teste Real)...")
            
            if not mt5.initialize():
                logger.error(f"Falha ao inicializar MT5: {mt5.last_error()}")
                return False
            
            self.account_info = mt5.account_info()
            if self.account_info is None:
                logger.error("Nao foi possivel obter informacoes da conta")
                return False
            
            self.session_stats['start_balance'] = self.account_info.balance
            
            logger.info(f"CONECTADO! Conta: {self.account_info.login}")
            logger.info(f"Saldo: ${self.account_info.balance:.2f}")
            logger.info(f"Alavancagem: 1:{self.account_info.leverage}")
            logger.info(f"Servidor: {self.account_info.server}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar MT5: {e}")
            return False
    
    def validate_market_conditions(self, symbol: str) -> Dict:
        """Validacao rigorosa das condicoes de mercado"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'valid': False, 'error': 'Simbolo nao disponivel'}
            
            # Verificar se o mercado esta aberto
            if not symbol_info.session_open:
                return {'valid': False, 'error': 'Mercado fechado'}
            
            # Verificar spread
            if symbol_info.spread > self.filters['max_spread']:
                return {'valid': False, 'error': f'Spread alto: {symbol_info.spread}'}
            
            # Verificar volatilidade atual
            volatility_check = self._check_volatility_conditions(symbol)
            if not volatility_check['valid']:
                return volatility_check
            
            # Verificar volume
            volume_check = self._check_volume_conditions(symbol)
            if not volume_check['valid']:
                return volume_check
            
            # Verificar tendencia de mercado
            trend_check = self._check_trend_conditions(symbol)
            if not trend_check['valid']:
                return trend_check
            
            return {
                'valid': True,
                'spread': symbol_info.spread,
                'volatility': volatility_check['volatility_pct'],
                'volume_ratio': volume_check['volume_ratio'],
                'trend_strength': trend_check['trend_strength']
            }
            
        except Exception as e:
            logger.error(f"Erro validacao mercado {symbol}: {e}")
            return {'valid': False, 'error': str(e)}
    
    def _check_volatility_conditions(self, symbol: str) -> Dict:
        """Verifica condicoes de volatilidade"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 50)
            if rates is None or len(rates) < 20:
                return {'valid': False, 'error': 'Dados insuficientes'}
            
            df = pd.DataFrame(rates)
            
            # Calcular volatilidade real
            high_low = df['high'] - df['low']
            current_price = df['close'].iloc[-1]
            avg_range = high_low.tail(14).mean()
            volatility_pct = (avg_range / current_price) * 100
            
            # Verificar se esta dentro dos limites
            if volatility_pct < self.filters['min_volatility']:
                return {'valid': False, 'error': f'Volatilidade baixa: {volatility_pct:.4f}%'}
            elif volatility_pct > self.filters['max_volatility']:
                return {'valid': False, 'error': f'Volatilidade alta: {volatility_pct:.4f}%'}
            
            return {'valid': True, 'volatility_pct': volatility_pct}
            
        except Exception as e:
            return {'valid': False, 'error': f'Erro volatilidade: {e}'}
    
    def _check_volume_conditions(self, symbol: str) -> Dict:
        """Verifica condicoes de volume"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 30)
            if rates is None or len(rates) < 20:
                return {'valid': False, 'error': 'Dados de volume insuficientes'}
            
            df = pd.DataFrame(rates)
            
            # Analisar volume
            avg_volume = df['tick_volume'].tail(20).mean()
            current_volume = df['tick_volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            if volume_ratio < self.filters['volume_threshold']:
                return {'valid': False, 'error': f'Volume baixo: {volume_ratio:.1f}x'}
            
            return {'valid': True, 'volume_ratio': volume_ratio}
            
        except Exception as e:
            return {'valid': False, 'error': f'Erro volume: {e}'}
    
    def _check_trend_conditions(self, symbol: str) -> Dict:
        """Verifica condicoes de tendencia"""
        try:
            # Multi-timeframe trend analysis
            timeframes = [
                (mt5.TIMEFRAME_M5, 'M5', 20),
                (mt5.TIMEFRAME_M15, 'M15', 30),
                (mt5.TIMEFRAME_H1, 'H1', 24)
            ]
            
            trend_scores = {'bullish': 0, 'bearish': 0, 'neutral': 0}
            
            for tf, tf_name, periods in timeframes:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, periods)
                if rates is None or len(rates) < 10:
                    continue
                
                df = pd.DataFrame(rates)
                current_price = df['close'].iloc[-1]
                
                # EMAs multiplas
                ema_fast = df['close'].tail(10).ewm(span=10).mean().iloc[-1]
                ema_medium = df['close'].tail(20).ewm(span=20).mean().iloc[-1]
                ema_slow = df['close'].tail(50).ewm(span=50).mean().iloc[-1]
                
                if current_price > ema_fast > ema_medium > ema_slow:
                    trend_scores['bullish'] += 1
                elif current_price < ema_fast < ema_medium < ema_slow:
                    trend_scores['bearish'] += 1
                else:
                    trend_scores['neutral'] += 1
            
            total_trends = sum(trend_scores.values())
            if total_trends == 0:
                return {'valid': False, 'error': 'Sem dados de tendencia'}
            
            # Calcular força da tendencia
            max_trend = max(trend_scores, key=trend_scores.get)
            trend_strength = trend_scores[max_trend] / total_trends
            
            if trend_strength < 0.6:  # Menos de 60% de consenso
                return {'valid': False, 'error': f'Tendencia fraca: {trend_strength:.1%}'}
            
            return {'valid': True, 'trend_strength': trend_strength, 'trend_direction': max_trend}
            
        except Exception as e:
            return {'valid': False, 'error': f'Erro tendencia: {e}'}
    
    def advanced_real_time_analysis(self, symbol: str) -> Dict:
        """Analise avancada em tempo real"""
        try:
            # Validacao de mercado primeiro
            market_validation = self.validate_market_conditions(symbol)
            if not market_validation['valid']:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': market_validation['error']}
            
            if not mt5.symbol_select(symbol, True):
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Simbolo nao selecionado'}
            
            symbol_info = mt5.symbol_info(symbol)
            current_price = (symbol_info.ask + symbol_info.bid) / 2
            
            # Analise multi-timeframe avancada
            multi_tf_signal = self._advanced_multi_timeframe_analysis(symbol)
            
            # Analise de momento com RSI e MACD simplificado
            momentum_signal = self._advanced_momentum_analysis(symbol)
            
            # Analise de volatilidade e volume
            volatility_signal = self._advanced_volatility_analysis(symbol)
            
            # Consolidacao com pesos otimizados
            final_signal = self._consolidate_advanced_signals(
                multi_tf_signal, momentum_signal, volatility_signal, market_validation
            )
            
            return final_signal
            
        except Exception as e:
            logger.error(f"Erro analise avancada {symbol}: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Erro analise'}
    
    def _advanced_multi_timeframe_analysis(self, symbol: str) -> Dict:
        """Analise multi-timeframe avancada"""
        try:
            timeframes = [
                (mt5.TIMEFRAME_M5, 'M5', 25, 0.25),   # 25% peso
                (mt5.TIMEFRAME_M15, 'M15', 35, 0.35), # 35% peso
                (mt5.TIMEFRAME_H1, 'H1', 40, 0.40)   # 40% peso
            ]
            
            signals = []
            confidences = []
            reasons = []
            
            for tf, tf_name, periods, weight in timeframes:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, periods)
                if rates is None or len(rates) < 15:
                    continue
                
                df = pd.DataFrame(rates)
                current_price = df['close'].iloc[-1]
                
                # Indicadores multiplos
                ema_10 = df['close'].tail(10).ewm(span=10).mean().iloc[-1]
                ema_20 = df['close'].tail(20).ewm(span=20).mean().iloc[-1]
                sma_50 = df['close'].tail(50).mean()
                
                # RSI
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / (loss + 1e-12)
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                # Sinal do timeframe
                bullish_signals = 0
                total_signals = 0
                
                # EMA cross
                if ema_10 > ema_20:
                    bullish_signals += 1
                total_signals += 1
                
                # Preco vs EMA
                if current_price > ema_20:
                    bullish_signals += 1
                total_signals += 1
                
                # RSI
                if 40 <= current_rsi <= 60:  # Zona neutra otimizada
                    if current_rsi < 50:
                        bullish_signals += 0.5
                    else:
                        bullish_signals -= 0.5
                elif current_rsi < 40:
                    bullish_signals += 1
                elif current_rsi > 60:
                    bullish_signals -= 1
                total_signals += 1
                
                # Determinar sinal do timeframe
                signal_strength = bullish_signals / total_signals
                
                if signal_strength > 0.6:
                    tf_signal = 'BUY'
                    confidence = min(0.9, 0.6 + signal_strength * 0.3)
                elif signal_strength < -0.6:
                    tf_signal = 'SELL'
                    confidence = min(0.9, 0.6 + abs(signal_strength) * 0.3)
                else:
                    tf_signal = 'HOLD'
                    confidence = 0.5
                
                if tf_signal in ['BUY', 'SELL']:
                    signals.append(tf_signal)
                    confidences.append(confidence * weight)
                    reasons.append(f"{tf_name}:{tf_signal}({confidence:.0%})")
            
            return {
                'signals': signals,
                'confidences': confidences,
                'reasons': reasons,
                'timeframe_count': len(signals)
            }
            
        except Exception as e:
            logger.error(f"Erro multi-TF avancado: {e}")
            return {'signals': [], 'confidences': [], 'reasons': [], 'timeframe_count': 0}
    
    def _advanced_momentum_analysis(self, symbol: str) -> Dict:
        """Analise de momento avancada"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 40)
            if rates is None or len(rates) < 25:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Dados insuficientes'}
            
            df = pd.DataFrame(rates)
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-12)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # ROC (Rate of Change)
            roc_10 = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
            current_roc = roc_10.iloc[-1]
            
            # Volume analysis
            avg_volume = df['tick_volume'].tail(20).mean()
            current_volume = df['tick_volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Price momentum
            price_change_5 = ((df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6]) * 100
            
            # Scoring system
            momentum_score = 0
            reasons = []
            
            # RSI analysis (conservative)
            if 35 <= current_rsi <= 65:
                if current_rsi < 45:  # Ligeiramente oversold
                    momentum_score += 2
                    reasons.append(f"RSI favoravel: {current_rsi:.1f}")
                elif current_rsi > 55:  # Ligeiramente overbought
                    momentum_score -= 1
                    reasons.append(f"RSI cauteloso: {current_rsi:.1f}")
                else:
                    momentum_score += 0.5
                    reasons.append(f"RSI neutro: {current_rsi:.1f}")
            elif current_rsi < 35:
                momentum_score += 3
                reasons.append(f"RSI oversold: {current_rsi:.1f}")
            else:  # RSI > 65
                momentum_score -= 2
                reasons.append(f"RSI overbought: {current_rsi:.1f}")
            
            # ROC analysis
            if abs(current_roc) < 0.3:  # Movimento estavel
                momentum_score += 1
                reasons.append(f"ROC estavel: {current_roc:.2f}%")
            elif current_roc > 0.3:
                momentum_score += 2
                reasons.append(f"ROC positivo: {current_roc:.2f}%")
            elif current_roc < -0.3:
                momentum_score -= 1
                reasons.append(f"ROC negativo: {current_roc:.2f}%")
            
            # Volume confirmation
            if volume_ratio > 2.0:
                momentum_score += 2
                reasons.append(f"Volume elevado: {volume_ratio:.1f}x")
            elif volume_ratio > 1.5:
                momentum_score += 1
                reasons.append(f"Volume acima media: {volume_ratio:.1f}x")
            
            # Price momentum
            if price_change_5 > 0.1:
                momentum_score += 1
                reasons.append(f"Momentum +{price_change_5:.2f}%")
            elif price_change_5 < -0.1:
                momentum_score -= 0.5
                reasons.append(f"Momentum {price_change_5:.2f}%")
            
            # Determine signal
            if momentum_score >= 4:
                signal = 'BUY'
                confidence = min(0.85, 0.6 + momentum_score / 20)
            elif momentum_score <= 0:
                signal = 'SELL'
                confidence = min(0.85, 0.6 + abs(momentum_score) / 20)
            else:
                signal = 'HOLD'
                confidence = 0.5
            
            return {
                'signal': signal,
                'confidence': confidence,
                'rsi': current_rsi,
                'roc': current_roc,
                'volume_ratio': volume_ratio,
                'price_momentum': price_change_5,
                'momentum_score': momentum_score,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Erro momento avancado: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Erro momento'}
    
    def _advanced_volatility_analysis(self, symbol: str) -> Dict:
        """Analise de volatilidade avancada"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 60)
            if rates is None or len(rates) < 30:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Dados volatilidade insuficientes'}
            
            df = pd.DataFrame(rates)
            
            # ATR calculation
            high_low = df['high'] - df['low']
            close_prev = df['close'].shift(1)
            high_close = abs(df['high'] - close_prev)
            low_close = abs(df['low'] - close_prev)
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            volatility_pct = (atr / current_price) * 100
            
            # Volatilidade recente vs historica
            recent_vol = true_range.tail(10).mean()
            historical_vol = true_range.mean()
            vol_ratio = recent_vol / historical_vol if historical_vol > 0 else 1.0
            
            # Bollinger Bands position
            sma_20 = df['close'].tail(20).mean()
            std_20 = df['close'].tail(20).std()
            bb_upper = sma_20 + (std_20 * 2)
            bb_lower = sma_20 - (std_20 * 2)
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
            
            # Determine volatility signal
            if 0.05 <= volatility_pct <= 0.8:  # Volatilidade ideal para trading
                if vol_ratio > 1.2:  # Volatilidade aumentando
                    signal = 'favorable'
                    confidence = 0.8
                    reason = f"Vol ideal crescendo: {volatility_pct:.3f}%"
                else:
                    signal = 'favorable'
                    confidence = 0.7
                    reason = f"Vol ideal estavel: {volatility_pct:.3f}%"
            elif volatility_pct < 0.05:  # Muito baixa
                signal = 'low_volatility'
                confidence = 0.3
                reason = f"Vol muito baixa: {volatility_pct:.3f}%"
            else:  # Muito alta
                signal = 'high_volatility'
                confidence = 0.2
                reason = f"Vol muito alta: {volatility_pct:.3f}%"
            
            return {
                'signal': signal,
                'confidence': confidence,
                'atr': atr,
                'volatility_pct': volatility_pct,
                'vol_ratio': vol_ratio,
                'bb_position': bb_position,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Erro volatilidade avancada: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Erro volatilidade'}
    
    def _consolidate_advanced_signals(self, multi_tf: Dict, momentum: Dict, 
                                    volatility: Dict, market: Dict) -> Dict:
        """Consolida sinais avancados com pesos otimizados"""
        try:
            signals = []
            confidences = []
            reasons = []
            
            # Multi-timeframe (peso 35%)
            if multi_tf.get('timeframe_count', 0) > 0:
                for signal, confidence in zip(multi_tf['signals'], multi_tf['confidences']):
                    signals.append(signal)
                    confidences.append(confidence * 0.35)
                reasons.extend(multi_tf['reasons'])
            
            # Momentum (peso 40%)
            if momentum.get('signal') in ['BUY', 'SELL']:
                signals.append(momentum['signal'])
                confidences.append(momentum['confidence'] * 0.40)
                reasons.extend(momentum.get('reasons', []))
            
            # Volatility (peso 25%)
            if volatility.get('signal') == 'favorable':
                # Adicionar sinal baseado na direcao predominante
                if signals:
                    buy_count = signals.count('BUY')
                    sell_count = signals.count('SELL')
                    if buy_count > sell_count:
                        signals.append('BUY')
                    elif sell_count > buy_count:
                        signals.append('SELL')
                confidences.append(volatility['confidence'] * 0.25)
                reasons.append(volatility.get('reason', 'Vol favoravel'))
            
            # Decisao final
            if signals and confidences:
                buy_signals = signals.count('BUY')
                sell_signals = signals.count('SELL')
                avg_confidence = sum(confidences) / len(confidences)
                
                # Critério rigoroso para teste real
                if avg_confidence >= self.min_confidence:
                    if buy_signals > sell_signals * 1.2:  # Buy predominante
                        final_signal = 'BUY'
                        final_confidence = avg_confidence
                    elif sell_signals > buy_signals * 1.2:  # Sell predominante
                        final_signal = 'SELL'
                        final_confidence = avg_confidence
                    else:
                        final_signal = 'HOLD'
                        final_confidence = avg_confidence * 0.8
                else:
                    final_signal = 'HOLD'
                    final_confidence = avg_confidence
            else:
                final_signal = 'HOLD'
                final_confidence = 0.0
                reasons = ['Sem sinais suficientes']
            
            return {
                'signal': final_signal,
                'confidence': final_confidence,
                'reasons': reasons,
                'market_conditions': market,
                'signal_breakdown': {
                    'multi_timeframe': multi_tf.get('timeframe_count', 0),
                    'momentum': momentum.get('signal', 'HOLD'),
                    'volatility': volatility.get('signal', 'neutral')
                }
            }
            
        except Exception as e:
            logger.error(f"Erro consolidacao avancada: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'reasons': ['Erro consolidacao']}
    
    def execute_real_trade(self, analysis: Dict) -> bool:
        """Executa trade real com validacao adicional"""
        try:
            symbol = analysis['symbol']
            signal = analysis['signal']
            confidence = analysis['confidence']
            current_price = analysis['current_price']
            
            if signal not in ['BUY', 'SELL']:
                logger.info(f"{symbol}: Sinal HOLD (conf: {confidence:.1%}) - Nenhuma acao")
                return False
            
            # Validacao final antes da execucao
            if confidence < self.min_confidence:
                logger.warning(f"{symbol}: Confiança {confidence:.1%} abaixo do minimo {self.min_confidence:.1%}")
                return False
            
            # Verificar limite de posicoes
            positions = mt5.positions_get()
            if positions and len(positions) >= self.max_positions:
                logger.warning(f"Limite de posicoes atingido: {len(positions)}/{self.max_positions}")
                return False
            
            logger.info(f"EXECUTANDO TRADE REAL: {signal} - {symbol} (Conf: {confidence:.1%})")
            logger.info(f"Razoes: {analysis.get('reasons', ['Sem razoes'])[0] if analysis.get('reasons') else 'Sem detalhes'}")
            
            # Calcular SL/TP dinamico baseado em ATR
            sl, tp = self.calculate_real_sl_tp(symbol, current_price, signal)
            
            # Preparar ordem
            if signal == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": self.volume_base,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,  # Tolerancia para execucao real
                "magic": 234003,  # ID unico para trades reais
                "comment": f"IA_GAIN_REAL_{signal}_C{int(confidence*100)}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Enviar ordem
            logger.info(f"Enviando ordem: {symbol} {signal} @ {price:.5f} (SL: {sl:.5f}, TP: {tp:.5f})")
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"SUCESSO! Trade real executado - Ticket: {result.order}")
                logger.info(f"Preco de entrada: {price:.5f}")
                self._register_real_trade(symbol, signal, price, sl, tp, confidence, analysis)
                self.session_stats['trades_executed'] += 1
                return True
            else:
                logger.error(f"FALHA na execucao real: {result.comment} (Codigo: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"Erro critico na execucao do trade real: {e}")
            return False
    
    def calculate_real_sl_tp(self, symbol: str, entry_price: float, signal: str) -> Tuple[float, float]:
        """Calcula SL/TP para trades reais com ATR dinamico"""
        try:
            # Obter ATR de multiplos timeframes
            atr_values = []
            
            for tf in [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1]:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, 20)
                if rates is not None and len(rates) > 0:
                    df = pd.DataFrame(rates)
                    high_low = df['high'] - df['low']
                    atr_tf = high_low.tail(14).mean() if len(high_low) >= 14 else high_low.mean()
                    atr_values.append(atr_tf)
            
            # Usar ATR medio ou padrao
            atr = sum(atr_values) / len(atr_values) if atr_values else entry_price * 0.001
            
            # Multiplicadores conservadores para teste real
            sl_multiplier = 2.0  # Stop mais largo para mercado real
            tp_multiplier = 4.0  # TP 2x o stop (ratio 1:2)
            
            if signal == 'BUY':
                stop_loss = entry_price - (atr * sl_multiplier)
                take_profit = entry_price + (atr * tp_multiplier)
            else:  # SELL
                stop_loss = entry_price + (atr * sl_multiplier)
                take_profit = entry_price - (atr * tp_multiplier)
            
            # Arredondar para 5 casas decimais (forex padrao)
            return round(stop_loss, 5), round(take_profit, 5)
            
        except Exception as e:
            logger.error(f"Erro calculo SL/TP real: {e}")
            # Valores de seguranca para mercado real
            if signal == 'BUY':
                return round(entry_price * 0.998, 5), round(entry_price * 1.004, 5)
            else:
                return round(entry_price * 1.002, 5), round(entry_price * 0.996, 5)
    
    def _register_real_trade(self, symbol: str, signal: str, price: float, 
                           sl: float, tp: float, confidence: float, analysis: Dict):
        """Registra trade real com detalhes completos"""
        trade_record = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'signal': signal,
            'entry_price': price,
            'stop_loss': sl,
            'take_profit': tp,
            'confidence': confidence,
            'volume': self.volume_base,
            'status': 'OPEN',
            'risk_reward_ratio': self.risk_reward_ratio,
            'market_conditions': analysis.get('market_conditions', {}),
            'signal_analysis': analysis.get('signal_breakdown', {}),
            'reasons': analysis.get('reasons', [])
        }
        
        self.operation_history.append(trade_record)
        self.active_positions[symbol] = trade_record
        
        logger.info(f"Trade real registrado: {symbol} {signal} @ {price:.5f}")
        logger.info(f"Risco: {abs(price - sl):.5f} | Recompensa: {abs(tp - price):.5f}")
    
    def monitor_real_time_performance(self):
        """Monitora performance em tempo real"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return
            
            current_pnl = sum(pos.profit for pos in positions)
            self.session_stats['total_pnl'] = current_pnl
            
            # Calcular drawdown
            if current_pnl < self.session_stats['max_drawdown']:
                self.session_stats['max_drawdown'] = current_pnl
            
            # Atualizar trades vencedores/perdedores
            for pos in positions:
                if pos.profit > 0:
                    self.session_stats['trades_won'] += 1
                elif pos.profit < 0:
                    self.session_stats['trades_lost'] += 1
            
            # Verificar alertas
            self._check_real_time_alerts(current_pnl, len(positions))
            
        except Exception as e:
            logger.error(f"Erro monitoramento tempo real: {e}")
    
    def _check_real_time_alerts(self, current_pnl: float, position_count: int):
        """Verifica alertas em tempo real"""
        try:
            # Alerta de drawdown
            max_allowed_loss = self.session_stats['start_balance'] * 0.02  # 2% max loss
            if current_pnl < -max_allowed_loss:
                logger.warning(f"ALERTA: Drawdown atingiu ${current_pnl:.2f} (max: ${max_allowed_loss:.2f})")
            
            # Alerta de numero de posicoes
            if position_count >= self.max_positions:
                logger.warning(f"ALERTA: Numero maximo de posicoes atingido: {position_count}")
            
            # Alerta de tempo de sessao
            session_duration = datetime.now() - self.session_stats['start_time']
            if session_duration.total_seconds() > 3600:  # 1 hora
                logger.info(f"INFO: Sessao ativa por {session_duration.total_seconds()/60:.0f} minutos")
            
        except Exception as e:
            logger.error(f"Erro alertas tempo real: {e}")
    
    def scan_and_trade_real_time(self) -> int:
        """Escaneia e executa trades em tempo real"""
        try:
            logger.info("Iniciando scan em tempo real...")
            trades_executed = 0
            
            # Verificar condicoes gerais primeiro
            if not self.running:
                return 0
            
            positions = mt5.positions_get()
            current_positions = len(positions) if positions else 0
            
            if current_positions >= self.max_positions:
                logger.warning(f"Max posicoes atingido: {current_positions}/{self.max_positions}")
                return 0
            
            # Analisar cada simbolo
            for symbol in self.trading_symbols:
                if not self.running:
                    break
                
                logger.info(f"Analisando em tempo real: {symbol}")
                
                # Analise avancada em tempo real
                analysis = self.advanced_real_time_analysis(symbol)
                
                if analysis['signal'] == 'HOLD':
                    logger.info(f"{symbol}: HOLD - {analysis.get('reason', 'Sem sinal')}")
                    continue
                
                # Preparar dados para execucao
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info:
                    current_price = (symbol_info.ask + symbol_info.bid) / 2
                    analysis['symbol'] = symbol
                    analysis['current_price'] = current_price
                    
                    logger.info(f"SINAL DETECTADO: {symbol} - {analysis['signal']} (Conf: {analysis['confidence']:.1%})")
                    
                    # Executar trade real
                    if self.execute_real_trade(analysis):
                        trades_executed += 1
                        logger.info(f"Trade real executado: {symbol}")
                        
                        # Pausa entre trades
                        time.sleep(5)
                
                # Pausa entre analises
                time.sleep(2)
            
            logger.info(f"Scan tempo real concluido - {trades_executed} trades executados")
            return trades_executed
            
        except Exception as e:
            logger.error(f"Erro scan tempo real: {e}")
            return 0
    
    def run_real_time_test(self, max_cycles: int = 10, cycle_interval: int = 180):
        """Executa teste em tempo real"""
        try:
            logger.info("INICIANDO TESTE EM TEMPO REAL MERCADO")
            logger.info("="*70)
            logger.info(f"Ciclos maximos: {max_cycles}")
            logger.info(f"Intervalo: {cycle_interval}s")
            logger.info(f"Saldo inicial: ${self.account_info.balance:.2f}")
            logger.info("="*70)
            logger.info("AVISO: ESTE E UM TESTE REAL COM EXECUCAO DE TRADES!")
            logger.info("Parametros ultra-conservadores ativos")
            logger.info("="*70)
            
            total_trades = 0
            cycle_count = 0
            
            while self.running and cycle_count < max_cycles:
                cycle_count += 1
                cycle_start = datetime.now()
                
                logger.info(f"\nCICLO {cycle_count}/{max_cycles} - {cycle_start.strftime('%H:%M:%S')}")
                logger.info("-" * 50)
                
                # Monitorar performance
                self.monitor_real_time_performance()
                
                # Executar scan e trades
                trades_in_cycle = self.scan_and_trade_real_time()
                total_trades += trades_in_cycle
                
                logger.info(f"Ciclo {cycle_count} concluido - {trades_in_cycle} trades")
                
                # Verificar condicoes de parada
                if not self.running:
                    logger.info("Teste interrompido pelo usuario")
                    break
                
                # Verificar limite de perda
                current_pnl = self.session_stats['total_pnl']
                max_loss_allowed = self.session_stats['start_balance'] * 0.02  # 2% max
                if current_pnl < -max_loss_allowed:
                    logger.warning(f"Limite de perda atingido: ${current_pnl:.2f}")
                    break
                
                # Aguardar proximo ciclo (se nao for o ultimo)
                if self.running and cycle_count < max_cycles:
                    logger.info(f"Aguardando proximo ciclo...")
                    time.sleep(cycle_interval)
            
            # Resumo final
            self._display_real_time_summary(total_trades, cycle_count)
            
        except KeyboardInterrupt:
            logger.info("\nTeste interrompido manualmente")
        except Exception as e:
            logger.error(f"Erro durante teste tempo real: {e}")
        finally:
            self.running = False
    
    def _display_real_time_summary(self, total_trades: int, cycles_completed: int):
        """Exibe resumo final do teste em tempo real"""
        logger.info("\n" + "="*70)
        logger.info("RESUMO FINAL - TESTE EM TEMPO REAL MERCADO")
        logger.info("="*70)
        
        final_balance = mt5.account_info().balance
        session_pnl = final_balance - self.session_stats['start_balance']
        pnl_percentage = (session_pnl / self.session_stats['start_balance']) * 100
        session_duration = datetime.now() - self.session_stats['start_time']
        
        logger.info(f"Saldo final: ${final_balance:.2f}")
        logger.info(f"PnL do teste: ${session_pnl:.2f} ({pnl_percentage:+.2f}%)")
        logger.info(f"Total de trades: {total_trades}")
        logger.info(f"Ciclos completados: {cycles_completed}")
        logger.info(f"Duracao: {session_duration.total_seconds()/60:.1f} minutos")
        logger.info(f"Drawdown maximo: ${self.session_stats['max_drawdown']:.2f}")
        
        if total_trades > 0:
            logger.info(f"Trades vencedores: {self.session_stats['trades_won']}")
            logger.info(f"Trades perdedores: {self.session_stats['trades_lost']}")
        
        # Salvar relatorio detalhado
        self._save_real_time_report(session_pnl, total_trades, cycles_completed, session_duration)
        
        logger.info("\nTeste em tempo real concluido!")
        logger.info("="*70)
    
    def _save_real_time_report(self, pnl: float, total_trades: int, cycles: int, duration: timedelta):
        """Salva relatorio detalhado do teste"""
        try:
            report = {
                'test_type': 'real_time_market_test',
                'start_time': self.session_stats['start_time'].isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': duration.total_seconds() / 60,
                'initial_balance': self.session_stats['start_balance'],
                'final_balance': mt5.account_info().balance,
                'pnl': pnl,
                'pnl_percentage': (pnl / self.session_stats['start_balance']) * 100,
                'total_trades': total_trades,
                'cycles_completed': cycles,
                'trades_won': self.session_stats['trades_won'],
                'trades_lost': self.session_stats['trades_lost'],
                'max_drawdown': self.session_stats['max_drawdown'],
                'parameters_used': {
                    'max_risk_per_trade': self.max_risk_per_trade,
                    'min_confidence': self.min_confidence,
                    'risk_reward_ratio': self.risk_reward_ratio,
                    'max_positions': self.max_positions,
                    'volume_base': self.volume_base,
                    'filters': self.filters
                },
                'operation_history': self.operation_history,
                'active_positions_at_end': list(self.active_positions.keys())
            }
            
            filename = f"real_time_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatorio detalhado salvo: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatorio: {e}")

def main():
    """Funcao principal para teste em tempo real"""
    print("IA GAIN + MetaTrader 5 - TESTE EM TEMPO REAL MERCADO")
    print("="*70)
    print("TESTE REAL COM EXECUCAO DE TRADES!")
    print("Parametros ultra-conservadores:")
    print(f"   • Risco por trade: {0.5}% (ultra conservador)")
    print(f"   • Confiança minima: {60}%")
    print(f"   • Volume: 0.01 lotes")
    print(f"   • Max posicoes: 3")
    print(f"   • Limite perda: 2%")
    print("="*70)
    
    # Confirmacao de seguranca
    response = input("\nCONFIRMA EXECUCAO DE TESTE REAL COM TRADES? (SIM/NAO): ").upper().strip()
    if response != 'SIM':
        print("Teste cancelado")
        return
    
    # Configurar parametros
    try:
        max_cycles = int(input("Numero maximo de ciclos (padrao: 10): ") or "10")
        if max_cycles < 1 or max_cycles > 50:
            print("Ciclos devem ser entre 1 e 50")
            return
    except ValueError:
        print("Valor invalido, usando 10 ciclos")
        max_cycles = 10
    
    try:
        cycle_interval = int(input("Intervalo entre ciclos em segundos (padrao: 180): ") or "180")
        if cycle_interval < 60 or cycle_interval > 3600:
            print("Intervalo deve ser entre 60s e 3600s")
            return
    except ValueError:
        print("Valor invalido, usando 180s")
        cycle_interval = 180
    
    # Criar tester
    tester = IA_GAIN_RealTimeTest()
    
    # Conectar
    if not tester.connect_to_mt5():
        print("Falha ao conectar ao MT5")
        return
    
    try:
        # Executar teste
        tester.run_real_time_test(max_cycles, cycle_interval)
    except Exception as e:
        logger.error(f"Erro fatal no teste: {e}")
    finally:
        if tester.connected:
            mt5.shutdown()
            print("Desconectado do MT5")

if __name__ == "__main__":
    main()