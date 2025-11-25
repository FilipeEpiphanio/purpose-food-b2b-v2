#!/usr/bin/env python3
"""
Integração IA GAIN + MetaTrader 5 com Análise Avançada
Este script utiliza múltiplos filtros e estratégias avançadas do sistema IA GAIN
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.error("MetaTrader5 não instalado. Execute: pip install MetaTrader5")

# Importar análises avançadas do IA GAIN
try:
    from src.analysis.technical_analysis import TechnicalAnalysis
    from src.strategies.ml_based import MLBased
    from src.strategies.breakout import Breakout
    from src.strategies.mean_reversion import MeanReversion
    from src.strategies.momentum import Momentum
    from src.analysis.momentum_analysis import MomentumAnalyzer
    IA_ANALYSIS_AVAILABLE = True
    logger.info("✅ Módulos avançados de análise IA GAIN disponíveis")
except ImportError as e:
    logger.warning(f"Módulos avançados não disponíveis: {e}")
    IA_ANALYSIS_AVAILABLE = False

# Importar sistema IA GAIN básico
try:
    from ia_gain.core.ia_gain_system import IA_GAIN_System
    from ia_gain.core.base import MarketData, Signal
    IA_GAIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Sistema IA GAIN básico não disponível: {e}")
    IA_GAIN_AVAILABLE = False

class IA_GAIN_MT5_Advanced:
    """Integração avançada IA GAIN + MetaTrader 5 com múltiplos filtros"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.mt5_config = config.get('mt5', {})
        self.connected = False
        self.trading_enabled = self.mt5_config.get('trading', {}).get('enabled', False)
        
        # Inicializar analisadores
        self.analyzers = {}
        if IA_ANALYSIS_AVAILABLE:
            self._initialize_analyzers()
        
    def _initialize_analyzers(self):
        """Inicializa todos os analisadores disponíveis"""
        try:
            # Análise Técnica Clássica
            self.analyzers['technical'] = TechnicalAnalysis({
                'ema_fast': 21,
                'ema_slow': 50,
                'rsi_period': 14,
                'buy_rsi': 55.0,
                'sell_rsi': 45.0
            })
            
            # Machine Learning
            self.analyzers['ml'] = MLBased(
                score_col=None,
                buy_thresh=0.65,
                sell_thresh=0.35
            )
            
            # Breakout
            self.analyzers['breakout'] = Breakout(window=20)
            
            # Mean Reversion
            self.analyzers['mean_reversion'] = MeanReversion(
                rsi_period=14,
                low_thresh=30,
                high_thresh=70
            )
            
            # Momentum
            self.analyzers['momentum'] = Momentum(
                roc_period=10,
                sma_period=20
            )
            
            logger.info("✅ Analisadores avançados inicializados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar analisadores: {e}")
    
    async def connect_mt5(self) -> bool:
        """Conecta ao MetaTrader 5"""
        try:
            if not MT5_AVAILABLE:
                logger.error("MetaTrader5 não disponível")
                return False
                
            # Inicializar MT5
            if not mt5.initialize():
                logger.error(f"Falha ao inicializar MT5: {mt5.last_error()}")
                return False
            
            # Obter informações da conta
            account_info = mt5.account_info()
            if account_info:
                logger.info(f"📊 Conta MT5: {account_info.login} | Saldo: ${account_info.balance:.2f}")
                self.connected = True
                return True
            else:
                logger.error("Não foi possível obter informações da conta")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao conectar MT5: {e}")
            return False
    
    def get_market_data(self, symbol: str, timeframe: str = 'H1', count: int = 100) -> Optional[pd.DataFrame]:
        """Obtém dados de mercado do MT5"""
        try:
            if not self.connected or not MT5_AVAILABLE:
                return None
            
            # Mapear timeframe string para MT5 constant
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            # Selecionar símbolo
            if not mt5.symbol_select(symbol, True):
                logger.warning(f"Não foi possível selecionar símbolo: {symbol}")
                return None
            
            # Obter dados históricos
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            if rates is None or len(rates) == 0:
                logger.warning(f"Dados não disponíveis para: {symbol}")
                return None
            
            # Converter para DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {e}")
            return None
    
    def advanced_market_analysis(self, symbol: str, timeframe: str = 'H1') -> Dict:
        """Análise de mercado com múltiplos filtros e estratégias"""
        try:
            # Obter dados de mercado
            market_data = self.get_market_data(symbol, timeframe)
            if market_data is None or len(market_data) < 50:
                return {'error': 'Dados insuficientes para análise'}
            
            # Obter preço atual
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'error': 'Informações do símbolo não disponíveis'}
            
            current_price = (symbol_info.ask + symbol_info.bid) / 2
            
            analysis_results = {}
            signals = []
            confidences = []
            
            # 1. Análise Técnica Clássica (EMA + RSI)
            if 'technical' in self.analyzers:
                try:
                    tech_result = self.analyzers['technical'].analyze(market_data)
                    analysis_results['technical'] = tech_result
                    signals.append(tech_result['signal'])
                    confidences.append(tech_result['confidence'])
                    logger.debug(f"Técnica: {tech_result['signal']} (conf: {tech_result['confidence']:.2f})")
                except Exception as e:
                    logger.error(f"Erro análise técnica: {e}")
            
            # 2. Machine Learning
            if 'ml' in self.analyzers:
                try:
                    ml_signals = self.analyzers['ml'].generate_signals(market_data)
                    if ml_signals:
                        last_signal = ml_signals[-1]
                        ml_signal = last_signal.action.upper()
                        ml_confidence = getattr(last_signal, 'confidence', 0.6)
                        analysis_results['ml'] = {'signal': ml_signal, 'confidence': ml_confidence}
                        signals.append(ml_signal)
                        confidences.append(ml_confidence)
                        logger.debug(f"ML: {ml_signal} (conf: {ml_confidence:.2f})")
                except Exception as e:
                    logger.error(f"Erro análise ML: {e}")
            
            # 3. Breakout
            if 'breakout' in self.analyzers:
                try:
                    breakout_signals = self.analyzers['breakout'].generate_signals(market_data)
                    if breakout_signals:
                        last_signal = breakout_signals[-1]
                        breakout_signal = last_signal.action.upper()
                        analysis_results['breakout'] = {'signal': breakout_signal, 'confidence': 0.7}
                        signals.append(breakout_signal)
                        confidences.append(0.7)
                        logger.debug(f"Breakout: {breakout_signal}")
                except Exception as e:
                    logger.error(f"Erro análise breakout: {e}")
            
            # 4. Mean Reversion
            if 'mean_reversion' in self.analyzers:
                try:
                    mean_rev_signals = self.analyzers['mean_reversion'].generate_signals(market_data)
                    if mean_rev_signals:
                        last_signal = mean_rev_signals[-1]
                        mean_rev_signal = last_signal.action.upper()
                        analysis_results['mean_reversion'] = {'signal': mean_rev_signal, 'confidence': 0.65}
                        signals.append(mean_rev_signal)
                        confidences.append(0.65)
                        logger.debug(f"Mean Reversion: {mean_rev_signal}")
                except Exception as e:
                    logger.error(f"Erro análise mean reversion: {e}")
            
            # 5. Análise de Volume e Volatilidade
            volume_analysis = self._analyze_volume_volatility(market_data)
            analysis_results['volume'] = volume_analysis
            
            # 6. Análise de Suporte/Resistência
            support_resistance = self._analyze_support_resistance(market_data)
            analysis_results['support_resistance'] = support_resistance
            
            # Consolidar sinais
            final_signal = self._consolidate_signals(signals, confidences)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'timeframe': timeframe,
                'timestamp': datetime.now(),
                'final_signal': final_signal['signal'],
                'final_confidence': final_signal['confidence'],
                'individual_analyses': analysis_results,
                'volume_analysis': volume_analysis,
                'support_resistance': support_resistance,
                'risk_level': self._assess_risk_level(market_data),
                'market_condition': self._determine_market_condition(market_data)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise avançada: {e}")
            return {'error': str(e)}
    
    def _analyze_volume_volatility(self, market_data: pd.DataFrame) -> Dict:
        """Análise de volume e volatilidade"""
        try:
            # Volume médio
            avg_volume = market_data['tick_volume'].tail(20).mean()
            current_volume = market_data['tick_volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Volatilidade (ATR)
            high_low = market_data['high'] - market_data['low']
            close_prev = market_data['close'].shift(1)
            high_close = abs(market_data['high'] - close_prev)
            low_close = abs(market_data['low'] - close_prev)
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.tail(14).mean()
            
            # Análise de volume anormal
            volume_spike = volume_ratio > 2.0
            
            return {
                'avg_volume': avg_volume,
                'current_volume': current_volume,
                'volume_ratio': volume_ratio,
                'volume_spike': volume_spike,
                'atr': atr,
                'volatility_level': 'high' if atr > market_data['close'].iloc[-1] * 0.01 else 'normal'
            }
            
        except Exception as e:
            logger.error(f"Erro análise volume/volatilidade: {e}")
            return {'error': str(e)}
    
    def _analyze_support_resistance(self, market_data: pd.DataFrame) -> Dict:
        """Análise básica de suporte e resistência"""
        try:
            close_prices = market_data['close'].tail(50)
            current_price = close_prices.iloc[-1]
            
            # Encontrar níveis de suporte/resistência simples
            max_price = close_prices.max()
            min_price = close_prices.min()
            
            # Proximidade com níveis extremos
            resistance_distance = (max_price - current_price) / current_price * 100
            support_distance = (current_price - min_price) / current_price * 100
            
            return {
                'resistance_level': max_price,
                'support_level': min_price,
                'resistance_distance_pct': resistance_distance,
                'support_distance_pct': support_distance,
                'near_resistance': resistance_distance < 1.0,
                'near_support': support_distance < 1.0
            }
            
        except Exception as e:
            logger.error(f"Erro análise suporte/resistência: {e}")
            return {'error': str(e)}
    
    def _consolidate_signals(self, signals: List[str], confidences: List[float]) -> Dict:
        """Consolida múltiplos sinais em um único sinal final"""
        if not signals:
            return {'signal': 'HOLD', 'confidence': 0.5}
        
        # Contar sinais
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        hold_count = signals.count('HOLD')
        
        # Média de confiança
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Lógica de consolidação
        if buy_count > sell_count and buy_count > hold_count:
            signal = 'BUY'
            confidence = avg_confidence * (buy_count / len(signals))
        elif sell_count > buy_count and sell_count > hold_count:
            signal = 'SELL'
            confidence = avg_confidence * (sell_count / len(signals))
        else:
            signal = 'HOLD'
            confidence = avg_confidence
        
        return {
            'signal': signal,
            'confidence': min(0.95, max(0.1, confidence)),
            'buy_votes': buy_count,
            'sell_votes': sell_count,
            'hold_votes': hold_count,
            'total_signals': len(signals)
        }
    
    def _assess_risk_level(self, market_data: pd.DataFrame) -> str:
        """Avalia nível de risco do mercado"""
        try:
            returns = market_data['close'].pct_change().tail(20)
            volatility = returns.std() * np.sqrt(252)  # Volatilidade anualizada
            
            if volatility > 0.3:
                return 'high'
            elif volatility > 0.15:
                return 'medium'
            else:
                return 'low'
                
        except Exception:
            return 'medium'
    
    def _determine_market_condition(self, market_data: pd.DataFrame) -> str:
        """Determina condição atual do mercado"""
        try:
            close_prices = market_data['close'].tail(50)
            current_price = close_prices.iloc[-1]
            sma_20 = close_prices.tail(20).mean()
            sma_50 = close_prices.mean()
            
            if current_price > sma_20 > sma_50:
                return 'trending_up'
            elif current_price < sma_20 < sma_50:
                return 'trending_down'
            else:
                return 'ranging'
                
        except Exception:
            return 'ranging'
    
    async def run_advanced_analysis(self, symbols: List[str] = None):
        """Executa análise avançada para múltiplos símbolos"""
        if not self.connected:
            logger.error("MT5 não conectado")
            return
        
        if symbols is None:
            symbols = ['EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm']
        
        logger.info(f"🚀 Iniciando análise avançada para {len(symbols)} símbolos...")
        
        results = []
        for symbol in symbols:
            logger.info(f"📊 Analisando {symbol}...")
            result = self.advanced_market_analysis(symbol)
            results.append(result)
            
            # Aguardar um pouco entre análises para não sobrecarregar
            await asyncio.sleep(0.5)
        
        # Exibir resumo
        self._display_advanced_summary(results)
        
        return results
    
    def _display_advanced_summary(self, results: List[Dict]):
        """Exibe resumo da análise avançada"""
        print("\n" + "="*80)
        print("📊 RESUMO DA ANÁLISE AVANÇADA IA GAIN + MT5")
        print("="*80)
        
        buy_signals = []
        sell_signals = []
        hold_signals = []
        
        for result in results:
            if 'error' in result:
                continue
                
            symbol = result['symbol']
            signal = result['final_signal']
            confidence = result['final_confidence']
            
            if signal == 'BUY':
                buy_signals.append((symbol, confidence))
            elif signal == 'SELL':
                sell_signals.append((symbol, confidence))
            else:
                hold_signals.append((symbol, confidence))
        
        print(f"🟢 SINAIS DE COMPRA ({len(buy_signals)}):")
        for symbol, conf in sorted(buy_signals, key=lambda x: x[1], reverse=True):
            print(f"   • {symbol:8} | Confiança: {conf:.1%}")
        
        print(f"\n🔴 SINAIS DE VENDA ({len(sell_signals)}):")
        for symbol, conf in sorted(sell_signals, key=lambda x: x[1], reverse=True):
            print(f"   • {symbol:8} | Confiança: {conf:.1%}")
        
        print(f"\n⚪ SINAIS NEUTROS ({len(hold_signals)}):")
        for symbol, conf in sorted(hold_signals, key=lambda x: x[1], reverse=True):
            print(f"   • {symbol:8} | Confiança: {conf:.1%}")
        
        print("\n" + "="*80)

async def main():
    """Função principal"""
    print("🚀 IA GAIN + MetaTrader 5 - Análise Avançada com Múltiplos Filtros")
    print("="*80)
    
    # Configuração
    config = {
        'mt5': {
            'trading': {'enabled': False}  # Desabilitar trading para teste
        }
    }
    
    # Criar integração avançada
    integration = IA_GAIN_MT5_Advanced(config)
    
    # Conectar ao MT5
    if not await integration.connect_mt5():
        print("❌ Falha ao conectar MT5")
        return
    
    # Executar análise avançada
    symbols = ['EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm', 'USDCADm', 'NZDUSDm']
    results = await integration.run_advanced_analysis(symbols)
    
    # Exemplo de análise detalhada para um símbolo
    print("\n🔍 EXEMPLO DE ANÁLISE DETALHADA:")
    if results and len(results) > 0:
        detailed_result = results[0]
        if 'error' not in detailed_result:
            print(f"Símbolo: {detailed_result['symbol']}")
            print(f"Preço Atual: {detailed_result['current_price']:.5f}")
            print(f"Sinal Final: {detailed_result['final_signal']}")
            print(f"Confiança: {detailed_result['final_confidence']:.1%}")
            print(f"Condição do Mercado: {detailed_result['market_condition']}")
            print(f"Nível de Risco: {detailed_result['risk_level']}")
            
            if 'individual_analyses' in detailed_result:
                print("\nAnálises Individuais:")
                for analysis_type, result in detailed_result['individual_analyses'].items():
                    if isinstance(result, dict) and 'signal' in result:
                        print(f"  • {analysis_type}: {result['signal']}")
    
    print("\n✅ Análise avançada concluída!")

if __name__ == "__main__":
    asyncio.run(main())