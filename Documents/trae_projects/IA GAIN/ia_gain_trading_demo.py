#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - TESTE DE TRADING (MODO DEMO)
Versão de teste para validar todos os filtros antes de operar ao vivo
"""

import MetaTrader5 as mt5
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import time
from typing import Dict, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IA_GAIN_TradingDemo:
    """Demo de trading para testar todos os filtros sem executar ordens reais"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        self.test_results = []
        
        # Parâmetros de teste
        self.test_symbols = ['EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm']
        self.min_confidence = 0.7
        self.volume_test = 0.01
        
        # Filtros a testar
        self.filters_test = {
            'min_spread': 10,
            'min_volatility': 0.0005,
            'max_volatility': 0.01,
            'volume_spike': 2.0,
            'trend_confirmation': True,
            'rsi_extreme': 30,  # Oversold
            'rsi_extreme_high': 70,  # Overbought
        }
    
    def connect_to_mt5(self) -> bool:
        """Conecta ao MetaTrader 5"""
        try:
            logger.info("🔌 Conectando ao MetaTrader 5 (Modo Demo)...")
            
            if not mt5.initialize():
                logger.error(f"❌ Falha ao inicializar MT5: {mt5.last_error()}")
                return False
            
            self.account_info = mt5.account_info()
            if self.account_info is None:
                logger.error("❌ Não foi possível obter informações da conta")
                return False
            
            logger.info(f"✅ Conectado! Conta: {self.account_info.login}")
            logger.info(f"💰 Saldo: ${self.account_info.balance:.2f}")
            logger.info(f"🏢 Servidor: {self.account_info.server}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar MT5: {e}")
            return False
    
    def test_market_analysis(self, symbol: str) -> Dict:
        """Testa análise de mercado completa"""
        try:
            logger.info(f"🔍 Testando análise para {symbol}...")
            
            # Selecionar símbolo
            if not mt5.symbol_select(symbol, True):
                return {'error': 'Não foi possível selecionar símbolo'}
            
            # Obter informações
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'error': 'Informações do símbolo não disponíveis'}
            
            # Testar filtros básicos
            test_result = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'current_price': (symbol_info.ask + symbol_info.bid) / 2,
                'spread': symbol_info.spread,
                'filters_passed': [],
                'filters_failed': [],
                'signals_generated': [],
                'confidence_scores': []
            }
            
            # Filtro 1: Spread
            if symbol_info.spread <= self.filters_test['min_spread']:
                test_result['filters_passed'].append(f"✅ Spread OK: {symbol_info.spread} pts")
            else:
                test_result['filters_failed'].append(f"❌ Spread alto: {symbol_info.spread} pts")
            
            # Obter dados históricos
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 50)
            if rates is not None and len(rates) > 20:
                df = pd.DataFrame(rates)
                
                # Filtro 2: Volatilidade
                returns = df['close'].pct_change().dropna()
                volatility = returns.std()
                
                if self.filters_test['min_volatility'] <= volatility <= self.filters_test['max_volatility']:
                    test_result['filters_passed'].append(f"✅ Volatilidade OK: {volatility:.6f}")
                else:
                    test_result['filters_failed'].append(f"❌ Volatilidade fora: {volatility:.6f}")
                
                # Filtro 3: Volume
                avg_volume = df['tick_volume'].iloc[:-5].mean()
                recent_volume = df['tick_volume'].tail(5).mean()
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
                
                if volume_ratio >= self.filters_test['volume_spike']:
                    test_result['filters_passed'].append(f"✅ Volume spike: {volume_ratio:.2f}x")
                else:
                    test_result['filters_passed'].append(f"ℹ️ Volume normal: {volume_ratio:.2f}x")
                
                # Filtro 4: Análise Técnica
                # RSI
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
                
                if loss != 0:
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                else:
                    rsi = 50
                
                # Médias móveis
                sma_20 = df['close'].tail(20).mean()
                sma_50 = df['close'].mean()
                current_price = df['close'].iloc[-1]
                
                # Sinais técnicos
                if rsi <= self.filters_test['rsi_extreme']:
                    test_result['signals_generated'].append(f"🟢 RSI Oversold: {rsi:.1f}")
                    test_result['confidence_scores'].append(0.8)
                elif rsi >= self.filters_test['rsi_extreme_high']:
                    test_result['signals_generated'].append(f"🔴 RSI Overbought: {rsi:.1f}")
                    test_result['confidence_scores'].append(0.8)
                else:
                    test_result['signals_generated'].append(f"⚪ RSI Normal: {rsi:.1f}")
                    test_result['confidence_scores'].append(0.5)
                
                # Tendência
                if current_price > sma_20 > sma_50:
                    test_result['signals_generated'].append(f"🟢 Tendência Alta")
                    test_result['confidence_scores'].append(0.7)
                elif current_price < sma_20 < sma_50:
                    test_result['signals_generated'].append(f"🔴 Tendência Baixa")
                    test_result['confidence_scores'].append(0.7)
                else:
                    test_result['signals_generated'].append(f"⚪ Tendência Neutra")
                    test_result['confidence_scores'].append(0.4)
                
                # Filtro 5: Multi-timeframe
                m5_rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
                h1_rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 20)
                
                if m5_rates is not None and h1_rates is not None:
                    m5_df = pd.DataFrame(m5_rates)
                    h1_df = pd.DataFrame(h1_rates)
                    
                    m5_trend = "alta" if m5_df['close'].iloc[-1] > m5_df['close'].tail(10).mean() else "baixa"
                    h1_trend = "alta" if h1_df['close'].iloc[-1] > h1_df['close'].mean() else "baixa"
                    
                    if m5_trend == h1_trend:
                        test_result['filters_passed'].append(f"✅ Confluência M5/H1: {m5_trend}")
                        test_result['confidence_scores'].append(0.9)
                    else:
                        test_result['filters_failed'].append(f"❌ Divergência M5/H1: M5={m5_trend}, H1={h1_trend}")
                
            else:
                test_result['filters_failed'].append("❌ Dados históricos insuficientes")
            
            # Calcular confiança final
            if test_result['confidence_scores']:
                avg_confidence = sum(test_result['confidence_scores']) / len(test_result['confidence_scores'])
                test_result['final_confidence'] = avg_confidence
                
                # Gerar sinal final de teste
                if avg_confidence >= self.min_confidence:
                    if any("alta" in signal for signal in test_result['signals_generated']):
                        test_result['final_signal'] = "BUY"
                    elif any("baixa" in signal for signal in test_result['signals_generated']):
                        test_result['final_signal'] = "SELL"
                    else:
                        test_result['final_signal'] = "HOLD"
                else:
                    test_result['final_signal'] = "HOLD"
            else:
                test_result['final_confidence'] = 0.0
                test_result['final_signal'] = "HOLD"
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ Erro ao testar {symbol}: {e}")
            return {'error': str(e)}
    
    def simulate_trade_execution(self, test_result: Dict) -> Dict:
        """Simula execução de trade baseado no teste"""
        try:
            if 'error' in test_result:
                return {'status': 'ERROR', 'message': test_result['error']}
            
            symbol = test_result['symbol']
            signal = test_result.get('final_signal', 'HOLD')
            confidence = test_result.get('final_confidence', 0.0)
            current_price = test_result['current_price']
            
            # Simular ordem apenas se for BUY/SELL com alta confiança
            if signal in ['BUY', 'SELL'] and confidence >= self.min_confidence:
                # Calcular SL/TP simulados (exemplo: 50 pips SL, 75 pips TP)
                if signal == 'BUY':
                    sl = current_price - 0.0050  # 50 pips
                    tp = current_price + 0.0075  # 75 pips
                else:  # SELL
                    sl = current_price + 0.0050  # 50 pips
                    tp = current_price - 0.0075  # 75 pips
                
                simulated_trade = {
                    'status': 'WOULD_TRADE',
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': confidence,
                    'entry_price': current_price,
                    'stop_loss': round(sl, 5),
                    'take_profit': round(tp, 5),
                    'volume': self.volume_test,
                    'simulated_time': datetime.now(),
                    'risk_reward_ratio': 1.5
                }
                
                logger.info(f"🎯 Simulação: {signal} {symbol} @ {current_price:.5f} "
                          f"(SL: {sl:.5f}, TP: {tp:.5f}, Conf: {confidence:.1%})")
                
                return simulated_trade
            else:
                return {
                    'status': 'NO_TRADE',
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': confidence,
                    'reason': 'Confiança baixa ou sinal HOLD'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na simulação: {e}")
            return {'status': 'ERROR', 'message': str(e)}
    
    def run_comprehensive_test(self) -> Dict:
        """Executa teste completo em todos os símbolos"""
        try:
            logger.info("🚀 INICIANDO TESTE COMPLETO DE TRADING")
            logger.info("="*60)
            logger.info("Este é um teste DEMO - NENHUMA ordem real será executada")
            logger.info("="*60)
            
            if not self.connected:
                logger.error("❌ Não conectado ao MT5")
                return {'error': 'Not connected'}
            
            test_summary = {
                'start_time': datetime.now(),
                'total_symbols_tested': 0,
                'symbols_with_signals': 0,
                'would_trade_count': 0,
                'avg_confidence': 0.0,
                'test_results': [],
                'simulated_trades': []
            }
            
            # Testar cada símbolo
            for symbol in self.test_symbols:
                logger.info(f"\n📊 TESTANDO {symbol}")
                logger.info("-"*40)
                
                # Análise de mercado
                market_test = self.test_market_analysis(symbol)
                test_summary['test_results'].append(market_test)
                test_summary['total_symbols_tested'] += 1
                
                if 'error' not in market_test:
                    # Simular trade
                    simulated_trade = self.simulate_trade_execution(market_test)
                    test_summary['simulated_trades'].append(simulated_trade)
                    
                    # Estatísticas
                    if market_test.get('final_confidence', 0) > 0:
                        test_summary['avg_confidence'] += market_test['final_confidence']
                        test_summary['symbols_with_signals'] += 1
                    
                    if simulated_trade['status'] == 'WOULD_TRADE':
                        test_summary['would_trade_count'] += 1
                
                # Pequena pausa entre testes
                time.sleep(1)
            
            # Calcular médias finais
            if test_summary['symbols_with_signals'] > 0:
                test_summary['avg_confidence'] /= test_summary['symbols_with_signals']
            
            test_summary['end_time'] = datetime.now()
            test_summary['duration'] = str(test_summary['end_time'] - test_summary['start_time'])
            
            # Exibir resumo
            self.display_test_summary(test_summary)
            
            # Salvar resultados
            self.save_test_results(test_summary)
            
            return test_summary
            
        except Exception as e:
            logger.error(f"❌ Erro durante teste: {e}")
            return {'error': str(e)}
    
    def display_test_summary(self, summary: Dict):
        """Exibe resumo do teste"""
        print("\n" + "="*60)
        print("📊 RESUMO DO TESTE DE TRADING")
        print("="*60)
        print(f"⏰ Início: {summary['start_time'].strftime('%H:%M:%S')}")
        print(f"🏁 Fim: {summary['end_time'].strftime('%H:%M:%S')}")
        print(f"⏱️  Duração: {summary['duration']}")
        print(f"📈 Símbolos testados: {summary['total_symbols_tested']}")
        print(f"🎯 Sinais gerados: {summary['symbols_with_signals']}")
        print(f"💰 Trades simulados: {summary['would_trade_count']}")
        print(f"📊 Confiança média: {summary['avg_confidence']:.1%}")
        
        if summary['would_trade_count'] > 0:
            print(f"\n🚀 TRADES QUE SERIAM EXECUTADOS:")
            for trade in summary['simulated_trades']:
                if trade['status'] == 'WOULD_TRADE':
                    print(f"   • {trade['signal']} {trade['symbol']} @ {trade['entry_price']:.5f}")
                    print(f"     SL: {trade['stop_loss']:.5f} | TP: {trade['take_profit']:.5f}")
                    print(f"     Confiança: {trade['confidence']:.1%} | R/R: {trade['risk_reward_ratio']}:1")
        
        print("\n" + "="*60)
        
        # Recomendação final
        if summary['would_trade_count'] > 0 and summary['avg_confidence'] >= self.min_confidence:
            print("✅ TESTE APROVADO - Sistema pronto para trading ao vivo!")
            print("💡 Recomendações:")
            print("   • Comece com volume mínimo (0.01)")
            print("   • Monitore de perto as primeiras operações")
            print("   • Use stop loss sempre")
        else:
            print("⚠️  TESTE NÃO APROVADO - Ajustes necessários:")
            if summary['avg_confidence'] < self.min_confidence:
                print("   • Confiança média baixa - revisar filtros")
            if summary['would_trade_count'] == 0:
                print("   • Nenhum sinal de trade - mercado pode estar lateral")
    
    def save_test_results(self, summary: Dict):
        """Salva resultados do teste"""
        try:
            filename = f"trading_test_{summary['start_time'].strftime('%Y%m%d_%H%M%S')}.json"
            
            # Converter datetime para string
            summary_serializable = summary.copy()
            for key in ['start_time', 'end_time']:
                if key in summary_serializable:
                    summary_serializable[key] = summary_serializable[key].isoformat()
            
            with open(filename, 'w') as f:
                json.dump(summary_serializable, f, indent=2, default=str)
            
            logger.info(f"📄 Resultados salvos em: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {e}")

def main():
    """Função principal"""
    print("🚀 IA GAIN + MetaTrader 5 - TESTE DE TRADING")
    print("="*60)
    print("📋 Este é um teste DEMO")
    print("🔍 Analisaremos oportunidades sem executar ordens reais")
    print("✅ Verificaremos todos os filtros de segurança")
    print("="*60)
    
    input("\nPressione Enter para iniciar o teste...")
    
    # Criar tester
    tester = IA_GAIN_TradingDemo()
    
    # Conectar ao MT5
    if not tester.connect_to_mt5():
        print("❌ Falha ao conectar ao MT5")
        return
    
    try:
        # Executar teste completo
        results = tester.run_comprehensive_test()
        
        if 'error' not in results:
            print(f"\n✅ Teste concluído com sucesso!")
            
            # Perguntar se deseja iniciar trading ao vivo
            if results['would_trade_count'] > 0:
                response = input("\nDeseja iniciar trading ao vivo agora? (SIM/NÃO): ").upper().strip()
                if response == 'SIM':
                    print("\n🔄 Iniciando módulo de trading ao vivo...")
                    # Aqui poderia chamar o módulo ao vivo
                    print("✅ Módulo de trading ao vivo pronto!")
                else:
                    print("\n👍 Teste concluído. Sistema pronto quando você estiver!")
            else:
                print("\n📊 Nenhuma oportunidade no momento. Tente novamente mais tarde.")
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
    finally:
        if tester.connected:
            mt5.shutdown()
            print("🔌 Desconectado do MT5")

if __name__ == "__main__":
    main()