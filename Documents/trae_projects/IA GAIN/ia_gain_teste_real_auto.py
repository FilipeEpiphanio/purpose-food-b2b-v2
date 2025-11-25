#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - TESTE REAL MERCADO AUTO
Teste automatico em tempo real com execucao imediata
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
        logging.FileHandler('teste_real_auto.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IA_GAIN_TestRealAuto:
    """Teste real automatico com parametros ultra-conservadores"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        
        # PARAMETROS ULTRA-CONSERVADORES
        self.max_positions = 2  # Max 2 posicoes para teste
        self.max_risk_per_trade = 0.005  # 0.5% risco por trade
        self.min_confidence = 0.65  # 65% confianca minima (alta)
        self.risk_reward_ratio = 2.0  # 1:2 ratio
        self.volume_base = 0.01  # Volume minimo
        
        # Filtros rigorosos
        self.filters = {
            'max_spread': 25,  # Spread maximo 25 pontos
            'min_volatility': 0.0003,  # Volatilidade minima
            'max_volatility': 0.01,  # Volatilidade maxima
            'volume_threshold': 2.5,  # Volume 2.5x acima da media
            'trend_confirmation_periods': 3,  # 3 periodos confirmados
        }
        
        # Pares principais para teste
        self.trading_symbols = ['EURUSDm', 'GBPUSDm', 'USDJPYm']
        
        # Estatisticas
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
    
    def connect_to_mt5(self) -> bool:
        """Conecta ao MetaTrader 5"""
        try:
            logger.info("Conectando ao MetaTrader 5 (Teste Real Auto)...")
            
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
            logger.info(f"Servidor: {self.account_info.server}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar MT5: {e}")
            return False
    
    def validate_market_real(self, symbol: str) -> Dict:
        """Validacao rigorosa do mercado real"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'valid': False, 'error': 'Simbolo nao disponivel'}
            
            # Verificar spread
            if symbol_info.spread > self.filters['max_spread']:
                return {'valid': False, 'error': f'Spread alto: {symbol_info.spread}'}
            
            # Analise de volatilidade
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 30)
            if rates is None or len(rates) < 20:
                return {'valid': False, 'error': 'Dados insuficientes'}
            
            df = pd.DataFrame(rates)
            high_low = df['high'] - df['low']
            current_price = df['close'].iloc[-1]
            atr = high_low.tail(14).mean()
            volatility_pct = (atr / current_price) * 100
            
            if volatility_pct < self.filters['min_volatility']:
                return {'valid': False, 'error': f'Vol baixa: {volatility_pct:.4f}%'}
            elif volatility_pct > self.filters['max_volatility']:
                return {'valid': False, 'error': f'Vol alta: {volatility_pct:.4f}%'}
            
            # Analise de volume
            avg_volume = df['tick_volume'].tail(20).mean()
            current_volume = df['tick_volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            if volume_ratio < self.filters['volume_threshold']:
                return {'valid': False, 'error': f'Volume baixo: {volume_ratio:.1f}x'}
            
            return {
                'valid': True,
                'spread': symbol_info.spread,
                'volatility_pct': volatility_pct,
                'volume_ratio': volume_ratio,
                'atr': atr
            }
            
        except Exception as e:
            logger.error(f"Erro validacao mercado {symbol}: {e}")
            return {'valid': False, 'error': str(e)}
    
    def analyze_real_signal(self, symbol: str) -> Dict:
        """Analise de sinal para mercado real"""
        try:
            # Validacao inicial
            market_check = self.validate_market_real(symbol)
            if not market_check['valid']:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': market_check['error']}
            
            if not mt5.symbol_select(symbol, True):
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Simbolo nao selecionado'}
            
            symbol_info = mt5.symbol_info(symbol)
            current_price = (symbol_info.ask + symbol_info.bid) / 2
            
            # Analise Multi-Timeframe
            timeframes = [
                (mt5.TIMEFRAME_M5, 'M5', 20, 0.4),
                (mt5.TIMEFRAME_M15, 'M15', 30, 0.6)
            ]
            
            timeframe_scores = {'bullish': 0, 'bearish': 0}
            total_weight = 0
            
            for tf, tf_name, periods, weight in timeframes:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, periods)
                if rates is None or len(rates) < 10:
                    continue
                
                df = pd.DataFrame(rates)
                current_tf_price = df['close'].iloc[-1]
                
                # Medias moveis
                ema_10 = df['close'].tail(10).ewm(span=10).mean().iloc[-1]
                ema_20 = df['close'].tail(20).ewm(span=20).mean().iloc[-1]
                sma_30 = df['close'].tail(30).mean()
                
                # Sinal do timeframe
                if current_tf_price > ema_10 > ema_20 > sma_30:
                    timeframe_scores['bullish'] += weight
                elif current_tf_price < ema_10 < ema_20 < sma_30:
                    timeframe_scores['bearish'] += weight
                
                total_weight += weight
            
            # Analise de momento
            rates_m15 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 25)
            if rates_m15 is not None and len(rates_m15) >= 20:
                df_m15 = pd.DataFrame(rates_m15)
                
                # RSI
                delta = df_m15['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / (loss + 1e-12)
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                # Sinal de momento
                if 40 <= current_rsi <= 60:  # Zona neutra
                    if current_rsi < 50:
                        timeframe_scores['bullish'] += 0.5
                    else:
                        timeframe_scores['bearish'] += 0.5
                elif current_rsi < 40:
                    timeframe_scores['bullish'] += 1.0
                elif current_rsi > 60:
                    timeframe_scores['bearish'] += 1.0
            
            # Decisao final
            if total_weight > 0:
                if timeframe_scores['bullish'] > timeframe_scores['bearish'] * 1.2:
                    signal = 'BUY'
                    confidence = min(0.85, 0.6 + (timeframe_scores['bullish'] / total_weight) * 0.25)
                elif timeframe_scores['bearish'] > timeframe_scores['bullish'] * 1.2:
                    signal = 'SELL'
                    confidence = min(0.85, 0.6 + (timeframe_scores['bearish'] / total_weight) * 0.25)
                else:
                    signal = 'HOLD'
                    confidence = 0.5
            else:
                signal = 'HOLD'
                confidence = 0.5
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'signal': signal,
                'confidence': confidence,
                'market_conditions': market_check,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erro analise sinal real {symbol}: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': str(e)}
    
    def execute_trade_real(self, analysis: Dict) -> bool:
        """Executa trade real"""
        try:
            symbol = analysis['symbol']
            signal = analysis['signal']
            confidence = analysis['confidence']
            current_price = analysis['current_price']
            
            if signal not in ['BUY', 'SELL']:
                logger.info(f"{symbol}: Sinal HOLD - Nenhuma acao")
                return False
            
            if confidence < self.min_confidence:
                logger.info(f"{symbol}: Confiança {confidence:.1%} abaixo do minimo")
                return False
            
            # Verificar limite de posicoes
            positions = mt5.positions_get()
            if positions and len(positions) >= self.max_positions:
                logger.warning(f"Limite de posicoes atingido: {len(positions)}/{self.max_positions}")
                return False
            
            logger.info(f"EXECUTANDO TRADE REAL: {signal} - {symbol} (Conf: {confidence:.1%})")
            
            # Calcular SL/TP baseado em ATR
            atr = analysis['market_conditions']['atr']
            sl_distance = atr * 2.5  # Stop mais largo para teste real
            tp_distance = atr * 5.0  # TP 2x o stop (ratio 1:2)
            
            if signal == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask
                sl = price - sl_distance
                tp = price + tp_distance
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
                sl = price + sl_distance
                tp = price - tp_distance
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": self.volume_base,
                "type": order_type,
                "price": price,
                "sl": round(sl, 5),
                "tp": round(tp, 5),
                "deviation": 25,
                "magic": 234004,
                "comment": f"IA_REAL_{signal}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            logger.info(f"Enviando ordem: {symbol} {signal} @ {price:.5f}")
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"SUCESSO! Trade real executado - Ticket: {result.order}")
                self._register_trade_real(symbol, signal, price, sl, tp, confidence, analysis)
                self.session_stats['trades_executed'] += 1
                return True
            else:
                logger.error(f"FALHA na execucao: {result.comment} (Cod: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"Erro execucao trade real: {e}")
            return False
    
    def _register_trade_real(self, symbol: str, signal: str, price: float, 
                             sl: float, tp: float, confidence: float, analysis: Dict):
        """Registra trade real"""
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
            'atr_used': analysis['market_conditions'].get('atr', 0)
        }
        
        self.operation_history.append(trade_record)
        logger.info(f"Trade real registrado: {symbol} {signal} @ {price:.5f}")
        logger.info(f"Risco: {abs(price - sl):.5f} | Recompensa: {abs(tp - price):.5f}")
    
    def scan_and_trade_real_auto(self) -> int:
        """Escaneia e executa trades reais automaticamente"""
        try:
            logger.info("Iniciando scan automatico de mercado real...")
            trades_executed = 0
            
            # Verificar condicoes
            positions = mt5.positions_get()
            current_positions = len(positions) if positions else 0
            
            if current_positions >= self.max_positions:
                logger.warning(f"Max posicoes atingido: {current_positions}/{self.max_positions}")
                return 0
            
            # Analisar cada simbolo
            for symbol in self.trading_symbols:
                logger.info(f"Analisando mercado real: {symbol}")
                
                # Analise completa
                analysis = self.analyze_real_signal(symbol)
                
                if analysis['signal'] == 'HOLD':
                    logger.info(f"{symbol}: HOLD - Aguardando melhor setup")
                    continue
                
                # Executar trade real
                if self.execute_trade_real(analysis):
                    trades_executed += 1
                    logger.info(f"TRADE REAL EXECUTADO: {symbol}")
                    
                    # Pausa apos trade executado
                    time.sleep(3)
                    
                    # Verificar se atingiu limite
                    positions = mt5.positions_get()
                    if positions and len(positions) >= self.max_positions:
                        logger.info("Limite de posicoes atingido apos trade")
                        break
                
                # Pausa entre analises
                time.sleep(2)
            
            logger.info(f"Scan automatico concluido - {trades_executed} trades reais executados")
            return trades_executed
            
        except Exception as e:
            logger.error(f"Erro scan automatico real: {e}")
            return 0
    
    def monitor_performance_real(self):
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
            
            # Contar trades
            for pos in positions:
                if pos.profit > 0:
                    self.session_stats['trades_won'] += 1
                elif pos.profit < 0:
                    self.session_stats['trades_lost'] += 1
            
            # Verificar limites
            max_loss = self.session_stats['start_balance'] * 0.02  # 2% max
            if current_pnl < -max_loss:
                logger.warning(f"ALERTA: Drawdown atingiu ${current_pnl:.2f} (max: ${max_loss:.2f})")
            
            logger.info(f"Performance Real:")
            logger.info(f"  PnL Atual: ${current_pnl:.2f}")
            logger.info(f"  Posicoes Abertas: {len(positions)}")
            logger.info(f"  Drawdown Max: ${self.session_stats['max_drawdown']:.2f}")
            
        except Exception as e:
            logger.error(f"Erro monitoramento real: {e}")
    
    def run_test_real_auto(self, max_trades: int = 5):
        """Executa teste real automatico"""
        try:
            logger.info("INICIANDO TESTE REAL AUTOMATICO")
            logger.info("="*60)
            logger.info(f"Limite de trades: {max_trades}")
            logger.info(f"Saldo inicial: ${self.account_info.balance:.2f}")
            logger.info("="*60)
            logger.info("TESTE REAL COM TRADES AUTOMATICOS!")
            logger.info("="*60)
            
            trades_executed = 0
            cycles = 0
            
            while trades_executed < max_trades:
                cycles += 1
                cycle_start = datetime.now()
                
                logger.info(f"\nCICLO {cycles} - {cycle_start.strftime('%H:%M:%S')}")
                logger.info("-" * 40)
                
                # Monitorar performance
                self.monitor_performance_real()
                
                # Executar scan e trades
                new_trades = self.scan_and_trade_real_auto()
                trades_executed += new_trades
                
                logger.info(f"Ciclo {cycles}: {new_trades} trades | Total: {trades_executed}/{max_trades}")
                
                # Verificar condicoes de parada
                current_pnl = self.session_stats['total_pnl']
                max_loss_allowed = self.session_stats['start_balance'] * 0.02
                
                if current_pnl < -max_loss_allowed:
                    logger.warning(f"Limite de perda atingido: ${current_pnl:.2f}")
                    break
                
                # Pausa entre ciclos
                if trades_executed < max_trades:
                    logger.info("Aguardando proximo ciclo...")
                    time.sleep(60)  # 1 minuto entre ciclos
            
            # Resumo final
            self._display_final_summary_real(trades_executed, cycles)
            
        except Exception as e:
            logger.error(f"Erro durante teste real: {e}")
    
    def _display_final_summary_real(self, total_trades: int, cycles: int):
        """Exibe resumo final do teste real"""
        logger.info("\n" + "="*60)
        logger.info("RESUMO FINAL - TESTE REAL AUTOMATICO")
        logger.info("="*60)
        
        final_balance = mt5.account_info().balance
        session_pnl = final_balance - self.session_stats['start_balance']
        pnl_percentage = (session_pnl / self.session_stats['start_balance']) * 100
        session_duration = datetime.now() - self.session_stats['start_time']
        
        logger.info(f"Saldo final: ${final_balance:.2f}")
        logger.info(f"PnL do teste: ${session_pnl:.2f} ({pnl_percentage:+.2f}%)")
        logger.info(f"Total de trades: {total_trades}")
        logger.info(f"Ciclos executados: {cycles}")
        logger.info(f"Duracao: {session_duration.total_seconds()/60:.1f} minutos")
        logger.info(f"Drawdown maximo: ${self.session_stats['max_drawdown']:.2f}")
        
        if total_trades > 0:
            logger.info(f"Trades vencedores: {self.session_stats['trades_won']}")
            logger.info(f"Trades perdedores: {self.session_stats['trades_lost']}")
        
        # Salvar relatorio
        self._save_real_test_report(session_pnl, total_trades, cycles, session_duration)
        
        logger.info("\nTeste real automatico concluido!")
        logger.info("="*60)
    
    def _save_real_test_report(self, pnl: float, total_trades: int, cycles: int, duration: timedelta):
        """Salva relatorio detalhado do teste real"""
        try:
            report = {
                'test_type': 'real_market_auto_test',
                'start_time': self.session_stats['start_time'].isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': duration.total_seconds() / 60,
                'initial_balance': self.session_stats['start_balance'],
                'final_balance': mt5.account_info().balance,
                'pnl': pnl,
                'pnl_percentage': (pnl / self.session_stats['start_balance']) * 100,
                'total_trades': total_trades,
                'cycles_executed': cycles,
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
                'operation_history': self.operation_history
            }
            
            filename = f"teste_real_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatorio detalhado salvo: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatorio: {e}")

def main():
    """Funcao principal automatica"""
    print("IA GAIN + MetaTrader 5 - TESTE REAL AUTOMATICO")
    print("="*60)
    print("INICIANDO TESTE REAL IMEDIATAMENTE!")
    print("Parametros ultra-conservadores:")
    print(f"   • Risco por trade: 0.5% (ultra conservador)")
    print(f"   • Confiança minima: 65% (muito alta)")
    print(f"   • Volume: 0.01 lotes")
    print(f"   • Max posicoes: 2")
    print(f"   • Limite perda: 2%")
    print("="*60)
    print("Iniciando em 3 segundos...")
    
    time.sleep(3)
    
    # Criar tester
    tester = IA_GAIN_TestRealAuto()
    
    # Conectar
    if not tester.connect_to_mt5():
        print("Falha ao conectar ao MT5")
        return
    
    try:
        # Executar teste automatico
        tester.run_test_real_auto(max_trades=3)  # Limite conservador
    except Exception as e:
        logger.error(f"Erro fatal no teste: {e}")
    finally:
        if tester.connected:
            mt5.shutdown()
            print("Desconectado do MT5")

if __name__ == "__main__":
    main()