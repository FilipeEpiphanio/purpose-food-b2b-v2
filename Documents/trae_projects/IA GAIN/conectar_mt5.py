#!/usr/bin/env python3
"""
Script de conexão MetaTrader 5 para IA GAIN
Este script estabelece conexão com o MetaTrader 5 e testa as funcionalidades
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    logger.info("MetaTrader5 library imported successfully")
except ImportError:
    MT5_AVAILABLE = False
    logger.error("MetaTrader5 library not available. Please install: pip install MetaTrader5")
    mt5 = None

class MT5Connection:
    """Gerenciador de conexão MetaTrader 5"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.connected = False
        self.account_info = None
        
    def connect(self) -> bool:
        """Conecta ao MetaTrader 5"""
        try:
            if not MT5_AVAILABLE:
                logger.error("MetaTrader5 library not available")
                return False
                
            # Inicializar MT5
            logger.info("Inicializando MetaTrader 5...")
            
            # Obter configurações
            login = self.config.get('login')
            password = self.config.get('password')
            server = self.config.get('server')
            path = self.config.get('path', '')
            
            # Inicializar com caminho se especificado
            if path:
                if not mt5.initialize(path=path):
                    logger.error(f"Falha ao inicializar MT5 com caminho: {path}")
                    return False
            else:
                if not mt5.initialize():
                    logger.error("Falha ao inicializar MT5")
                    return False
            
            logger.info("MT5 inicializado com sucesso")
            
            # Fazer login se credenciais fornecidas
            if login and password and server:
                logger.info(f"Tentando login com conta: {login}")
                if not mt5.login(login, password, server):
                    logger.error(f"Falha no login: {mt5.last_error()}")
                    mt5.shutdown()
                    return False
                logger.info(f"Login realizado com sucesso: {login}")
            
            # Verificar conexão
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Falha ao obter informações da conta")
                mt5.shutdown()
                return False
                
            self.connected = True
            self.account_info = account_info
            
            logger.info(f"✅ Conectado ao MetaTrader 5!")
            logger.info(f"📊 Conta: {account_info.login}")
            logger.info(f"💰 Saldo: ${account_info.balance:.2f}")
            logger.info(f"📈 Equity: ${account_info.equity:.2f}")
            logger.info(f"🏢 Servidor: {account_info.server}")
            logger.info(f"👤 Nome: {account_info.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar MT5: {e}")
            if mt5:
                mt5.shutdown()
            return False
    
    def disconnect(self):
        """Desconecta do MetaTrader 5"""
        try:
            if self.connected and mt5:
                mt5.shutdown()
                self.connected = False
                logger.info("Desconectado do MetaTrader 5")
        except Exception as e:
            logger.error(f"Erro ao desconectar MT5: {e}")
    
    def get_symbols(self, limit: int = 10):
        """Obtém lista de símbolos disponíveis"""
        try:
            if not self.connected:
                logger.error("Não conectado ao MT5")
                return []
                
            symbols = mt5.symbols_get()
            if symbols is None:
                logger.error("Falha ao obter símbolos")
                return []
                
            logger.info(f"Encontrados {len(symbols)} símbolos")
            
            # Retornar primeiros símbolos
            symbols_list = []
            for i, symbol in enumerate(symbols[:limit]):
                symbols_list.append({
                    'name': symbol.name,
                    'description': symbol.description,
                    'spread': symbol.spread,
                    'point': symbol.point,
                    'trade_contract_size': symbol.trade_contract_size
                })
                
            return symbols_list
            
        except Exception as e:
            logger.error(f"Erro ao obter símbolos: {e}")
            return []
    
    def get_market_data(self, symbol: str, timeframe: str = 'H1', count: int = 100):
        """Obtém dados de mercado"""
        try:
            if not self.connected:
                logger.error("Não conectado ao MT5")
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
            import pandas as pd
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            logger.info(f"✅ Dados obtidos: {len(df)} candles de {symbol} ({timeframe})")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {e}")
            return None
    
    def get_current_price(self, symbol: str):
        """Obtém preço atual do símbolo"""
        try:
            if not self.connected:
                logger.error("Não conectado ao MT5")
                return None
                
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Falha ao obter tick para {symbol}")
                return None
                
            return {
                'bid': tick.bid,
                'ask': tick.ask,
                'time': datetime.fromtimestamp(tick.time)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter preço atual: {e}")
            return None
    
    def get_positions(self):
        """Obtém posições abertas"""
        try:
            if not self.connected:
                logger.error("Não conectado ao MT5")
                return []
                
            positions = mt5.positions_get()
            if positions is None:
                logger.error("Falha ao obter posições")
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
                    'tp': pos.tp
                })
                
            return positions_list
            
        except Exception as e:
            logger.error(f"Erro ao obter posições: {e}")
            return []

async def main():
    """Função principal para testar conexão MT5"""
    
    print("🚀 Iniciando conexão MetaTrader 5")
    print("=" * 50)
    
    # Configuração de exemplo (substitua com suas credenciais reais)
    config = {
        "login": 12345678,  # Substitua com seu login
        "password": "your_password",  # Substitua com sua senha
        "server": "YourBroker-Server",  # Substitua com seu servidor
        "path": ""  # Caminho opcional para o terminal MT5
    }
    
    # Também pode carregar de arquivo config.json
    try:
        with open('config.json', 'r') as f:
            file_config = json.load(f)
            config.update(file_config.get('mt5', {}))
            logger.info("Configuração carregada de config.json")
    except FileNotFoundError:
        logger.info("Arquivo config.json não encontrado, usando configuração padrão")
    except Exception as e:
        logger.warning(f"Erro ao carregar config.json: {e}")
    
    # Criar conexão MT5
    mt5_conn = MT5Connection(config)
    
    # Conectar
    if await asyncio.to_thread(mt5_conn.connect):
        print("\n✅ Conexão estabelecida com sucesso!")
        
        # Testar funcionalidades
        print("\n📊 Testando funcionalidades...")
        
        # Obter símbolos
        symbols = mt5_conn.get_symbols(5)
        if symbols:
            print(f"\n📈 Símbolos disponíveis ({len(symbols)}):")
            for symbol in symbols:
                print(f"  - {symbol['name']}: {symbol['description']}")
        
        # Obter preço atual (exemplo com EURUSD)
        current_price = mt5_conn.get_current_price("EURUSD")
        if current_price:
            print(f"\n💰 Preço atual EURUSD:")
            print(f"  - Bid: {current_price['bid']}")
            print(f"  - Ask: {current_price['ask']}")
        
        # Obter dados históricos
        market_data = mt5_conn.get_market_data("EURUSD", "H1", 10)
        if market_data is not None:
            print(f"\n📊 Dados históricos EURUSD (H1, últimos 10 candles):")
            print(market_data.head())
        
        # Obter posições
        positions = mt5_conn.get_positions()
        if positions:
            print(f"\n📍 Posições abertas ({len(positions)}):")
            for pos in positions:
                print(f"  - {pos['symbol']} {pos['type']} vol={pos['volume']} profit=${pos['profit']:.2f}")
        else:
            print("\n📍 Nenhuma posição aberta")
        
        # Manter conexão por um momento
        print("\n⏳ Mantendo conexão por 5 segundos...")
        await asyncio.sleep(5)
        
        # Desconectar
        mt5_conn.disconnect()
        print("\n👋 Desconectado do MetaTrader 5")
        
    else:
        print("\n❌ Falha na conexão com MetaTrader 5")
        print("Verifique:")
        print("  - Se o MetaTrader 5 está instalado")
        print("  - Se o terminal está aberto")
        print("  - As credenciais de login/servidor")
        print("  - A conexão com a internet")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")