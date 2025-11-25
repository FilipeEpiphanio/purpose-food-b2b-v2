#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - TRADING AO VIVO COM FILTROS AVANÇADOS
Script para executar operações reais com todos os filtros de segurança
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
import time
import asyncio
from typing import Dict, List, Optional, Tuple
import os

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IA_GAIN_LiveTrader:
    """Trader ao vivo com IA GAIN e múltiplos filtros de segurança"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        self.max_positions = 3  # Máximo de posições simultâneas
        self.max_risk_per_trade = 0.02  # 2% risco por trade
        self.min_confidence = 0.7  # Confiança mínima 70%
        self.risk_reward_ratio = 1.5  # Risco/recompensa 1:1.5
        self.volume_base = 0.01  # Volume mínimo para teste
        self.operational_hours = (9, 17)  # Horário de operação (9h às 17h)
        
        # Parâmetros de filtro
        self.filters = {
            'min_spread': 10,  # Spread máximo em pontos
            'min_volatility': 0.0005,  # Volatilidade mínima
            'max_volatility': 0.01,  # Volatilidade máxima
            'volume_spike_threshold': 2.0,  # Spike de volume
            'trend_confirmation_periods': 3,  # Períodos para confirmação de tendência
        }
        
        # Símbolos permitidos para teste
        self.trading_symbols = [
            'EURUSDm', 'GBPUSDm', 'USDJPYm', 'AUDUSDm', 'USDCHFm',
            'USDCADm', 'NZDUSDm', 'EURJPYm', 'GBPJPYm'
        ]
        
        # Histórico de operações
        self.operation_history = []
        self.daily_trades = 0
        self.daily_pnl = 0.0
        
    def connect_to_mt5(self) -> bool:
        """Conecta ao MetaTrader 5 com verificações"""
        try:
            logger.info("🔌 Conectando ao MetaTrader 5...")
            
            if not mt5.initialize():
                logger.error(f"❌ Falha ao inicializar MT5: {mt5.last_error()}")
                return False
            
            # Obter informações da conta
            self.account_info = mt5.account_info()
            if self.account_info is None:
                logger.error("❌ Não foi possível obter informações da conta")
                return False
            
            logger.info(f"✅ Conectado! Conta: {self.account_info.login}")
            logger.info(f"💰 Saldo: ${self.account_info.balance:.2f}")
            logger.info(f"🏢 Servidor: {self.account_info.server}")
            logger.info(f"📈 Alavancagem: 1:{self.account_info.leverage}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar MT5: {e}")
            return False
    
    def check_operational_hours(self) -> bool:
        """Verifica se está dentro do horário operacional"""
        current_hour = datetime.now().hour
        start_hour, end_hour = self.operational_hours
        
        if start_hour <= current_hour < end_hour:
            return True
        else:
            logger.warning(f"🕐 Fora do horário operacional ({start_hour}h - {end_hour}h)")
            return False
    
    def check_risk_limits(self) -> bool:
        """Verifica limites de risco"""
        try:
            # Verificar número de posições abertas
            positions = mt5.positions_get()
            open_positions = len(positions) if positions else 0
            
            if open_positions >= self.max_positions:
                logger.warning(f"⚠️ Máximo de posições atingido: {open_positions}/{self.max_positions}")
                return False
            
            # Verificar drawdown diário
            daily_loss_pct = abs(self.daily_pnl) / self.account_info.balance
            if daily_loss_pct > 0.05:  # 5% max daily loss
                logger.warning(f"⚠️ Limite de perda diária atingido: {daily_loss_pct:.1%}")
                return False
            
            # Verificar número de trades diários
            if self.daily_trades >= 10:  # Máximo 10 trades por dia
                logger.warning(f"⚠️ Máximo de trades diários atingido: {self.daily_trades}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar limites de risco: {e}")
            return False
    
    def analyze_market_conditions(self, symbol: str) -> Dict:
        """Análise completa das condições de mercado"""
        try:
            # Selecionar símbolo
            if not mt5.symbol_select(symbol, True):
                return {'error': 'Não foi possível selecionar símbolo'}
            
            # Obter informações do símbolo
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return {'error': 'Informações do símbolo não disponíveis'}
            
            # Verificar spread
            if symbol_info.spread > self.filters['min_spread']:
                return {'error': f'Spread muito alto: {symbol_info.spread} pontos'}
            
            # Obter dados históricos (últimas 50 barras M15)
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 50)
            if rates is None or len(rates) < 20:
                return {'error': 'Dados históricos insuficientes'}
            
            df = pd.DataFrame(rates)
            current_price = (symbol_info.ask + symbol_info.bid) / 2
            
            # Análise de tendência com múltiplos timeframe
            trend_analysis = self._multi_timeframe_analysis(symbol)
            
            # Análise de volatilidade
            volatility = self._analyze_volatility(df)
            
            # Análise de volume
            volume_analysis = self._analyze_volume(df)
            
            # Análise técnica básica
            technical_analysis = self._technical_analysis(df, current_price)
            
            # Calcular força do sinal (0-100)
            signal_strength = self._calculate_signal_strength(
                trend_analysis, volatility, volume_analysis, technical_analysis
            )
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'spread': symbol_info.spread,
                'trend_analysis': trend_analysis,
                'volatility': volatility,
                'volume_analysis': volume_analysis,
                'technical_analysis': technical_analysis,
                'signal_strength': signal_strength,
                'signal': self._get_signal_from_strength(signal_strength),
                'confidence': signal_strength / 100,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de mercado para {symbol}: {e}")
            return {'error': str(e)}
    
    def _multi_timeframe_analysis(self, symbol: str) -> Dict:
        """Análise de tendência em múltiplos timeframes"""
        try:
            # M5, M15, H1
            timeframes = [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1]
            timeframe_names = ['M5', 'M15', 'H1']
            
            trends = {}
            
            for tf, name in zip(timeframes, timeframe_names):
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, 20)
                if rates is not None and len(rates) > 10:
                    df = pd.DataFrame(rates)
                    sma_fast = df['close'].tail(10).mean()
                    sma_slow = df['close'].mean()
                    current_price = df['close'].iloc[-1]
                    
                    if current_price > sma_fast > sma_slow:
                        trends[name] = 'bullish'
                    elif current_price < sma_fast < sma_slow:
                        trends[name] = 'bearish'
                    else:
                        trends[name] = 'neutral'
                else:
                    trends[name] = 'neutral'
            
            # Consolidação da tendência
            bullish_count = sum(1 for t in trends.values() if t == 'bullish')
            bearish_count = sum(1 for t in trends.values() if t == 'bearish')
            
            if bullish_count >= 2:
                overall_trend = 'strong_bullish'
            elif bearish_count >= 2:
                overall_trend = 'strong_bearish'
            elif bullish_count == 1:
                overall_trend = 'weak_bullish'
            elif bearish_count == 1:
                overall_trend = 'weak_bearish'
            else:
                overall_trend = 'neutral'
            
            return {
                'individual_timeframes': trends,
                'overall_trend': overall_trend,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count
            }
            
        except Exception as e:
            logger.error(f"Erro análise multi-timeframe: {e}")
            return {'overall_trend': 'neutral', 'error': str(e)}
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """Análise de volatilidade"""
        try:
            # Retornos percentuais
            returns = df['close'].pct_change().dropna()
            
            # Volatilidade atual (últimas 10 barras)
            recent_volatility = returns.tail(10).std()
            
            # Volatilidade histórica (todas as barras)
            historical_volatility = returns.std()
            
            # Ratio de volatilidade
            vol_ratio = recent_volatility / historical_volatility if historical_volatility > 0 else 1.0
            
            # Classificação
            if recent_volatility < self.filters['min_volatility']:
                vol_level = 'too_low'
            elif recent_volatility > self.filters['max_volatility']:
                vol_level = 'too_high'
            else:
                vol_level = 'normal'
            
            return {
                'recent_volatility': recent_volatility,
                'historical_volatility': historical_volatility,
                'volatility_ratio': vol_ratio,
                'volatility_level': vol_level
            }
            
        except Exception as e:
            logger.error(f"Erro análise volatilidade: {e}")
            return {'volatility_level': 'normal', 'error': str(e)}
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Análise de volume"""
        try:
            # Volume médio (excluindo as últimas 5 barras)
            avg_volume = df['tick_volume'].iloc[:-5].mean()
            
            # Volume recente (últimas 5 barras)
            recent_volume = df['tick_volume'].tail(5).mean()
            
            # Ratio de volume
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Spike de volume
            volume_spike = volume_ratio > self.filters['volume_spike_threshold']
            
            return {
                'avg_volume': avg_volume,
                'recent_volume': recent_volume,
                'volume_ratio': volume_ratio,
                'volume_spike': volume_spike
            }
            
        except Exception as e:
            logger.error(f"Erro análise volume: {e}")
            return {'volume_spike': False, 'error': str(e)}
    
    def _technical_analysis(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Análise técnica básica"""
        try:
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
            
            # Sinal de preço vs médias
            if current_price > sma_20 > sma_50:
                ma_signal = 'bullish'
            elif current_price < sma_20 < sma_50:
                ma_signal = 'bearish'
            else:
                ma_signal = 'neutral'
            
            return {
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'ma_signal': ma_signal,
                'price_vs_sma20_pct': (current_price - sma_20) / sma_20 * 100
            }
            
        except Exception as e:
            logger.error(f"Erro análise técnica: {e}")
            return {'rsi': 50, 'ma_signal': 'neutral', 'error': str(e)}
    
    def _calculate_signal_strength(self, trend: Dict, volatility: Dict, 
                                 volume: Dict, technical: Dict) -> float:
        """Calcula força do sinal (0-100)"""
        strength = 50  # Neutro inicial
        
        # Tendência (40% do peso)
        trend_strength = {
            'strong_bullish': 80,
            'weak_bullish': 65,
            'neutral': 50,
            'weak_bearish': 35,
            'strong_bearish': 20
        }
        strength += (trend_strength.get(trend['overall_trend'], 50) - 50) * 0.4
        
        # Volatilidade (20% do peso)
        if volatility['volatility_level'] == 'normal':
            strength += 10
        elif volatility['volatility_level'] == 'too_high':
            strength -= 15
        elif volatility['volatility_level'] == 'too_low':
            strength -= 10
        
        # Volume (20% do peso)
        if volume['volume_spike']:
            strength += 10
        
        # Técnico (20% do peso)
        if technical['ma_signal'] == 'bullish':
            strength += 10
        elif technical['ma_signal'] == 'bearish':
            strength -= 10
        
        # RSI ajuste fino
        rsi = technical.get('rsi', 50)
        if 30 < rsi < 70:  # Zona normal
            pass
        elif rsi <= 30:  # Oversold - bom para compra
            strength += 5
        elif rsi >= 70:  # Overbought - bom para venda
            strength -= 5
        
        return max(0, min(100, strength))  # Limitar entre 0-100
    
    def _get_signal_from_strength(self, strength: float) -> str:
        """Converte força do sinal em ação"""
        if strength >= 75:
            return 'STRONG_BUY'
        elif strength >= 65:
            return 'BUY'
        elif strength <= 25:
            return 'STRONG_SELL'
        elif strength <= 35:
            return 'SELL'
        else:
            return 'HOLD'
    
    def calculate_stop_loss_take_profit(self, symbol: str, entry_price: float, 
                                      signal: str, atr_value: float = None) -> Tuple[float, float]:
        """Calcula Stop Loss e Take Profit baseado em ATR"""
        try:
            # Obter ATR se não fornecido
            if atr_value is None:
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 20)
                if rates is not None and len(rates) > 0:
                    df = pd.DataFrame(rates)
                    high_low = df['high'] - df['low']
                    atr_value = high_low.tail(14).mean()
                else:
                    atr_value = entry_price * 0.001  # Valor padrão
            
            # Multiplicador de ATR baseado no sinal
            if 'STRONG' in signal:
                sl_multiplier = 1.5  # Stop mais largo para sinais fortes
                tp_multiplier = 2.5  # Take profit maior
            else:
                sl_multiplier = 1.0
                tp_multiplier = 1.5
            
            if signal in ['BUY', 'STRONG_BUY']:
                stop_loss = entry_price - (atr_value * sl_multiplier)
                take_profit = entry_price + (atr_value * tp_multiplier)
            else:  # SELL ou STRONG_SELL
                stop_loss = entry_price + (atr_value * sl_multiplier)
                take_profit = entry_price - (atr_value * tp_multiplier)
            
            # Arredondar para 5 casas decimais (padrão forex)
            stop_loss = round(stop_loss, 5)
            take_profit = round(take_profit, 5)
            
            logger.info(f"📊 SL/TP calculados - SL: {stop_loss:.5f}, TP: {take_profit:.5f}")
            
            return stop_loss, take_profit
            
        except Exception as e:
            logger.error(f"Erro ao calcular SL/TP: {e}")
            # Valores padrão de segurança
            if signal in ['BUY', 'STRONG_BUY']:
                return entry_price * 0.995, entry_price * 1.005
            else:
                return entry_price * 1.005, entry_price * 0.995
    
    def execute_trade(self, symbol: str, signal: str, volume: float, 
                     entry_price: float, confidence: float) -> bool:
        """Executa ordem de trade com todos os filtros"""
        try:
            logger.info(f"🚀 Preparando ordem {signal} para {symbol} - Preço: {entry_price:.5f}")
            
            # Verificar confiança mínima
            if confidence < self.min_confidence:
                logger.warning(f"⚠️ Confiança baixa demais: {confidence:.1%} < {self.min_confidence:.1%}")
                return False
            
            # Verificar sinal
            if signal not in ['BUY', 'SELL', 'STRONG_BUY', 'STRONG_SELL']:
                logger.error(f"❌ Sinal inválido: {signal}")
                return False
            
            # Calcular SL e TP
            stop_loss, take_profit = self.calculate_stop_loss_take_profit(symbol, entry_price, signal)
            
            # Preparar ordem
            if signal in ['BUY', 'STRONG_BUY']:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
            
            # Criar request da ordem
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": 10,  # Desvio máximo em pontos
                "magic": 234000,  # Número mágico para identificar nossas ordens
                "comment": f"IA_GAIN_{signal}_CONF_{int(confidence*100)}",
                "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
                "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or Cancel
            }
            
            # Enviar ordem
            logger.info(f"📤 Enviando ordem - Tipo: {signal}, Volume: {volume}, Preço: {price:.5f}")
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Ordem executada com sucesso! Ticket: {result.order}")
                
                # Registrar operação
                self._register_operation(symbol, signal, volume, price, stop_loss, take_profit, confidence)
                
                self.daily_trades += 1
                return True
            else:
                logger.error(f"❌ Falha na ordem: {result.comment} (Código: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar trade: {e}")
            return False
    
    def _register_operation(self, symbol: str, signal: str, volume: float, 
                           entry_price: float, sl: float, tp: float, confidence: float):
        """Registra operação no histórico"""
        operation = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'signal': signal,
            'volume': volume,
            'entry_price': entry_price,
            'stop_loss': sl,
            'take_profit': tp,
            'confidence': confidence,
            'status': 'OPEN',
            'ticket': None  # Será preenchido quando a posição for identificada
        }
        
        self.operation_history.append(operation)
        
        # Salvar em arquivo JSON
        try:
            with open('trading_history.json', 'w') as f:
                json.dump(self.operation_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {e}")
    
    def scan_trading_opportunities(self) -> List[Dict]:
        """Escaneia oportunidades de trading"""
        logger.info("🔍 Escaneando oportunidades de trading...")
        
        opportunities = []
        
        for symbol in self.trading_symbols:
            logger.info(f"📊 Analisando {symbol}...")
            
            # Análise completa de mercado
            market_analysis = self.analyze_market_conditions(symbol)
            
            if 'error' in market_analysis:
                logger.warning(f"⚠️ {symbol}: {market_analysis['error']}")
                continue
            
            signal = market_analysis['signal']
            confidence = market_analysis['confidence']
            
            # Filtrar apenas sinais de alta qualidade
            if signal in ['BUY', 'SELL', 'STRONG_BUY', 'STRONG_SELL'] and confidence >= self.min_confidence:
                opportunities.append(market_analysis)
                logger.info(f"🎯 Oportunidade encontrada: {symbol} - {signal} (Confiança: {confidence:.1%})")
            else:
                logger.info(f"ℹ️ {symbol}: {signal} (Confiança: {confidence:.1%}) - Não atende critérios")
            
            # Pequena pausa entre análises
            time.sleep(0.5)
        
        logger.info(f"✅ Escaneamento concluído - {len(opportunities)} oportunidades encontradas")
        return opportunities
    
    def execute_trades_from_opportunities(self, opportunities: List[Dict]) -> int:
        """Executa trades baseado nas oportunidades encontradas"""
        executed_count = 0
        
        for opp in opportunities:
            symbol = opp['symbol']
            signal = opp['signal']
            confidence = opp['confidence']
            current_price = opp['current_price']
            
            logger.info(f"🚀 Executando trade para {symbol} - {signal}")
            
            # Executar trade
            success = self.execute_trade(symbol, signal, self.volume_base, current_price, confidence)
            
            if success:
                executed_count += 1
                logger.info(f"✅ Trade executado com sucesso: {symbol}")
            else:
                logger.error(f"❌ Falha ao executar trade: {symbol}")
            
            # Pequena pausa entre trades
            time.sleep(1)
        
        return executed_count
    
    def monitor_open_positions(self):
        """Monitora posições abertas"""
        try:
            positions = mt5.positions_get()
            if positions is None or len(positions) == 0:
                logger.info("📍 Nenhuma posição aberta no momento")
                return
            
            total_profit = 0
            logger.info(f"📊 Monitorando {len(positions)} posições abertas:")
            
            for position in positions:
                profit = position.profit
                total_profit += profit
                
                profit_pct = (profit / self.account_info.balance) * 100
                profit_color = "🟢" if profit >= 0 else "🔴"
                
                logger.info(f"{profit_color} {position.symbol:8} | "
                          f"{'COMPRA' if position.type == mt5.ORDER_TYPE_BUY else 'VENDA':6} | "
                          f"Vol: {position.volume:.2f} | "
                          f"Entrada: {position.price_open:.5f} | "
                          f"Atual: {position.price_current:.5f} | "
                          f"Lucro: ${profit:.2f} ({profit_pct:.2f}%)")
            
            total_pct = (total_profit / self.account_info.balance) * 100
            total_color = "🟢" if total_profit >= 0 else "🔴"
            
            logger.info(f"\n{total_color} 📊 Lucro Total das Posições: ${total_profit:.2f} ({total_pct:.2f}%)")
            
            # Atualizar PnL diário
            self.daily_pnl = total_profit
            
        except Exception as e:
            logger.error(f"Erro ao monitorar posições: {e}")
    
    def run_live_trading_session(self, duration_minutes: int = 30):
        """Executa sessão de trading ao vivo"""
        try:
            logger.info("🚀 INICIANDO SESSÃO DE TRADING AO VIVO")
            logger.info("="*60)
            logger.info(f"⏱️  Duração: {duration_minutes} minutos")
            logger.info(f"💰 Saldo inicial: ${self.account_info.balance:.2f}")
            logger.info(f"📊 Volume por trade: {self.volume_base} lotes")
            logger.info(f"🎯 Mín. confiança: {self.min_confidence:.1%}")
            logger.info("="*60)
            
            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            cycle_count = 0
            
            while datetime.now() < end_time:
                cycle_count += 1
                logger.info(f"\n🔄 CICLO {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                logger.info("-"*40)
                
                # Verificações de segurança
                if not self.check_operational_hours():
                    break
                
                if not self.check_risk_limits():
                    logger.warning("⚠️ Limites de risco atingidos, aguardando próximo ciclo...")
                    time.sleep(60)
                    continue
                
                # Monitorar posições existentes
                self.monitor_open_positions()
                
                # Escaneamento de oportunidades
                opportunities = self.scan_trading_opportunities()
                
                # Executar trades
                if opportunities:
                    executed = self.execute_trades_from_opportunities(opportunities)
                    logger.info(f"✅ {executed} trades executados neste ciclo")
                else:
                    logger.info("ℹ️ Nenhuma oportunidade neste ciclo")
                
                # Aguardar próximo ciclo (5 minutos)
                logger.info(f"⏰ Aguardando próximo ciclo...")
                time.sleep(300)  # 5 minutos
                
                # Atualizar informações da conta
                self.account_info = mt5.account_info()
            
            logger.info("\n" + "="*60)
            logger.info("🏁 SESSÃO DE TRADING FINALIZADA")
            logger.info("="*60)
            
            # Resumo final
            final_balance = self.account_info.balance
            session_pnl = final_balance - self.account_info.balance + self.daily_pnl
            
            logger.info(f"💰 Saldo final: ${final_balance:.2f}")
            logger.info(f"📈 PnL da sessão: ${session_pnl:.2f}")
            logger.info(f"📊 Total de trades: {self.daily_trades}")
            logger.info(f"⏱️  Duração: {(datetime.now() - start_time).total_seconds() / 60:.1f} minutos")
            
            # Salvar relatório
            self._save_session_report(start_time, datetime.now(), session_pnl)
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Sessão interrompida pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro durante sessão de trading: {e}")
        finally:
            logger.info("👋 Trading finalizado")
    
    def _save_session_report(self, start_time: datetime, end_time: datetime, pnl: float):
        """Salva relatório da sessão"""
        try:
            report = {
                'session_id': f"session_{start_time.strftime('%Y%m%d_%H%M%S')}",
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'initial_balance': self.account_info.balance - pnl,
                'final_balance': self.account_info.balance,
                'pnl': pnl,
                'pnl_percentage': (pnl / (self.account_info.balance - pnl)) * 100,
                'total_trades': self.daily_trades,
                'trading_parameters': {
                    'volume_base': self.volume_base,
                    'max_risk_per_trade': self.max_risk_per_trade,
                    'min_confidence': self.min_confidence,
                    'max_positions': self.max_positions
                },
                'operation_history': self.operation_history
            }
            
            filename = f"trading_session_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"📄 Relatório salvo: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")

def main():
    """Função principal"""
    print("🚀 IA GAIN + MetaTrader 5 - TRADING AO VIVO")
    print("="*60)
    print("⚠️  AVISO: Este script executará operações reais!")
    print("💡 Recomendações:")
    print("   • Use volume mínimo (0.01 lotes)")
    print("   • Monitore ativamente")
    print("   • Esteja preparado para interromper se necessário")
    print("="*60)
    
    # Confirmação do usuário
    response = input("\nDeseja iniciar a sessão de trading? (SIM/NÃO): ").upper().strip()
    if response != 'SIM':
        print("❌ Operação cancelada pelo usuário")
        return
    
    # Configurar duração
    try:
        duration = int(input("Duração da sessão em minutos (padrão: 30): ") or "30")
        if duration < 5 or duration > 120:
            print("❌ Duração deve ser entre 5 e 120 minutos")
            return
    except ValueError:
        print("❌ Valor inválido, usando 30 minutos")
        duration = 30
    
    # Criar trader
    trader = IA_GAIN_LiveTrader()
    
    # Conectar ao MT5
    if not trader.connect_to_mt5():
        print("❌ Falha ao conectar ao MT5")
        return
    
    # Executar sessão de trading
    try:
        trader.run_live_trading_session(duration)
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        if trader.connected:
            mt5.shutdown()
            print("🔌 Desconectado do MT5")

if __name__ == "__main__":
    main()