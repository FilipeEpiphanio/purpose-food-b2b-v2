#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - VERSÃO AGRESSIVA
Versão com timeframes menores e filtros mais flexíveis para mais trades
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
        logging.FileHandler('ia_gain_agressivo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IA_GAIN_Agressivo:
    """Versão agressiva com timeframes menores e filtros flexíveis"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        
        # PARAMETROS MAIS AGRESSIVOS
        self.max_positions = 5  # Aumentado para mais oportunidades
        self.max_risk_per_trade = 0.01  # 1% risco por trade (dobro do ultra-conservador)
        self.min_confidence = 0.55  # 55% confiança minima (reduzida)
        self.risk_reward_ratio = 1.5  # 1:1.5 ratio (mais realista)
        self.volume_base = 0.01  # Volume base
        
        # FILTROS MAIS FLEXÍVEIS
        self.filters = {
            'max_spread': 35,  # Spread aumentado para 35 pontos
            'min_volatility': 0.0002,  # Volatilidade minima reduzida
            'max_volatility': 0.015,  # Volatilidade maxima aumentada
            'volume_threshold': 1.5,  # Volume 1.5x acima da media (reduzido)
            'trend_confirmation_periods': 2,  # Apenas 2 periodos confirmados
        }
        
        # TIME FRAMES MENORES - FOCO EM SCALPING
        self.timeframes = [
            (mt5.TIMEFRAME_M1, 'M1', 15, 0.3),   # 1 minuto - peso 0.3
            (mt5.TIMEFRAME_M5, 'M5', 20, 0.5),   # 5 minutos - peso 0.5
            (mt5.TIMEFRAME_M15, 'M15', 30, 0.8),  # 15 minutos - peso 0.8
        ]
        
        # MAIS PARES PARA MAIS OPORTUNIDADES
        self.trading_symbols = [
            'EURUSDm', 'GBPUSDm', 'USDJPYm', 'USDCHFm', 'AUDUSDm', 'USDCADm'
        ]
        
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
            logger.info("Conectando ao MetaTrader 5 (Versao Agressiva)...")
            
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
            logger.info("MODO AGRESSIVO ATIVADO!")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar MT5: {e}")
            return False
    
    def validate_market_agressive(self, symbol: str) -> Dict:
        """Validacao flexivel do mercado para mais trades"""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'valid': False, 'error': 'Simbolo nao disponivel'}
            
            # Verificar spread (mais flexível)
            if symbol_info.spread > self.filters['max_spread']:
                return {'valid': False, 'error': f'Spread alto: {symbol_info.spread}'}
            
            # Analise de volatilidade (menos rigorosa)
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
            if rates is None or len(rates) < 15:
                return {'valid': False, 'error': 'Dados insuficientes'}
            
            df = pd.DataFrame(rates)
            high_low = df['high'] - df['low']
            current_price = df['close'].iloc[-1]
            atr = high_low.tail(10).mean()
            volatility_pct = (atr / current_price) * 100
            
            # Faixa de volatilidade mais ampla
            if volatility_pct < self.filters['min_volatility']:
                return {'valid': False, 'error': f'Vol baixa: {volatility_pct:.4f}%'}
            elif volatility_pct > self.filters['max_volatility']:
                return {'valid': False, 'error': f'Vol alta: {volatility_pct:.4f}%'}
            
            # Analise de volume (menos exigente)
            avg_volume = df['tick_volume'].tail(10).mean()
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
            logger.error(f"Erro validacao agressiva {symbol}: {e}")
            return {'valid': False, 'error': str(e)}
    
    def analyze_agressive_signal(self, symbol: str) -> Dict:
        """Analise agressiva com timeframes menores"""
        try:
            # Validacao inicial (mais flexível)
            market_check = self.validate_market_agressive(symbol)
            if not market_check['valid']:
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': market_check['error']}
            
            if not mt5.symbol_select(symbol, True):
                return {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'Simbolo nao selecionado'}
            
            symbol_info = mt5.symbol_info(symbol)
            current_price = (symbol_info.ask + symbol_info.bid) / 2
            
            # ANALISE MULTI-TIMEFRAME AGRESSIVA
            timeframe_scores = {'bullish': 0, 'bearish': 0}
            total_weight = 0
            
            for tf, tf_name, periods, weight in self.timeframes:
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, periods)
                if rates is None or len(rates) < 10:
                    continue
                
                df = pd.DataFrame(rates)
                current_tf_price = df['close'].iloc[-1]
                
                # MEDIAS MOVEIS RAPIDAS (menos periodos)
                ema_5 = df['close'].tail(5).ewm(span=5).mean().iloc[-1]
                ema_10 = df['close'].tail(10).ewm(span=10).mean().iloc[-1]
                sma_15 = df['close'].tail(15).mean()
                
                # SINAL DO TIMEFRAME (criterios mais flexíveis)
                if current_tf_price > ema_5 > ema_10:
                    timeframe_scores['bullish'] += weight
                elif current_tf_price < ema_5 < ema_10:
                    timeframe_scores['bearish'] += weight
                
                total_weight += weight
            
            # ANALISE DE MOMENTO RAPIDA (RSI 7 periodos)
            rates_m5 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
            if rates_m5 is not None and len(rates_m5) >= 15:
                df_m5 = pd.DataFrame(rates_m5)
                
                # RSI 7 periodos (mais rapido)
                delta = df_m5['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
                rs = gain / (loss + 1e-12)
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                # Zonas mais amplas para sinais
                if 35 <= current_rsi <= 65:  # Zona neutra mais ampla
                    if current_rsi < 50:
                        timeframe_scores['bullish'] += 0.3
                    else:
                        timeframe_scores['bearish'] += 0.3
                elif current_rsi < 35:  # Sobrevenda
                    timeframe_scores['bullish'] += 0.8
                elif current_rsi > 65:  # Sobrecompra
                    timeframe_scores['bearish'] += 0.8
            
            # ANALISE DE VELAS RAPIDA
            rates_m1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10)
            if rates_m1 is not None and len(rates_m1) >= 5:
                df_m1 = pd.DataFrame(rates_m1)
                
                # Ultimas 3 velas
                last_candles = df_m1.tail(3)
                bull_candles = 0
                bear_candles = 0
                
                for _, candle in last_candles.iterrows():
                    if candle['close'] > candle['open']:  # Vela de alta
                        bull_candles += 1
                    elif candle['close'] < candle['open']:  # Vela de baixa
                        bear_candles += 1
                
                # Sinal de velas recentes
                if bull_candles > bear_candles:
                    timeframe_scores['bullish'] += 0.5
                elif bear_candles > bull_candles:
                    timeframe_scores['bearish'] += 0.5
            
            # DECISAO FINAL (criterios mais flexíveis)
            if total_weight > 0:
                bullish_ratio = timeframe_scores['bullish'] / total_weight
                bearish_ratio = timeframe_scores['bearish'] / total_weight
                
                # Limiar reduzido para 55%
                if bullish_ratio > 0.55 and timeframe_scores['bullish'] > timeframe_scores['bearish']:
                    signal = 'BUY'
                    confidence = min(0.85, 0.55 + (bullish_ratio - 0.55) * 0.6)
                elif bearish_ratio > 0.55 and timeframe_scores['bearish'] > timeframe_scores['bullish']:
                    signal = 'SELL'
                    confidence = min(0.85, 0.55 + (bearish_ratio - 0.55) * 0.6)
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
                'timeframe_analysis': timeframe_scores,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erro analise agressiva {symbol}: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0, 'reason': str(e)}
    
    def execute_trade_agressive(self, analysis: Dict) -> bool:
        """Executa trade agressivo"""
        try:
            symbol = analysis['symbol']
            signal = analysis['signal']
            confidence = analysis['confidence']
            current_price = analysis['current_price']
            
            if signal not in ['BUY', 'SELL']:
                logger.info(f"{symbol}: Sinal HOLD - Aguardando")
                return False
            
            if confidence < self.min_confidence:
                logger.info(f"{symbol}: Confiança {confidence:.1%} abaixo do minimo")
                return False
            
            # Verificar limite de posicoes
            positions = mt5.positions_get()
            if positions and len(positions) >= self.max_positions:
                logger.warning(f"Limite de posicoes atingido: {len(positions)}/{self.max_positions}")
                return False
            
            logger.info(f"EXECUTANDO TRADE AGRESSIVO: {signal} - {symbol} (Conf: {confidence:.1%})")
            
            # Calcular SL/TP baseado em ATR (mais apertado para scalping)
            atr = analysis['market_conditions']['atr']
            sl_distance = atr * 1.5  # Stop mais apertado
            tp_distance = atr * 2.25  # TP 1.5x o stop (ratio 1:1.5)
            
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
                "deviation": 35,  # Maior tolerancia
                "magic": 234005,  # Magic diferente para agressivo
                "comment": f"IA_AGR_{signal}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            logger.info(f"Enviando ordem: {symbol} {signal} @ {price:.5f}")
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"SUCESSO! Trade agressivo executado - Ticket: {result.order}")
                self._register_trade_agressive(symbol, signal, price, sl, tp, confidence, analysis)
                self.session_stats['trades_executed'] += 1
                return True
            else:
                logger.error(f"FALHA na execucao: {result.comment} (Cod: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"Erro execucao trade agressivo: {e}")
            return False
    
    def _register_trade_agressive(self, symbol: str, signal: str, price: float, 
                                sl: float, tp: float, confidence: float, analysis: Dict):
        """Registra trade agressivo"""
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
            'atr_used': analysis['market_conditions'].get('atr', 0),
            'strategy_type': 'AGRESSIVO'
        }
        
        self.operation_history.append(trade_record)
        logger.info(f"Trade agressivo registrado: {symbol} {signal} @ {price:.5f}")
        logger.info(f"Risco: {abs(price - sl):.5f} | Recompensa: {abs(tp - price):.5f}")
    
    def scan_and_trade_agressive(self) -> int:
        """Escaneia e executa trades agressivos"""
        try:
            logger.info("Iniciando scan agressivo de mercado...")
            trades_executed = 0
            
            # Verificar condicoes
            positions = mt5.positions_get()
            current_positions = len(positions) if positions else 0
            
            if current_positions >= self.max_positions:
                logger.warning(f"Max posicoes atingido: {current_positions}/{self.max_positions}")
                return 0
            
            # Analisar cada simbolo rapidamente
            for symbol in self.trading_symbols:
                logger.info(f"Analise agressiva: {symbol}")
                
                # Analise rapida
                analysis = self.analyze_agressive_signal(symbol)
                
                if analysis['signal'] == 'HOLD':
                    logger.info(f"{symbol}: HOLD - Continuando")
                    continue
                
                # Executar trade agressivo
                if self.execute_trade_agressive(analysis):
                    trades_executed += 1
                    logger.info(f"TRADE AGRESSIVO EXECUTADO: {symbol}")
                    
                    # Pausa curta apos trade
                    time.sleep(2)
                    
                    # Verificar limite
                    positions = mt5.positions_get()
                    if positions and len(positions) >= self.max_positions:
                        logger.info("Limite de posicoes atingido")
                        break
                
                # Pausa curta entre simbolos
                time.sleep(1)
            
            logger.info(f"Scan agressivo concluido - {trades_executed} trades executados")
            return trades_executed
            
        except Exception as e:
            logger.error(f"Erro scan agressivo: {e}")
            return 0
    
    def monitor_performance_agressive(self):
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
            
            # Verificar limites (mais flexíveis)
            max_loss = self.session_stats['start_balance'] * 0.03  # 3% max (aumentado)
            if current_pnl < -max_loss:
                logger.warning(f"ALERTA: Drawdown ${current_pnl:.2f} (max: ${max_loss:.2f})")
            
            logger.info(f"Performance Agressiva:")
            logger.info(f"  PnL Atual: ${current_pnl:.2f}")
            logger.info(f"  Posicoes: {len(positions)}")
            logger.info(f"  Drawdown: ${self.session_stats['max_drawdown']:.2f}")
            
        except Exception as e:
            logger.error(f"Erro monitoramento agressivo: {e}")
    
    def run_agressive_session(self, max_trades: int = 10):
        """Executa sessao agressiva"""
        try:
            logger.info("INICIANDO SESSAO AGRESSIVA")
            logger.info("="*60)
            logger.info(f"Limite de trades: {max_trades}")
            logger.info(f"Saldo inicial: ${self.account_info.balance:.2f}")
            logger.info("="*60)
            logger.info("MODO AGRESSIVO - TIME FRAMES MENORES!")
            logger.info("="*60)
            logger.info("Parametros agressivos:")
            logger.info(f"   • Risco por trade: {self.max_risk_per_trade:.1%}")
            logger.info(f"   • Confiança minima: {self.min_confidence:.0%}")
            logger.info(f"   • Volume: {self.volume_base} lotes")
            logger.info(f"   • Max posicoes: {self.max_positions}")
            logger.info(f"   • Timeframes: M1, M5, M15")
            logger.info("="*60)
            
            trades_executed = 0
            cycles = 0
            
            while trades_executed < max_trades:
                cycles += 1
                cycle_start = datetime.now()
                
                logger.info(f"\nCICLO AGRESSIVO {cycles} - {cycle_start.strftime('%H:%M:%S')}")
                logger.info("-" * 40)
                
                # Monitorar performance
                self.monitor_performance_agressive()
                
                # Executar scan e trades agressivos
                new_trades = self.scan_and_trade_agressive()
                trades_executed += new_trades
                
                logger.info(f"Ciclo {cycles}: {new_trades} trades | Total: {trades_executed}/{max_trades}")
                
                # Verificar condicoes de parada
                current_pnl = self.session_stats['total_pnl']
                max_loss_allowed = self.session_stats['start_balance'] * 0.03
                
                if current_pnl < -max_loss_allowed:
                    logger.warning(f"Limite de perda atingido: ${current_pnl:.2f}")
                    break
                
                # Pausa curta entre ciclos (30 segundos para timeframes menores)
                if trades_executed < max_trades:
                    logger.info("Aguardando proximo ciclo agressivo...")
                    time.sleep(30)
            
            # Resumo final
            self._display_agressive_summary(trades_executed, cycles)
            
        except Exception as e:
            logger.error(f"Erro durante sessao agressiva: {e}")
    
    def _display_agressive_summary(self, total_trades: int, cycles: int):
        """Exibe resumo da sessao agressiva"""
        logger.info("\n" + "="*60)
        logger.info("RESUMO FINAL - SESSAO AGRESSIVA")
        logger.info("="*60)
        
        final_balance = mt5.account_info().balance
        session_pnl = final_balance - self.session_stats['start_balance']
        pnl_percentage = (session_pnl / self.session_stats['start_balance']) * 100
        session_duration = datetime.now() - self.session_stats['start_time']
        
        logger.info(f"Saldo final: ${final_balance:.2f}")
        logger.info(f"PnL da sessao: ${session_pnl:.2f} ({pnl_percentage:+.2f}%)")
        logger.info(f"Total de trades: {total_trades}")
        logger.info(f"Ciclos executados: {cycles}")
        logger.info(f"Duracao: {session_duration.total_seconds()/60:.1f} minutos")
        logger.info(f"Drawdown maximo: ${self.session_stats['max_drawdown']:.2f}")
        
        if total_trades > 0:
            logger.info(f"Trades vencedores: {self.session_stats['trades_won']}")
            logger.info(f"Trades perdedores: {self.session_stats['trades_lost']}")
        
        # Salvar relatorio
        self._save_agressive_report(session_pnl, total_trades, cycles, session_duration)
        
        logger.info("\nSessao agressiva concluida!")
        logger.info("="*60)
    
    def _save_agressive_report(self, pnl: float, total_trades: int, cycles: int, duration: timedelta):
        """Salva relatorio detalhado da sessao agressiva"""
        try:
            report = {
                'test_type': 'agressive_scalping_session',
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
                    'filters': self.filters,
                    'timeframes_used': [tf[1] for tf in self.timeframes]
                },
                'operation_history': self.operation_history
            }
            
            filename = f"agressive_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Relatorio agressivo salvo: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatorio agressivo: {e}")

def main():
    """Funcao principal agressiva"""
    print("IA GAIN + MetaTrader 5 - VERSAO AGRESSIVA")
    print("="*60)
    print("MODO SCALPING COM TIME FRAMES MENORES!")
    print("="*60)
    print("Caracteristicas agressivas:")
    print(f"   • Risco por trade: 1% (dobro do conservador)")
    print(f"   • Confiança minima: 55% (mais flexivel)")
    print(f"   • Timeframes: M1, M5, M15 (mais rapido)")
    print(f"   • Max posicoes: 5 (mais oportunidades)")
    print(f"   • Ciclos: 30 segundos (mais frequente)")
    print("="*60)
    print("Iniciando em 3 segundos...")
    
    time.sleep(3)
    
    # Criar trader agressivo
    trader = IA_GAIN_Agressivo()
    
    # Conectar
    if not trader.connect_to_mt5():
        print("Falha ao conectar ao MT5")
        return
    
    try:
        # Executar sessao agressiva
        trader.run_agressive_session(max_trades=15)  # Mais trades
    except Exception as e:
        logger.error(f"Erro fatal na sessao agressiva: {e}")
    finally:
        if trader.connected:
            mt5.shutdown()
            print("Desconectado do MT5")

if __name__ == "__main__":
    main()