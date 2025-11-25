#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - TRADING AO VIVO OTIMIZADO
Versão otimizada com parâmetros ajustados para mercado atual
"""

import MetaTrader5 as mt5
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IA_GAIN_LiveTradingOptimized:
    """Trading ao vivo otimizado para condições de mercado atuais"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        
        # Parâmetros OTIMIZADOS para mercado atual
        self.max_positions = 5  # Aumentado para mais oportunidades
        self.max_risk_per_trade = 0.01  # Reduzido para 1% (mais conservador)
        self.min_confidence = 0.55  # Reduzido para 55% (mais flexível)
        self.risk_reward_ratio = 2.0  # Aumentado para 1:2 (melhor R/R)
        self.volume_base = 0.01  # Volume mínimo para teste
        
        # Filtros OTIMIZADOS
        self.filters = {
            'max_spread': 50,  # Aumentado para 50 pontos (mercado volátil)
            'min_volatility': 0.0001,  # Reduzido para detectar movimentos pequenos
            'max_volatility': 0.02,  # Aumentado para tolerar volatilidade
            'volume_threshold': 1.5,  # Reduzido para 1.5x (mais sensível)
            'trend_confirmation_periods': 2,  # Reduzido para 2 períodos
        }
        
        # Símbolos otimizados (baseado no que temos disponível)
        self.trading_symbols = [
            'EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm',
            'USDCADm', 'NZDUSDm', 'EURJPYm', 'GBPJPYm', 'AUDJPYm'
        ]
        
        # Horário estendido (mercado forex 24h)
        self.trading_hours = {
            'start': 0,   # 00:00
            'end': 24,    # 24:00 (24 horas)
            'avoid_news': True,  # Evitar horários de notícias
        }
        
        # Estatísticas
        self.session_stats = {
            'trades_executed': 0,
            'trades_won': 0,
            'trades_lost': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'start_balance': 0.0,
        }
        
        self.operation_history = []
    
    def connect_to_mt5(self) -> bool:
        """Conecta ao MetaTrader 5"""
        try:
            logger.info("🔌 Conectando ao MetaTrader 5 (Otimizado)...")
            
            if not mt5.initialize():
                logger.error(f"❌ Falha ao inicializar MT5: {mt5.last_error()}")
                return False
            
            self.account_info = mt5.account_info()
            if self.account_info is None:
                logger.error("❌ Não foi possível obter informações da conta")
                return False
            
            self.session_stats['start_balance'] = self.account_info.balance
            
            logger.info(f"✅ Conectado! Conta: {self.account_info.login}")
            logger.info(f"💰 Saldo: ${self.account_info.balance:.2f}")
            logger.info(f"🏢 Servidor: {self.account_info.server}")
            logger.info(f"📊 Parâmetros otimizados carregados")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar MT5: {e}")
            return False
    
    def check_trading_conditions(self) -> bool:
        """Verifica condições gerais de trading"""
        try:
            # Verificar número de posições
            positions = mt5.positions_get()
            open_positions = len(positions) if positions else 0
            
            if open_positions >= self.max_positions:
                logger.warning(f"⚠️ Máximo de posições: {open_positions}/{self.max_positions}")
                return False
            
            # Verificar drawdown
            current_pnl = sum(pos.profit for pos in positions) if positions else 0
            current_equity = self.account_info.equity
            max_loss = self.session_stats['start_balance'] * 0.03  # 3% max loss per session
            
            if current_pnl < -max_loss:
                logger.warning(f"⚠️ Limite de perda atingido: ${current_pnl:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar condições: {e}")
            return False
    
    def advanced_market_scanner(self, symbol: str) -> Dict:
        """Scanner avançado de mercado com múltiplos filtros otimizados"""
        try:
            if not mt5.symbol_select(symbol, True):
                return {'error': 'Símbolo não disponível'}
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'error': 'Info não disponível'}
            
            current_price = (symbol_info.ask + symbol_info.bid) / 2
            
            # Scanner 1: Análise de Spread
            if symbol_info.spread > self.filters['max_spread']:
                return {'error': f'Spread alto: {symbol_info.spread}'}
            
            # Scanner 2: Análise Multi-Timeframe Otimizada
            scanner_results = self._multi_timeframe_scanner(symbol)
            
            # Scanner 3: Análise de Momento
            momentum_analysis = self._momentum_scanner(symbol)
            
            # Scanner 4: Análise de Volatilidade
            volatility_analysis = self._volatility_scanner(symbol)
            
            # Consolidar resultados
            final_signal = self._consolidate_scanner_results(
                scanner_results, momentum_analysis, volatility_analysis
            )
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'spread': symbol_info.spread,
                'signal': final_signal['signal'],
                'confidence': final_signal['confidence'],
                'reasons': final_signal['reasons'],
                'timestamp': datetime.now(),
                'individual_analyses': {
                    'multi_timeframe': scanner_results,
                    'momentum': momentum_analysis,
                    'volatility': volatility_analysis
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no scanner {symbol}: {e}")
            return {'error': str(e)}
    
    def _multi_timeframe_scanner(self, symbol: str) -> Dict:
        """Scanner multi-timeframe otimizado"""
        try:
            # Timeframes: M5, M15, H1 (mais ágeis)
            timeframes = [
                (mt5.TIMEFRAME_M5, 'M5', 20),
                (mt5.TIMEFRAME_M15, 'M15', 30),
                (mt5.TIMEFRAME_H1, 'H1', 24)
            ]
            
            timeframe_signals = {}
            bullish_count = 0
            bearish_count = 0
            
            for tf, tf_name, periods in timeframes:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, periods)
                if rates is None or len(rates) < 10:
                    timeframe_signals[tf_name] = 'neutral'
                    continue
                
                df = pd.DataFrame(rates)
                
                # Análise rápida: preço vs médias móveis
                current_price = df['close'].iloc[-1]
                sma_fast = df['close'].tail(5).mean()  # 5 períodos
                sma_slow = df['close'].tail(10).mean()  # 10 períodos
                
                if current_price > sma_fast and sma_fast > sma_slow:
                    signal = 'bullish'
                    bullish_count += 1
                elif current_price < sma_fast and sma_fast < sma_slow:
                    signal = 'bearish'
                    bearish_count += 1
                else:
                    signal = 'neutral'
                
                timeframe_signals[tf_name] = signal
            
            # Consolidação com pesos diferentes
            total_signals = len([s for s in timeframe_signals.values() if s != 'neutral'])
            
            if bullish_count >= 2:  # Maioria bullish
                overall_signal = 'bullish'
                confidence = 0.6 + (bullish_count / 3) * 0.3  # 60% a 90%
            elif bearish_count >= 2:  # Maioria bearish
                overall_signal = 'bearish'
                confidence = 0.6 + (bearish_count / 3) * 0.3  # 60% a 90%
            else:
                overall_signal = 'neutral'
                confidence = 0.5
            
            return {
                'individual_timeframes': timeframe_signals,
                'overall_signal': overall_signal,
                'confidence': confidence,
                'bullish_votes': bullish_count,
                'bearish_votes': bearish_count,
                'total_votes': total_signals
            }
            
        except Exception as e:
            logger.error(f"Erro scanner multi-timeframe: {e}")
            return {'overall_signal': 'neutral', 'confidence': 0.5, 'error': str(e)}
    
    def _momentum_scanner(self, symbol: str) -> Dict:
        """Scanner de momento com indicadores rápidos"""
        try:
            # Dados M5 para análise de momento
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 30)
            if rates is None or len(rates) < 20:
                return {'signal': 'neutral', 'confidence': 0.5}
            
            df = pd.DataFrame(rates)
            
            # RSI de 14 períodos
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-12)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # ROC (Rate of Change) - 10 períodos
            roc = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
            current_roc = roc.iloc[-1]
            
            # Análise de volume
            avg_volume = df['tick_volume'].tail(20).mean()
            current_volume = df['tick_volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Sinais de momento
            momentum_score = 0
            reasons = []
            
            # RSI
            if 40 <= current_rsi <= 60:  # Zona neutra otimizada
                momentum_score += 1
                reasons.append(f"RSI neutro: {current_rsi:.1f}")
            elif current_rsi < 40:  # Ligeiramente oversold
                momentum_score += 2
                reasons.append(f"RSI baixo: {current_rsi:.1f}")
            elif current_rsi > 60:  # Ligeiramente overbought
                momentum_score -= 1
                reasons.append(f"RSI alto: {current_rsi:.1f}")
            
            # ROC
            if abs(current_roc) < 0.2:  # Momento estável
                momentum_score += 1
                reasons.append(f"ROC estável: {current_roc:.2f}%")
            elif current_roc > 0.2:  # Momento positivo
                momentum_score += 2
                reasons.append(f"ROC positivo: {current_roc:.2f}%")
            elif current_roc < -0.2:  # Momento negativo
                momentum_score -= 1
                reasons.append(f"ROC negativo: {current_roc:.2f}%")
            
            # Volume
            if volume_ratio > 1.5:  # Volume acima da média
                momentum_score += 1
                reasons.append(f"Volume elevado: {volume_ratio:.1f}x")
            
            # Determinar sinal final
            if momentum_score >= 3:
                signal = 'bullish'
                confidence = 0.6 + min(0.3, momentum_score / 10)
            elif momentum_score <= 0:
                signal = 'bearish'
                confidence = 0.6 + min(0.3, abs(momentum_score) / 10)
            else:
                signal = 'neutral'
                confidence = 0.5
            
            return {
                'signal': signal,
                'confidence': confidence,
                'rsi': current_rsi,
                'roc': current_roc,
                'volume_ratio': volume_ratio,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Erro scanner momento: {e}")
            return {'signal': 'neutral', 'confidence': 0.5, 'error': str(e)}
    
    def _volatility_scanner(self, symbol: str) -> Dict:
        """Scanner de volatilidade para timing de entrada"""
        try:
            # M15 para análise de volatilidade
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 50)
            if rates is None or len(rates) < 20:
                return {'signal': 'neutral', 'confidence': 0.5}
            
            df = pd.DataFrame(rates)
            
            # ATR (Average True Range) simplificado
            high_low = df['high'] - df['low']
            close_prev = df['close'].shift(1)
            high_close = abs(df['high'] - close_prev)
            low_close = abs(df['low'] - close_prev)
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[-1]
            
            # Volatilidade percentual
            current_price = df['close'].iloc[-1]
            volatility_pct = (atr / current_price) * 100
            
            # Volatilidade recente vs histórica
            recent_vol = true_range.tail(10).mean()
            historical_vol = true_range.mean()
            vol_ratio = recent_vol / historical_vol if historical_vol > 0 else 1.0
            
            # Determinar sinal baseado na volatilidade
            if self.filters['min_volatility'] <= volatility_pct <= 0.5:  # Volatilidade "normal"
                signal = 'favorable'
                confidence = 0.7
                reason = f"Volatilidade ideal: {volatility_pct:.3f}%"
            elif volatility_pct < self.filters['min_volatility']:  # Muito baixa
                signal = 'low_volatility'
                confidence = 0.4
                reason = f"Volatilidade muito baixa: {volatility_pct:.3f}%"
            else:  # Muito alta
                signal = 'high_volatility'
                confidence = 0.3
                reason = f"Volatilidade alta: {volatility_pct:.3f}%"
            
            return {
                'signal': signal,
                'confidence': confidence,
                'atr': atr,
                'volatility_pct': volatility_pct,
                'vol_ratio': vol_ratio,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Erro scanner volatilidade: {e}")
            return {'signal': 'neutral', 'confidence': 0.5, 'error': str(e)}
    
    def _consolidate_scanner_results(self, multi_tf: Dict, momentum: Dict, volatility: Dict) -> Dict:
        """Consolida todos os scanners em um sinal final"""
        try:
            signals = []
            confidences = []
            reasons = []
            
            # Multi-timeframe (peso 40%)
            if multi_tf.get('overall_signal') == 'bullish':
                signals.append('BUY')
                confidences.append(multi_tf['confidence'] * 0.4)
                reasons.append(f"Multi-TF: Alta conf ({multi_tf['confidence']:.0%})")
            elif multi_tf.get('overall_signal') == 'bearish':
                signals.append('SELL')
                confidences.append(multi_tf['confidence'] * 0.4)
                reasons.append(f"Multi-TF: Baixa conf ({multi_tf['confidence']:.0%})")
            
            # Momentum (peso 35%)
            if momentum.get('signal') == 'bullish':
                signals.append('BUY')
                confidences.append(momentum['confidence'] * 0.35)
                reasons.extend(momentum.get('reasons', []))
            elif momentum.get('signal') == 'bearish':
                signals.append('SELL')
                confidences.append(momentum['confidence'] * 0.35)
                reasons.extend(momentum.get('reasons', []))
            
            # Volatilidade (peso 25%)
            if volatility.get('signal') == 'favorable':
                signals.append('BUY' if len([s for s in signals if s == 'BUY']) > len([s for s in signals if s == 'SELL']) else 'SELL')
                confidences.append(volatility['confidence'] * 0.25)
                reasons.append(volatility.get('reason', 'Volatilidade favorável'))
            
            # Decisão final
            if signals:
                buy_signals = signals.count('BUY')
                sell_signals = signals.count('SELL')
                avg_confidence = sum(confidences) / len(confidences)
                
                if buy_signals > sell_signals and avg_confidence >= self.min_confidence:
                    final_signal = 'BUY'
                    final_confidence = avg_confidence
                elif sell_signals > buy_signals and avg_confidence >= self.min_confidence:
                    final_signal = 'SELL'
                    final_confidence = avg_confidence
                else:
                    final_signal = 'HOLD'
                    final_confidence = 0.5
            else:
                final_signal = 'HOLD'
                final_confidence = 0.5
            
            return {
                'signal': final_signal,
                'confidence': final_confidence,
                'reasons': reasons,
                'individual_signals': {
                    'multi_timeframe': multi_tf.get('overall_signal', 'neutral'),
                    'momentum': momentum.get('signal', 'neutral'),
                    'volatility': volatility.get('signal', 'neutral')
                }
            }
            
        except Exception as e:
            logger.error(f"Erro consolidação: {e}")
            return {'signal': 'HOLD', 'confidence': 0.5, 'reasons': ['Erro na consolidação']}
    
    def execute_live_trade(self, analysis: Dict) -> bool:
        """Executa trade ao vivo com precisão"""
        try:
            symbol = analysis['symbol']
            signal = analysis['signal']
            confidence = analysis['confidence']
            current_price = analysis['current_price']
            
            if signal not in ['BUY', 'SELL']:
                logger.info(f"ℹ️ {symbol}: Sinal HOLD, nenhuma ação necessária")
                return False
            
            logger.info(f"🚀 Executando {signal} para {symbol} (Confiança: {confidence:.1%})")
            
            # Calcular SL/TP baseado na volatilidade
            sl, tp = self.calculate_dynamic_sl_tp(symbol, current_price, signal)
            
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
                "deviation": 15,  # Maior tolerância
                "magic": 234001,  # Identificador único
                "comment": f"IA_GAIN_{signal}_C{int(confidence*100)}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Ordem executada! Ticket: {result.order}")
                self._register_trade(symbol, signal, price, sl, tp, confidence)
                self.session_stats['trades_executed'] += 1
                return True
            else:
                logger.error(f"❌ Falha na ordem: {result.comment} (Código: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar trade: {e}")
            return False
    
    def calculate_dynamic_sl_tp(self, symbol: str, entry_price: float, signal: str) -> Tuple[float, float]:
        """Calcula SL/TP dinâmico baseado na volatilidade atual"""
        try:
            # Obter ATR recente
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 20)
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                high_low = df['high'] - df['low']
                atr = high_low.tail(14).mean()
            else:
                atr = entry_price * 0.0005  # ATR padrão
            
            # Ajustar multiplicadores baseado no sinal
            sl_multiplier = 1.2  # Stop mais apertado
            tp_multiplier = 2.4  # TP maior (ratio 1:2)
            
            if signal == 'BUY':
                stop_loss = entry_price - (atr * sl_multiplier)
                take_profit = entry_price + (atr * tp_multiplier)
            else:  # SELL
                stop_loss = entry_price + (atr * sl_multiplier)
                take_profit = entry_price - (atr * tp_multiplier)
            
            return round(stop_loss, 5), round(take_profit, 5)
            
        except Exception as e:
            logger.error(f"Erro cálculo SL/TP: {e}")
            # Valores de segurança
            if signal == 'BUY':
                return entry_price * 0.998, entry_price * 1.004
            else:
                return entry_price * 1.002, entry_price * 0.996
    
    def _register_trade(self, symbol: str, signal: str, price: float, 
                       sl: float, tp: float, confidence: float):
        """Registra trade executado"""
        trade_record = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'signal': signal,
            'entry_price': price,
            'stop_loss': sl,
            'take_profit': tp,
            'confidence': confidence,
            'volume': self.volume_base,
            'status': 'OPEN'
        }
        
        self.operation_history.append(trade_record)
        logger.info(f"📊 Trade registrado: {symbol} {signal} @ {price:.5f}")
    
    def scan_and_trade_optimized(self) -> int:
        """Escaneia e executa trades otimizados"""
        try:
            logger.info("🔍 Iniciando scan otimizado...")
            trades_executed = 0
            
            # Embaralhar símbolos para evitar viés
            import random
            symbols_to_scan = self.trading_symbols.copy()
            random.shuffle(symbols_to_scan)
            
            for symbol in symbols_to_scan:
                logger.info(f"📊 Analisando {symbol}...")
                
                # Análise completa otimizada
                analysis = self.advanced_market_scanner(symbol)
                
                if 'error' in analysis:
                    logger.warning(f"⚠️ {symbol}: {analysis['error']}")
                    continue
                
                signal = analysis['signal']
                confidence = analysis['confidence']
                
                logger.info(f"🎯 {symbol}: {signal} (Confiança: {confidence:.1%})")
                
                # Executar se atender aos critérios
                if signal in ['BUY', 'SELL'] and confidence >= self.min_confidence:
                    if self.execute_live_trade(analysis):
                        trades_executed += 1
                        logger.info(f"✅ Trade executado: {symbol}")
                        
                        # Pequena pausa entre trades
                        time.sleep(2)
                
                # Pequena pausa entre análises
                time.sleep(0.5)
            
            logger.info(f"✅ Scan concluído - {trades_executados} trades executados")
            return trades_executed
            
        except Exception as e:
            logger.error(f"❌ Erro no scan otimizado: {e}")
            return 0
    
    def monitor_session_performance(self):
        """Monitora performance da sessão"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return
            
            current_pnl = sum(pos.profit for pos in positions)
            self.session_stats['total_pnl'] = current_pnl
            
            # Calcular drawdown
            if current_pnl < self.session_stats['max_drawdown']:
                self.session_stats['max_drawdown'] = current_pnl
            
            # Contar trades vencedores/perdedores
            for pos in positions:
                if pos.profit > 0:
                    self.session_stats['trades_won'] += 1
                elif pos.profit < 0:
                    self.session_stats['trades_lost'] += 1
            
            logger.info(f"📈 Performance da sessão:")
            logger.info(f"   💰 PnL Total: ${current_pnl:.2f}")
            logger.info(f"   📊 Trades: {len(positions)} abertos")
            logger.info(f"   📉 Drawdown Máx: ${self.session_stats['max_drawdown']:.2f}")
            
        except Exception as e:
            logger.error(f"Erro ao monitorar performance: {e}")
    
    def run_optimized_trading_session(self, cycles: int = 3, cycle_interval: int = 300):
        """Executa sessão de trading otimizada"""
        try:
            logger.info("🚀 INICIANDO SESSÃO DE TRADING OTIMIZADA")
            logger.info("="*60)
            logger.info(f"🔄 Ciclos: {cycles}")
            logger.info(f"⏱️  Intervalo: {cycle_interval}s")
            logger.info(f"💰 Saldo inicial: ${self.account_info.balance:.2f}")
            logger.info("="*60)
            
            total_trades = 0
            
            for cycle in range(1, cycles + 1):
                logger.info(f"\n🔄 CICLO {cycle}/{cycles} - {datetime.now().strftime('%H:%M:%S')}")
                logger.info("-"*40)
                
                # Verificar condições
                if not self.check_trading_conditions():
                    logger.warning("⚠️ Condições não favoráveis, pulando ciclo")
                    time.sleep(cycle_interval)
                    continue
                
                # Monitorar performance
                self.monitor_session_performance()
                
                # Executar scan e trades
                trades_in_cycle = self.scan_and_trade_optimized()
                total_trades += trades_in_cycle
                
                logger.info(f"✅ Ciclo {cycle} concluído - {trades_in_cycle} trades")
                
                # Aguardar próximo ciclo (se não for o último)
                if cycle < cycles:
                    logger.info(f"⏰ Aguardando próximo ciclo...")
                    time.sleep(cycle_interval)
            
            # Resumo final
            self._display_final_summary(total_trades)
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Sessão interrompida pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro durante sessão: {e}")
    
    def _display_final_summary(self, total_trades: int):
        """Exibe resumo final da sessão"""
        logger.info("\n" + "="*60)
        logger.info("🏁 RESUMO FINAL DA SESSÃO OTIMIZADA")
        logger.info("="*60)
        
        final_balance = mt5.account_info().balance
        session_pnl = final_balance - self.session_stats['start_balance']
        pnl_percentage = (session_pnl / self.session_stats['start_balance']) * 100
        
        logger.info(f"💰 Saldo final: ${final_balance:.2f}")
        logger.info(f"📈 PnL da sessão: ${session_pnl:.2f} ({pnl_percentage:+.2f}%)")
        logger.info(f"📊 Total de trades: {total_trades}")
        logger.info(f"📉 Drawdown máximo: ${self.session_stats['max_drawdown']:.2f}")
        
        if total_trades > 0:
            logger.info(f"🏆 Trades vencedores: {self.session_stats['trades_won']}")
            logger.info(f"😞 Trades perdedores: {self.session_stats['trades_lost']}")
        
        # Salvar relatório
        self._save_session_report(session_pnl, total_trades)
        
        logger.info("\n✅ Sessão de trading otimizada concluída!")
    
    def _save_session_report(self, pnl: float, total_trades: int):
        """Salva relatório detalhado da sessão"""
        try:
            report = {
                'session_type': 'optimized_live_trading',
                'start_time': datetime.now().isoformat(),
                'initial_balance': self.session_stats['start_balance'],
                'final_balance': mt5.account_info().balance,
                'pnl': pnl,
                'pnl_percentage': (pnl / self.session_stats['start_balance']) * 100,
                'total_trades': total_trades,
                'trades_won': self.session_stats['trades_won'],
                'trades_lost': self.session_stats['trades_lost'],
                'max_drawdown': self.session_stats['max_drawdown'],
                'parameters_used': {
                    'min_confidence': self.min_confidence,
                    'volume_base': self.volume_base,
                    'risk_reward_ratio': self.risk_reward_ratio,
                    'max_positions': self.max_positions
                },
                'operation_history': self.operation_history
            }
            
            filename = f"optimized_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"📄 Relatório salvo: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    print("🚀 IA GAIN + MetaTrader 5 - TRADING OTIMIZADO AO VIVO")
    print("="*60)
    print("⚠️  AVISO: Este script executará operações reais!")
    print("📊 Parâmetros otimizados para mercado atual:")
    print("   • Confiança mínima: 55% (mais flexível)")
    print("   • Volume: 0.01 lotes")
    print("   • R/R Ratio: 1:2")
    print("   • Stop dinâmico baseado em ATR")
    print("="*60)
    
    # Confirmação
    response = input("\nDeseja iniciar trading ao vivo otimizado? (SIM/NÃO): ").upper().strip()
    if response != 'SIM':
        print("❌ Operação cancelada")
        return
    
    # Configurar sessão
    try:
        cycles = int(input("Número de ciclos (padrão: 3): ") or "3")
        if cycles < 1 or cycles > 10:
            print("❌ Ciclos devem ser entre 1 e 10")
            return
    except ValueError:
        print("❌ Valor inválido, usando 3 ciclos")
        cycles = 3
    
    try:
        interval = int(input("Intervalo entre ciclos em segundos (padrão: 300): ") or "300")
        if interval < 60 or interval > 1800:
            print("❌ Intervalo deve ser entre 60s e 1800s")
            return
    except ValueError:
        print("❌ Valor inválido, usando 300s")
        interval = 300
    
    # Criar trader
    trader = IA_GAIN_LiveTradingOptimized()
    
    # Conectar
    if not trader.connect_to_mt5():
        print("❌ Falha ao conectar ao MT5")
        return
    
    try:
        # Executar sessão
        trader.run_optimized_trading_session(cycles, interval)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
    finally:
        if trader.connected:
            mt5.shutdown()
            print("🔌 Desconectado do MT5")

if __name__ == "__main__":
    main()