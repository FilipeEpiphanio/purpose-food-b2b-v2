#!/usr/bin/env python3
"""
IA GAIN - Exchange Manager
Gerenciamento e monitoramento de exchanges
"""

import asyncio
import sys
import os
from pathlib import Path
import argparse
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    import ccxt
    import pandas as pd
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("Instale com: pip install ccxt pandas python-dotenv")
    sys.exit(1)

from utils.config_manager import ConfigManager
from utils.logger import setup_logger


class ExchangeManager:
    """Gerenciador de Exchanges para IA GAIN"""
    
    def __init__(self, config_path: str = None):
        self.config = ConfigManager(config_path)
        self.logger = setup_logger('ExchangeManager')
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.exchange_status: Dict[str, Dict] = {}
        
    def setup_environment(self):
        """Configurar ambiente e variáveis"""
        load_dotenv()
        
        # Criar diretórios necessários
        directories = [
            'logs',
            'data',
            'backtests',
            'exports'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            
    def check_dependencies(self) -> bool:
        """Verificar dependências necessárias"""
        required_packages = [
            'ccxt', 'pandas', 'numpy', 'python-dotenv', 'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
            print("Instale com: pip install ccxt pandas numpy python-dotenv requests")
            return False
        
        return True
        
    def check_config(self) -> bool:
        """Verificar configuração necessária"""
        try:
            config = self.config.get_config()
            
            # Verificar seção de API
            if 'api' not in config:
                print("❌ Seção 'api' não encontrada na configuração")
                return False
                
            # Verificar exchanges configuradas
            api_config = config.get('api', {})
            if not api_config:
                print("❌ Nenhuma exchange configurada na seção 'api'")
                return False
                
            print(f"📊 Exchanges configuradas: {list(api_config.keys())}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar configuração: {e}")
            return False
            
    async def initialize_exchanges(self):
        """Inicializar todas as exchanges configuradas"""
        try:
            config = self.config.get_config()
            api_config = config.get('api', {})
            
            self.logger.info(f"Inicializando {len(api_config)} exchanges...")
            
            for exchange_name, exchange_config in api_config.items():
                try:
                    await self._initialize_single_exchange(exchange_name, exchange_config)
                except Exception as e:
                    self.logger.error(f"Erro ao inicializar {exchange_name}: {e}")
                    self.exchange_status[exchange_name] = {
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    
            self.logger.info(f"Exchanges inicializadas: {len(self.exchanges)}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar exchanges: {e}")
            raise
            
    async def _initialize_single_exchange(self, exchange_name: str, exchange_config: Dict):
        """Inicializar exchange individual"""
        try:
            # Configurações específicas por exchange
            if exchange_name == 'binance':
                exchange = ccxt.binance({
                    'apiKey': exchange_config.get('api_key', ''),
                    'secret': exchange_config.get('api_secret', ''),
                    'sandbox': exchange_config.get('testnet', True),
                    'enableRateLimit': True,
                })
            elif exchange_name == 'coinbase':
                exchange = ccxt.coinbasepro({
                    'apiKey': exchange_config.get('api_key', ''),
                    'secret': exchange_config.get('api_secret', ''),
                    'password': exchange_config.get('passphrase', ''),
                    'enableRateLimit': True,
                })
            elif exchange_name == 'kraken':
                exchange = ccxt.kraken({
                    'apiKey': exchange_config.get('api_key', ''),
                    'secret': exchange_config.get('api_secret', ''),
                    'enableRateLimit': True,
                })
            elif exchange_name == 'oanda':
                exchange = ccxt.oanda({
                    'apiKey': exchange_config.get('api_key', ''),
                    'password': exchange_config.get('api_secret', ''),
                    'sandbox': exchange_config.get('sandbox', True),
                    'enableRateLimit': True,
                })
            elif exchange_name == 'fxcm':
                exchange = ccxt.fxcm({
                    'apiKey': exchange_config.get('api_key', ''),
                    'password': exchange_config.get('api_secret', ''),
                    'sandbox': exchange_config.get('sandbox', True),
                    'enableRateLimit': True,
                })
            else:
                # Exchange genérica
                exchange_class = getattr(ccxt, exchange_name, None)
                if exchange_class:
                    exchange = exchange_class({
                        'apiKey': exchange_config.get('api_key', ''),
                        'secret': exchange_config.get('api_secret', ''),
                        'enableRateLimit': True,
                    })
                else:
                    raise ValueError(f"Exchange {exchange_name} não suportada")
                    
            # Carregar mercados
            await exchange.load_markets()
            
            # Testar conexão
            try:
                balance = await exchange.fetch_balance()
                status = 'connected'
                error = None
            except Exception as e:
                status = 'connected_no_balance'
                error = str(e)
                
            self.exchanges[exchange_name] = exchange
            self.exchange_status[exchange_name] = {
                'status': status,
                'markets': len(exchange.symbols) if hasattr(exchange, 'symbols') else 0,
                'timeframes': list(exchange.timeframes.keys()) if hasattr(exchange, 'timeframes') else [],
                'error': error,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Exchange {exchange_name} inicializada: {status}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar {exchange_name}: {e}")
            raise
            
    async def test_exchange_apis(self) -> Dict[str, Dict]:
        """Testar APIs das exchanges"""
        results = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                self.logger.info(f"Testando API da {exchange_name}...")
                
                # Testar fetch_balance
                balance_test = await self._test_balance_fetch(exchange)
                
                # Testar fetch_ticker
                ticker_test = await self._test_ticker_fetch(exchange)
                
                # Testar fetch_order_book
                orderbook_test = await self._test_orderbook_fetch(exchange)
                
                results[exchange_name] = {
                    'balance_test': balance_test,
                    'ticker_test': ticker_test,
                    'orderbook_test': orderbook_test,
                    'overall_status': 'healthy' if all([balance_test['status'] == 'success', 
                                                       ticker_test['status'] == 'success']) else 'degraded'
                }
                
            except Exception as e:
                results[exchange_name] = {
                    'error': str(e),
                    'overall_status': 'error'
                }
                
        return results
        
    async def _test_balance_fetch(self, exchange: ccxt.Exchange) -> Dict:
        """Testar fetch de balanço"""
        try:
            start_time = datetime.now()
            balance = await exchange.fetch_balance()
            end_time = datetime.now()
            
            return {
                'status': 'success',
                'response_time_ms': (end_time - start_time).total_seconds() * 1000,
                'total_currencies': len(balance),
                'has_usdt': 'USDT' in balance
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
            
    async def _test_ticker_fetch(self, exchange: ccxt.Exchange) -> Dict:
        """Testar fetch de ticker"""
        try:
            # Selecionar símbolo comum
            symbols = getattr(exchange, 'symbols', [])
            if not symbols:
                return {'status': 'error', 'error': 'No symbols available'}
                
            test_symbol = symbols[0] if 'BTC/USDT' not in symbols else 'BTC/USDT'
            
            start_time = datetime.now()
            ticker = await exchange.fetch_ticker(test_symbol)
            end_time = datetime.now()
            
            return {
                'status': 'success',
                'response_time_ms': (end_time - start_time).total_seconds() * 1000,
                'symbol': test_symbol,
                'last_price': ticker.get('last', 0),
                'bid': ticker.get('bid', 0),
                'ask': ticker.get('ask', 0)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
            
    async def _test_orderbook_fetch(self, exchange: ccxt.Exchange) -> Dict:
        """Testar fetch de order book"""
        try:
            symbols = getattr(exchange, 'symbols', [])
            if not symbols:
                return {'status': 'error', 'error': 'No symbols available'}
                
            test_symbol = symbols[0] if 'BTC/USDT' not in symbols else 'BTC/USDT'
            
            start_time = datetime.now()
            orderbook = await exchange.fetch_order_book(test_symbol)
            end_time = datetime.now()
            
            return {
                'status': 'success',
                'response_time_ms': (end_time - start_time).total_seconds() * 1000,
                'symbol': test_symbol,
                'bids': len(orderbook.get('bids', [])),
                'asks': len(orderbook.get('asks', [])),
                'spread': orderbook.get('asks', [[0]])[0][0] - orderbook.get('bids', [[0]])[0][0]
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def list_exchanges(self) -> Dict[str, Dict]:
        """Listar exchanges e seu status"""
        return {
            'exchanges': self.exchange_status,
            'connected': len([e for e in self.exchange_status.values() if e.get('status') == 'connected']),
            'total': len(self.exchange_status)
        }
        
    async def get_exchange_info(self, exchange_name: str) -> Optional[Dict]:
        """Obter informações detalhadas de uma exchange"""
        if exchange_name not in self.exchanges:
            return None
            
        exchange = self.exchanges[exchange_name]
        
        try:
            info = {
                'name': exchange_name,
                'status': self.exchange_status.get(exchange_name, {}),
                'markets': len(exchange.symbols) if hasattr(exchange, 'symbols') else 0,
                'timeframes': list(exchange.timeframes.keys()) if hasattr(exchange, 'timeframes') else [],
                'has': {
                    'fetch_balance': exchange.has.get('fetchBalance', False),
                    'fetch_ticker': exchange.has.get('fetchTicker', False),
                    'fetch_order_book': exchange.has.get('fetchOrderBook', False),
                    'create_order': exchange.has.get('createOrder', False),
                    'cancel_order': exchange.has.get('cancelOrder', False),
                    'fetch_orders': exchange.has.get('fetchOrders', False),
                    'fetch_trades': exchange.has.get('fetchTrades', False),
                }
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Erro ao obter info da {exchange_name}: {e}")
            return None
            
    async def monitor_exchanges(self, duration_minutes: int = 5):
        """Monitorar exchanges por um período"""
        self.logger.info(f"Monitorando exchanges por {duration_minutes} minutos...")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                # Testar APIs
                test_results = await self.test_exchange_apis()
                
                # Mostrar status
                print(f"\n📊 Status das Exchanges - {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 60)
                
                for exchange_name, result in test_results.items():
                    status_icon = "✅" if result['overall_status'] == 'healthy' else "⚠️" if result['overall_status'] == 'degraded' else "❌"
                    print(f"{status_icon} {exchange_name:12} - {result['overall_status']}")
                    
                print(f"\n🔄 Próxima verificação em 60 segundos...")
                await asyncio.sleep(60)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoramento interrompido")
                break
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                await asyncio.sleep(60)
                
    def export_exchange_data(self, filename: str = None):
        """Exportar dados das exchanges"""
        if not filename:
            filename = f"exchange_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'exchanges': self.exchange_status,
                'total_connected': len([e for e in self.exchange_status.values() 
                                      if e.get('status') in ['connected', 'connected_no_balance']])
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Dados exportados para {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar dados: {e}")
            return None
            
    async def close(self):
        """Fechar conexões"""
        try:
            for exchange_name, exchange in self.exchanges.items():
                try:
                    await exchange.close()
                    self.logger.info(f"Exchange {exchange_name} fechada")
                except Exception as e:
                    self.logger.error(f"Erro ao fechar {exchange_name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao fechar exchanges: {e}")


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='IA GAIN - Exchange Manager')
    parser.add_argument('--mode', choices=['list', 'test', 'monitor', 'info', 'export'], 
                       default='list', help='Modo de operação')
    parser.add_argument('--exchange', type=str, help='Nome específico da exchange')
    parser.add_argument('--duration', type=int, default=5, help='Duração do monitoramento em minutos')
    parser.add_argument('--config', type=str, help='Caminho do arquivo de configuração')
    parser.add_argument('--output', type=str, help='Arquivo de saída para exportação')
    
    args = parser.parse_args()
    
    # Inicializar gerenciador
    manager = ExchangeManager(args.config)
    
    # Configurar ambiente
    manager.setup_environment()
    
    # Verificar dependências
    if not manager.check_dependencies():
        return 1
        
    # Verificar configuração
    if not manager.check_config():
        return 1
        
    try:
        # Inicializar exchanges
        await manager.initialize_exchanges()
        
        # Executar modo solicitado
        if args.mode == 'list':
            print("\n📋 Lista de Exchanges")
            print("=" * 50)
            info = manager.list_exchanges()
            
            for exchange_name, status in manager.exchange_status.items():
                status_icon = "✅" if status.get('status') == 'connected' else "⚠️" if status.get('status') == 'connected_no_balance' else "❌"
                print(f"{status_icon} {exchange_name:15} - {status.get('status', 'unknown')}")
                print(f"   Mercados: {status.get('markets', 0)}")
                print(f"   Timeframes: {len(status.get('timeframes', []))}")
                if status.get('error'):
                    print(f"   Erro: {status.get('error')}")
                print()
                
            print(f"Total: {info['total']} | Conectadas: {info['connected']}")
            
        elif args.mode == 'test':
            print("\n🧪 Testando APIs das Exchanges")
            print("=" * 50)
            
            results = await manager.test_exchange_apis()
            
            for exchange_name, result in results.items():
                status_icon = "✅" if result['overall_status'] == 'healthy' else "⚠️"
                print(f"\n{status_icon} {exchange_name}")
                print(f"   Status: {result['overall_status']}")
                
                if 'balance_test' in result:
                    bt = result['balance_test']
                    print(f"   Balance: {bt.get('status', 'unknown')} ({bt.get('response_time_ms', 0):.0f}ms)")
                    
                if 'ticker_test' in result:
                    tt = result['ticker_test']
                    print(f"   Ticker: {tt.get('status', 'unknown')} ({tt.get('response_time_ms', 0):.0f}ms)")
                    
        elif args.mode == 'monitor':
            print(f"\n👁️  Monitorando Exchanges por {args.duration} minutos")
            print("Pressione Ctrl+C para interromper")
            print("=" * 50)
            
            await manager.monitor_exchanges(args.duration)
            
        elif args.mode == 'info':
            if not args.exchange:
                print("❌ Especifique uma exchange com --exchange")
                return 1
                
            print(f"\nℹ️  Informações da Exchange: {args.exchange}")
            print("=" * 50)
            
            info = await manager.get_exchange_info(args.exchange)
            if info:
                print(json.dumps(info, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Exchange {args.exchange} não encontrada ou não inicializada")
                
        elif args.mode == 'export':
            output_file = args.output or f"exchange_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            print(f"\n💾 Exportando dados para {output_file}")
            print("=" * 50)
            
            filename = manager.export_exchange_data(output_file)
            if filename:
                print(f"✅ Dados exportados com sucesso para: {filename}")
            else:
                print("❌ Erro ao exportar dados")
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        manager.logger.error(f"Erro na execução: {e}")
        return 1
    finally:
        await manager.close()
        
    return 0


if __name__ == "__main__":
    # Adicionar o diretório src ao path para imports
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    from datetime import timedelta
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)