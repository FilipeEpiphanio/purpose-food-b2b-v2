#!/usr/bin/env python3
"""
Integração IA GAIN com MetaTrader 5
Este script conecta o sistema IA GAIN ao MetaTrader 5 para trading automático
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

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

# Importar sistema IA GAIN
try:
    from ia_gain.core.ia_gain_system import IA_GAIN_System
    from ia_gain.core.base import MarketData, Signal
    from ia_gain.utils.pandas_init import pandas as pd
    IA_GAIN_AVAILABLE = True
except ImportError as e:
    logger.error(f"Sistema IA GAIN não disponível: {e}")
    IA_GAIN_AVAILABLE = False

class IA_GAIN_MT5_Integration:
    """Integração entre IA GAIN e MetaTrader 5"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.mt5_config = config.get('mt5', {})
        self.ia_config = config.get('ia_gain', {})
        self.connected = False
        self.ia_system = None
        self.trading_enabled = self.mt5_config.get('trading', {}).get('enabled', False)
        
    async def initialize(self) -> bool:
        """Inicializa conexão MT5 e sistema IA GAIN"""
        try:
            logger.info("Inicializando integração IA GAIN + MT5...")
            
            # 1. Conectar ao MT5
            if not await self._connect_mt5():
                return False
                
            # 2. Inicializar sistema IA GAIN
            if IA_GAIN_AVAILABLE:
                self.ia_system = IA_GAIN_System(self.ia_config)
                logger.info("Sistema IA GAIN inicializado")
            else:
                logger.warning("Sistema IA GAIN não disponível, usando MT5 apenas")
                
            self.connected = True
            logger.info("✅ Integração IA GAIN + MT5 estabelecida com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar integração: {e}")
            return False
    
    async def _connect_mt5(self) -> bool:
        """Conecta ao MetaTrader 5"""
        try:
            if not MT5_AVAILABLE:
                logger.error("MetaTrader5 não disponível")
                return False
                
            # Inicializar MT5
            path = self.mt5_config.get('path', '')
            if path:
                if not mt5.initialize(path=path):
                    logger.error(f"Falha ao inicializar MT5: {mt5.last_error()}")
                    return False
            else:
                if not mt5.initialize():
                    logger.error(f"Falha ao inicializar MT5: {mt5.last_error()}")
                    return False
            
            # Fazer login se credenciais fornecidas
            login = self.mt5_config.get('login')
            password = self.mt5_config.get('password')
            server = self.mt5_config.get('server')
            
            if login and password and server:
                if not mt5.login(login, password, server):
                    logger.error(f"Falha no login MT5: {mt5.last_error()}")
                    mt5.shutdown()
                    return False
                logger.info(f"✅ Login MT5 realizado: {login}")
            
            # Verificar conexão
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Falha ao obter informações da conta MT5")
                mt5.shutdown()
                return False
                
            logger.info(f"📊 Conta MT5: {account_info.login} | Saldo: ${account_info.balance:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar MT5: {e}")
            if mt5:
                mt5.shutdown()
            return False
    
    def get_market_data(self, symbol: str, timeframe: str = 'H1', count: int = 100) -> Optional[pd.DataFrame]:
        """Obtém dados de mercado do MT5 para análise IA"""
        try:
            if not MT5_AVAILABLE:
                return None
                
            # Mapear timeframes
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            # Selecionar símbolo
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Falha ao selecionar símbolo: {symbol}")
                return None
                
            # Obter dados históricos
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
            if rates is None:
                logger.error(f"Falha ao obter dados para {symbol}")
                return None
                
            # Converter para DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df['symbol'] = symbol
            
            logger.info(f"✅ Dados obtidos: {len(df)} candles de {symbol} ({timeframe})")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {e}")
            return None
    
    def analyze_market(self, symbol: str, timeframe: str = 'H1') -> Optional[Dict]:
        """Analisa mercado usando IA GAIN"""
        try:
            # Obter dados
            market_data = self.get_market_data(symbol, timeframe)
            if market_data is None:
                return None
                
            # Criar objeto MarketData
            current_price = self.get_current_price(symbol)
            if current_price is None:
                return None
                
            market_info = MarketData(
                symbol=symbol,
                timeframe=timeframe,
                current_price=current_price['ask'],
                bid_price=current_price['bid'],
                timestamp=datetime.now()
            )
            
            # Análise IA (se disponível)
            if self.ia_system:
                signal = self.ia_system.analyze(market_info, market_data)
                return {
                    'signal': signal,
                    'market_data': market_data,
                    'current_price': current_price
                }
            else:
                # Análise básica com pandas
                analysis = self._basic_analysis(market_data)
                return {
                    'analysis': analysis,
                    'market_data': market_data,
                    'current_price': current_price
                }
                
        except Exception as e:
            logger.error(f"Erro ao analisar mercado: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Obtém preço atual do símbolo"""
        try:
            if not MT5_AVAILABLE:
                return None
                
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
                
            return {
                'bid': tick.bid,
                'ask': tick.ask,
                'time': datetime.fromtimestamp(tick.time)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter preço atual: {e}")
            return None
    
    def _basic_analysis(self, market_data: pd.DataFrame) -> Dict:
        """Análise básica de mercado"""
        try:
            if len(market_data) < 10:
                return {'error': 'Dados insuficientes'}
                
            # Calcular indicadores básicos
            close_prices = market_data['close']
            
            # Médias móveis
            sma_10 = close_prices.rolling(10).mean().iloc[-1]
            sma_20 = close_prices.rolling(20).mean().iloc[-1] if len(close_prices) >= 20 else sma_10
            
            # RSI básico
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
            rs = gain / loss if loss != 0 else 1
            rsi = 100 - (100 / (1 + rs))
            
            # Tendência
            current_price = close_prices.iloc[-1]
            trend = "bullish" if current_price > sma_10 else "bearish"
            
            # Sinal básico
            signal_strength = 0
            if current_price > sma_10:
                signal_strength += 1
            if sma_10 > sma_20:
                signal_strength += 1
            if rsi < 30:
                signal_strength += 2
            elif rsi > 70:
                signal_strength -= 2
                
            if signal_strength >= 2:
                signal = "buy"
            elif signal_strength <= -2:
                signal = "sell"
            else:
                signal = "hold"
                
            return {
                'signal': signal,
                'strength': abs(signal_strength) / 4,
                'current_price': current_price,
                'sma_10': sma_10,
                'sma_20': sma_20,
                'rsi': rsi,
                'trend': trend
            }
            
        except Exception as e:
            logger.error(f"Erro na análise básica: {e}")
            return {'error': str(e)}
    
    def execute_trade(self, symbol: str, signal: str, volume: float = 0.01) -> bool:
        """Executa trade baseado em sinal IA"""
        try:
            if not self.trading_enabled or not MT5_AVAILABLE:
                logger.warning("Trading não habilitado ou MT5 não disponível")
                return False
                
            # Obter preço atual
            price_info = self.get_current_price(symbol)
            if price_info is None:
                return False
                
            # Preparar ordem
            if signal.lower() == 'buy':
                order_type = mt5.ORDER_TYPE_BUY
                price = price_info['ask']
            elif signal.lower() == 'sell':
                order_type = mt5.ORDER_TYPE_SELL
                price = price_info['bid']
            else:
                logger.info(f"Sinal {signal} - nenhuma ação tomada")
                return False
                
            # Configurar SL/TP (exemplo: 50 pips SL, 100 pips TP)
            point = mt5.symbol_info(symbol).point
            sl_distance = 50 * point
            tp_distance = 100 * point
            
            if signal.lower() == 'buy':
                sl = price - sl_distance
                tp = price + tp_distance
            else:
                sl = price + sl_distance
                tp = price - tp_distance
                
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "type": order_type,
                "volume": volume,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 234000,
                "comment": f"IA_GAIN_{signal}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Trade executado: {signal} {symbol} vol={volume} @ {price}")
                logger.info(f"   Ticket: {result.order}, SL: {sl:.5f}, TP: {tp:.5f}")
                return True
            else:
                logger.error(f"❌ Trade falhou: {result.comment} (código: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao executar trade: {e}")
            return False
    
    def get_positions(self) -> List[Dict]:
        """Obtém posições abertas"""
        try:
            if not MT5_AVAILABLE:
                return []
                
            positions = mt5.positions_get()
            if positions is None:
                return []
                
            positions_list = []
            for pos in positions:
                positions_list.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'buy' if pos.type == mt5.ORDER_TYPE_BUY else 'sell',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'comment': pos.comment
                })
                
            return positions_list
            
        except Exception as e:
            logger.error(f"Erro ao obter posições: {e}")
            return []
    
    def close_position(self, ticket: int) -> bool:
        """Fecha posição por ticket"""
        try:
            if not MT5_AVAILABLE:
                return False
                
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"Posição {ticket} não encontrada")
                return False
                
            pos = position[0]
            
            # Preparar ordem de fechamento
            if pos.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(pos.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(pos.symbol).ask
                
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "type": order_type,
                "position": pos.ticket,
                "volume": pos.volume,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "IA_GAIN_CLOSE",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Posição {ticket} fechada com sucesso")
                return True
            else:
                logger.error(f"❌ Falha ao fechar posição {ticket}: {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao fechar posição: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do MT5"""
        try:
            if MT5_AVAILABLE and mt5:
                mt5.shutdown()
                self.connected = False
                logger.info("Desconectado do MetaTrader 5")
        except Exception as e:
            logger.error(f"Erro ao desconectar: {e}")

async def main():
    """Função principal de demonstração"""
    
    print("🚀 IA GAIN + MetaTrader 5 Integration")
    print("=" * 50)
    
    # Configuração
    config = {
        "mt5": {
            "login": 0,  # Usar conta atual
            "password": "",
            "server": "",
            "trading": {
                "enabled": True
            }
        },
        "ia_gain": {
            "enabled": True
        }
    }
    
    # Criar integração
    integration = IA_GAIN_MT5_Integration(config)
    
    # Inicializar
    if await integration.initialize():
        print("\n✅ Integração estabelecida com sucesso!")
        
        # Testar análise de mercado
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        
        for symbol in symbols:
            print(f"\n📊 Analisando {symbol}...")
            analysis = integration.analyze_market(symbol, "H1")
            
            if analysis:
                if 'signal' in analysis:
                    signal = analysis['signal']
                    print(f"   Sinal IA: {signal.signal} (força: {signal.strength:.2f})")
                elif 'analysis' in analysis:
                    basic_analysis = analysis['analysis']
                    print(f"   Sinal: {basic_analysis['signal']} (força: {basic_analysis['strength']:.2f})")
                    print(f"   RSI: {basic_analysis['rsi']:.1f}")
                    print(f"   Tendência: {basic_analysis['trend']}")
                
                # Executar trade se sinal forte
                if analysis.get('analysis', {}).get('strength', 0) >= 0.5:
                    if integration.trading_enabled:
                        signal_type = analysis['analysis']['signal']
                        print(f"   🚀 Executando trade: {signal_type}")
                        integration.execute_trade(symbol, signal_type)
                    else:
                        print("   ⚠️  Trading desabilitado")
            else:
                print(f"   ❌ Falha na análise")
        
        # Mostrar posições
        positions = integration.get_positions()
        if positions:
            print(f"\n📍 Posições abertas ({len(positions)}):")
            for pos in positions:
                profit_color = "🟢" if pos['profit'] >= 0 else "🔴"
                print(f"   {profit_color} {pos['symbol']} {pos['type']} vol={pos['volume']} profit=${pos['profit']:.2f}")
        else:
            print("\n📍 Nenhuma posição aberta")
        
        # Aguardar antes de desconectar
        print("\n⏳ Aguardando 10 segundos...")
        await asyncio.sleep(10)
        
        # Desconectar
        integration.disconnect()
        print("\n👋 Integração finalizada")
        
    else:
        print("\n❌ Falha na integração")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Execução interrompida")
    except Exception as e:
        print(f"\n❌ Erro: {e}")