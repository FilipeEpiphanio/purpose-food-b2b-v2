#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - TRADING AO VIVO OTIMIZADO AUTO
Versao automatica com parametros conservadores otimizados
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
        logging.FileHandler('live_trading_auto.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IA_GAIN_LiveTradingAuto:
    """Trading ao vivo automatico com parametros conservadores"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        
        # PARAMETROS CONSERVADORES OTIMIZADOS
        self.max_positions = 5  # Max 5 posicoes abertas
        self.max_risk_per_trade = 0.01  # 1% risco por trade
        self.min_confidence = 0.55  # 55% confianca minima
        self.risk_reward_ratio = 2.0  # 1:2 ratio
        self.volume_base = 0.01  # Volume minimo
        
        # Filtros otimizados
        self.filters = {
            'max_spread': 50,
            'min_volatility': 0.0001,
            'max_volatility': 0.02,
            'volume_threshold': 1.5,
            'trend_confirmation_periods': 2,
        }
        
        # Simbolos principais forex
        self.trading_symbols = [
            'EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm',
            'USDCADm', 'NZDUSDm', 'EURJPYm', 'GBPJPYm', 'AUDJPYm'
        ]
        
        # Estatisticas
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
            logger.info("Conectando ao MetaTrader 5...")
            
            if not mt5.initialize():
                logger.error(f"Falha ao inicializar MT5: {mt5.last_error()}")
                return False
            
            self.account_info = mt5.account_info()
            if self.account_info is None:
                logger.error("Nao foi possivel obter informacoes da conta")
                return False
            
            self.session_stats['start_balance'] = self.account_info.balance
            
            logger.info(f"Conectado! Conta: {self.account_info.login}")
            logger.info(f"Saldo: ${self.account_info.balance:.2f}")
            logger.info(f"Servidor: {self.account_info.server}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar MT5: {e}")
            return False
    
    def check_trading_conditions(self) -> bool:
        """Verifica condicoes de trading conservadoras"""
        try:
            positions = mt5.positions_get()
            open_positions = len(positions) if positions else 0
            
            if open_positions >= self.max_positions:
                logger.warning(f"Maximo de posicoes atingido: {open_positions}/{self.max_positions}")
                return False
            
            # Verificar drawdown diario (4.5% max)
            current_pnl = sum(pos.profit for pos in positions) if positions else 0
            max_daily_loss = self.session_stats['start_balance'] * 0.045
            
            if current_pnl < -max_daily_loss:
                logger.warning(f"Limite diario atingido: ${current_pnl:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar condicoes: {e}")
            return False
    
    def advanced_market_scanner(self, symbol: str) -> Dict:
        """Scanner multi-filtro conservador"""
        try:
            if not mt5.symbol_select(symbol, True):
                return {'error': 'Simbolo nao disponivel'}
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'error': 'Info nao disponivel'}
            
            current_price = (symbol_info.ask + symbol_info.bid) / 2
            
            # Filtro de spread
            if symbol_info.spread > self.filters['max_spread']:
                return {'error': f'Spread alto: {symbol_info.spread}'}
            
            # Analise Multi-Timeframe
            scanner_results = self._multi_timeframe_analysis(symbol)
            
            # Analise de Momento
            momentum_analysis = self._momentum_analysis(symbol)
            
            # Analise de Volatilidade
            volatility_analysis = self._volatility_analysis(symbol)
            
            # Consolidar resultados
            final_signal = self._consolidate_results(
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
                'analyses': {
                    'multi_timeframe': scanner_results,
                    'momentum': momentum_analysis,
                    'volatility': volatility_analysis
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no scanner {symbol}: {e}")
            return {'error': str(e)}
    
    def _multi_timeframe_analysis(self, symbol: str) -> Dict:
        """Analise multi-timeframe conservadora"""
        try:
            timeframes = [
                (mt5.TIMEFRAME_M5, 'M5', 20),
                (mt5.TIMEFRAME_M15, 'M15', 30),
                (mt5.TIMEFRAME_H1, 'H1', 24)
            ]
            
            timeframe_signals = {}
            bullish_votes = 0
            bearish_votes = 0
            
            for tf, tf_name, periods in timeframes:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, periods)
                if rates is None or len(rates) < 10:
                    timeframe_signals[tf_name] = 'neutral'
                    continue
                
                df = pd.DataFrame(rates)
                current_price = df['close'].iloc[-1]
                
                # Medias moveis rapidas
                ema_fast = df['close'].tail(5).ewm(span=5).mean().iloc[-1]
                ema_slow = df['close'].tail(10).ewm(span=10).mean().iloc[-1]
                sma_20 = df['close'].tail(20).mean()
                
                if current_price > ema_fast > ema_slow > sma_20:
                    signal = 'bullish'
                    bullish_votes += 1
                elif current_price < ema_fast < ema_slow < sma_20:
                    signal = 'bearish'
                    bearish_votes += 1
                else:
                    signal = 'neutral'
                
                timeframe_signals[tf_name] = signal
            
            # Decisao conservadora
            total_votes = bullish_votes + bearish_votes
            if total_votes >= 2:
                if bullish_votes > bearish_votes:
                    overall_signal = 'bullish'
                    confidence = 0.6 + (bullish_votes / 3) * 0.2
                else:
                    overall_signal = 'bearish'
                    confidence = 0.6 + (bearish_votes / 3) * 0.2
            else:
                overall_signal = 'neutral'
                confidence = 0.5
            
            return {
                'individual_timeframes': timeframe_signals,
                'overall_signal': overall_signal,
                'confidence': confidence,
                'bullish_votes': bullish_votes,
                'bearish_votes': bearish_votes
            }
            
        except Exception as e:
            logger.error(f"Erro analise multi-timeframe: {e}")
            return {'overall_signal': 'neutral', 'confidence': 0.5, 'error': str(e)}
    
    def _momentum_analysis(self, symbol: str) -> Dict:
        """Analise de momento com filtros conservadores"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 30)
            if rates is None or len(rates) < 20:
                return {'signal': 'neutral', 'confidence': 0.5}
            
            df = pd.DataFrame(rates)
            
            # RSI conservador (30-70)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-12)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Analise de volume
            avg_volume = df['tick_volume'].tail(20).mean()
            current_volume = df['tick_volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Sinal de momento
            if 35 <= current_rsi <= 65:  # Zona neutra conservadora
                if volume_ratio > 1.3:  # Volume confirmando
                    signal = 'bullish' if current_rsi < 50 else 'bearish'
                    confidence = 0.6 + min(0.2, volume_ratio / 5)
                else:
                    signal = 'neutral'
                    confidence = 0.5
            else:
                signal = 'neutral'
                confidence = 0.4
            
            return {
                'signal': signal,
                'confidence': confidence,
                'rsi': current_rsi,
                'volume_ratio': volume_ratio
            }
            
        except Exception as e:
            logger.error(f"Erro analise momento: {e}")
            return {'signal': 'neutral', 'confidence': 0.5, 'error': str(e)}
    
    def _volatility_analysis(self, symbol: str) -> Dict:
        """Analise de volatilidade para timing"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 50)
            if rates is None or len(rates) < 20:
                return {'signal': 'neutral', 'confidence': 0.5}
            
            df = pd.DataFrame(rates)
            
            # ATR calculado
            high_low = df['high'] - df['low']
            close_prev = df['close'].shift(1)
            high_close = abs(df['high'] - close_prev)
            low_close = abs(df['low'] - close_prev)
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            volatility_pct = (atr / current_price) * 100
            
            # Volatilidade ideal para trading (0.05% a 0.5%)
            if 0.05 <= volatility_pct <= 0.5:
                signal = 'favorable'
                confidence = 0.7
            elif volatility_pct < 0.05:  # Muito baixa
                signal = 'low_volatility'
                confidence = 0.3
            else:  # Muito alta
                signal = 'high_volatility'
                confidence = 0.2
            
            return {
                'signal': signal,
                'confidence': confidence,
                'atr': atr,
                'volatility_pct': volatility_pct
            }
            
        except Exception as e:
            logger.error(f"Erro analise volatilidade: {e}")
            return {'signal': 'neutral', 'confidence': 0.5, 'error': str(e)}
    
    def _consolidate_results(self, multi_tf: Dict, momentum: Dict, volatility: Dict) -> Dict:
        """Consolida analises com pesos conservadores"""
        try:
            signals = []
            confidences = []
            reasons = []
            
            # Multi-timeframe (peso 40%)
            if multi_tf.get('overall_signal') in ['bullish', 'bearish']:
                signals.append(multi_tf['overall_signal'])
                confidences.append(multi_tf['confidence'] * 0.4)
                reasons.append(f"Multi-TF: {multi_tf['confidence']:.0%}")
            
            # Momentum (peso 35%)
            if momentum.get('signal') in ['bullish', 'bearish']:
                signals.append(momentum['signal'])
                confidences.append(momentum['confidence'] * 0.35)
                reasons.append(f"RSI: {momentum.get('rsi', 0):.1f}")
            
            # Volatilidade (peso 25%)
            if volatility.get('signal') == 'favorable':
                confidences.append(volatility['confidence'] * 0.25)
                reasons.append(f"Vol: {volatility.get('volatility_pct', 0):.3f}%")
            
            # Decisao final
            if signals and confidences:
                buy_signals = signals.count('bullish')
                sell_signals = signals.count('bearish')
                avg_confidence = sum(confidences) / len(confidences)
                
                # Critério conservador: confiança >= 55%
                if avg_confidence >= self.min_confidence:
                    if buy_signals > sell_signals:
                        final_signal = 'BUY'
                    elif sell_signals > buy_signals:
                        final_signal = 'SELL'
                    else:
                        final_signal = 'HOLD'
                else:
                    final_signal = 'HOLD'
                    avg_confidence = 0.5
            else:
                final_signal = 'HOLD'
                avg_confidence = 0.5
            
            return {
                'signal': final_signal,
                'confidence': avg_confidence,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Erro consolidacao: {e}")
            return {'signal': 'HOLD', 'confidence': 0.5, 'reasons': ['Erro']}
    
    def execute_live_trade(self, analysis: Dict) -> bool:
        """Executa trade com parametros conservadores"""
        try:
            symbol = analysis['symbol']
            signal = analysis['signal']
            confidence = analysis['confidence']
            current_price = analysis['current_price']
            
            if signal not in ['BUY', 'SELL']:
                logger.info(f"{symbol}: Sinal HOLD (conf: {confidence:.1%})")
                return False
            
            logger.info(f"EXECUTANDO {signal} - {symbol} (Conf: {confidence:.1%})")
            
            # Calcular SL/TP dinamico
            sl, tp = self.calculate_conservative_sl_tp(symbol, current_price, signal)
            
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
                "deviation": 20,
                "magic": 234002,
                "comment": f"IA_GAIN_{signal}_AUTO",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"SUCESSO! Ordem {signal} executada - Ticket: {result.order}")
                self._register_trade(symbol, signal, price, sl, tp, confidence)
                self.session_stats['trades_executed'] += 1
                return True
            else:
                logger.error(f"FALHA na ordem: {result.comment} (Cod: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao executar trade: {e}")
            return False
    
    def calculate_conservative_sl_tp(self, symbol: str, entry_price: float, signal: str) -> Tuple[float, float]:
        """Calcula SL/TP conservadores baseado em ATR"""
        try:
            # Obter ATR recente (M15)
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 20)
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                high_low = df['high'] - df['low']
                atr = high_low.tail(14).mean()
            else:
                atr = entry_price * 0.0008  # ATR padrao conservador
            
            # Multiplicadores conservadores (1:2 ratio)
            sl_multiplier = 1.5  # Stop mais largo
            tp_multiplier = 3.0  # TP 2x o stop
            
            if signal == 'BUY':
                stop_loss = entry_price - (atr * sl_multiplier)
                take_profit = entry_price + (atr * tp_multiplier)
            else:  # SELL
                stop_loss = entry_price + (atr * sl_multiplier)
                take_profit = entry_price - (atr * tp_multiplier)
            
            return round(stop_loss, 5), round(take_profit, 5)
            
        except Exception as e:
            logger.error(f"Erro calculo SL/TP: {e}")
            # Valores de seguranca conservadores
            if signal == 'BUY':
                return entry_price * 0.995, entry_price * 1.010
            else:
                return entry_price * 1.005, entry_price * 0.990
    
    def _register_trade(self, symbol: str, signal: str, price: float, sl: float, tp: float, confidence: float):
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
            'status': 'OPEN',
            'risk_reward': self.risk_reward_ratio
        }
        
        self.operation_history.append(trade_record)
        logger.info(f"Trade registrado: {symbol} {signal} @ {price:.5f} (SL: {sl:.5f}, TP: {tp:.5f})")
    
    def scan_and_trade_auto(self) -> int:
        """Escaneia e executa trades automaticos"""
        try:
            logger.info("Iniciando scan automatico...")
            trades_executed = 0
            
            # Analisar cada simbolo
            for symbol in self.trading_symbols:
                logger.info(f"Analisando {symbol}...")
                
                analysis = self.advanced_market_scanner(symbol)
                
                if 'error' in analysis:
                    logger.warning(f"{symbol}: {analysis['error']}")
                    continue
                
                signal = analysis['signal']
                confidence = analysis['confidence']
                
                logger.info(f"Sinal: {signal} (Confianca: {confidence:.1%})")
                
                # Executar se atender aos criterios conservadores
                if signal in ['BUY', 'SELL'] and confidence >= self.min_confidence:
                    if self.execute_live_trade(analysis):
                        trades_executed += 1
                        logger.info(f"Trade executado com sucesso: {symbol}")
                        
                        # Pausa entre trades
                        time.sleep(3)
                
                # Pausa entre analises
                time.sleep(1)
            
            logger.info(f"Scan automatico concluido - {trades_executed} trades executados")
            return trades_executed
            
        except Exception as e:
            logger.error(f"Erro no scan automatico: {e}")
            return 0
    
    def monitor_performance(self):
        """Monitora performance da sessao"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return
            
            current_pnl = sum(pos.profit for pos in positions)
            self.session_stats['total_pnl'] = current_pnl
            
            # Calcular drawdown maximo (9% max)
            if current_pnl < self.session_stats['max_drawdown']:
                self.session_stats['max_drawdown'] = current_pnl
            
            # Contar trades
            for pos in positions:
                if pos.profit > 0:
                    self.session_stats['trades_won'] += 1
                elif pos.profit < 0:
                    self.session_stats['trades_lost'] += 1
            
            logger.info(f"Performance Atual:")
            logger.info(f"  PnL: ${current_pnl:.2f}")
            logger.info(f"  Posicoes: {len(positions)}")
            logger.info(f"  Drawdown Max: ${self.session_stats['max_drawdown']:.2f}")
            
        except Exception as e:
            logger.error(f"Erro ao monitorar: {e}")
    
    def run_auto_trading_session(self, cycles: int = 5, cycle_interval: int = 300):
        """Executa sessao de trading automatica conservadora"""
        try:
            logger.info("INICIANDO SESSAO DE TRADING AUTOMATICA CONSERVADORA")
            logger.info("="*60)
            logger.info(f"Ciclos: {cycles}")
            logger.info(f"Intervalo: {cycle_interval}s")
            logger.info(f"Saldo inicial: ${self.account_info.balance:.2f}")
            logger.info("="*60)
            
            total_trades = 0
            
            for cycle in range(1, cycles + 1):
                logger.info(f"\nCICLO {cycle}/{cycles} - {datetime.now().strftime('%H:%M:%S')}")
                logger.info("-"*40)
                
                # Verificar condicoes
                if not self.check_trading_conditions():
                    logger.warning("Condicoes nao atendidas, aguardando proximo ciclo")
                    if cycle < cycles:
                        time.sleep(cycle_interval)
                    continue
                
                # Monitorar performance
                self.monitor_performance()
                
                # Executar scan e trades
                trades_in_cycle = self.scan_and_trade_auto()
                total_trades += trades_in_cycle
                
                logger.info(f"Ciclo {cycle} concluido - {trades_in_cycle} trades")
                
                # Aguardar proximo ciclo
                if cycle < cycles:
                    logger.info(f"Aguardando proximo ciclo...")
                    time.sleep(cycle_interval)
            
            # Resumo final
            self._display_final_summary(total_trades)
            
        except KeyboardInterrupt:
            logger.info("\nSessao interrompida")
        except Exception as e:
            logger.error(f"Erro durante sessao: {e}")
    
    def _display_final_summary(self, total_trades: int):
        """Exibe resumo final"""
        logger.info("\n" + "="*60)
        logger.info("RESUMO FINAL - SESSAO CONSERVADORA")
        logger.info("="*60)
        
        final_balance = mt5.account_info().balance
        session_pnl = final_balance - self.session_stats['start_balance']
        pnl_percentage = (session_pnl / self.session_stats['start_balance']) * 100
        
        logger.info(f"Saldo final: ${final_balance:.2f}")
        logger.info(f"PnL da sessao: ${session_pnl:.2f} ({pnl_percentage:+.2f}%)")
        logger.info(f"Total de trades: {total_trades}")
        logger.info(f"Drawdown maximo: ${self.session_stats['max_drawdown']:.2f}")
        
        if total_trades > 0:
            logger.info(f"Trades vencedores: {self.session_stats['trades_won']}")
            logger.info(f"Trades perdedores: {self.session_stats['trades_lost']}")
        
        # Salvar relatorio
        self._save_session_report(session_pnl, total_trades)
        
        logger.info("\nSessao de trading automatica concluida!")
    
    def _save_session_report(self, pnl: float, total_trades: int):
        """Salva relatorio detalhado"""
        try:
            report = {
                'session_type': 'auto_conservative_trading',
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
                    'max_risk_per_trade': self.max_risk_per_trade,
                    'min_confidence': self.min_confidence,
                    'risk_reward_ratio': self.risk_reward_ratio,
                    'max_positions': self.max_positions,
                    'volume_base': self.volume_base
                },
                'operation_history': self.operation_history
            }
            
            filename = f"auto_conservative_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatorio salvo: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatorio: {e}")

def main():
    """Funcao principal automatica"""
    print("IA GAIN + MetaTrader 5 - TRADING AUTOMATICO CONSERVADOR")
    print("="*60)
    print("PARAMETROS CONSERVADORES ATIVOS:")
    print(f"   • Risco por trade: 1%")
    print(f"   • Risco diario max: 4.5%") 
    print(f"   • Drawdown max: 9%")
    print(f"   • Confiança minima: 55%")
    print(f"   • Max posicoes: 5")
    print(f"   • Ratio R/R: 1:2")
    print("="*60)
    
    # Iniciar automaticamente
    print("\nIniciando sessao automatica em 5 segundos...")
    print("Pressione Ctrl+C para cancelar")
    
    try:
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nOperacao cancelada")
        return
    
    # Criar trader
    trader = IA_GAIN_LiveTradingAuto()
    
    # Conectar
    if not trader.connect_to_mt5():
        print("Falha ao conectar ao MT5")
        return
    
    try:
        # Executar sessao automatica
        trader.run_auto_trading_session(cycles=5, cycle_interval=300)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        if trader.connected:
            mt5.shutdown()
            print("Desconectado do MT5")

if __name__ == "__main__":
    main()