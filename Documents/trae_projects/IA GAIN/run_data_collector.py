#!/usr/bin/env python3
"""
IA GAIN - Data Collector Executor
Script executável para coleta de dados de criptomoedas
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path
from datetime import datetime

def setup_environment():
    """Configurar ambiente e paths"""
    # Adicionar o diretório src ao path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data_collector.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Verificar dependências necessárias"""
    required_packages = [
        'ccxt', 'pandas', 'numpy', 'aiohttp', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install ccxt pandas numpy aiohttp requests")
        return False
    
    return True

async def collect_market_data(symbols=None, timeframe='1h', limit=200):
    """Coletar dados de mercado"""
    try:
        from data.data_collector import DataCollector
        
        collector = DataCollector()
        await collector.initialize_exchanges()
        
        if not symbols:
            # Obter top criptomoedas
            top_coins = await collector.get_top_cryptocurrencies(limit=20)
            symbols = [f"{coin['symbol'].upper()}/USDT" for coin in top_coins]
        
        print(f"📊 Coletando dados para {len(symbols)} símbolos...")
        
        for symbol in symbols:
            try:
                print(f"Coletando dados para {symbol}...")
                
                # Dados históricos
                df = await collector.get_historical_data(symbol, timeframe, limit)
                if not df.empty:
                    # Calcular indicadores
                    df['rsi'] = collector.calculate_rsi(df['close'])
                    df['macd'], df['macd_signal'] = collector.calculate_macd(df['close'])
                    df['bb_upper'], df['bb_middle'], df['bb_lower'] = collector.calculate_bollinger_bands(df['close'])
                    
                    # Salvar dados
                    filename = f"data/{symbol.replace('/', '_')}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    os.makedirs('data', exist_ok=True)
                    df.to_csv(filename)
                    print(f"✅ Dados salvos: {filename}")
                
                # Pequena pausa para não sobrecarregar as APIs
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Erro ao coletar dados para {symbol}: {e}")
                continue
        
        print("✅ Coleta de dados concluída!")
        
    except Exception as e:
        print(f"❌ Erro geral na coleta de dados: {e}")
        raise

async def collect_fundamental_data():
    """Coletar dados fundamentais"""
    try:
        from data.data_collector import DataCollector
        
        collector = DataCollector()
        
        # Obter top criptomoedas
        top_coins = await collector.get_top_cryptocurrencies(limit=50)
        
        print(f"📈 Coletando dados fundamentais para {len(top_coins)} criptomoedas...")
        
        fundamental_data = []
        for coin in top_coins:
            try:
                coin_id = coin['id']
                symbol = coin['symbol']
                
                print(f"Coletando fundamentos para {symbol}...")
                
                # Dados fundamentais
                fundamentals = await collector.get_fundamental_data(coin_id)
                if fundamentals:
                    fundamentals.update({
                        'symbol': symbol,
                        'name': coin['name'],
                        'current_price': coin.get('current_price', 0),
                        'market_cap_rank': coin.get('market_cap_rank', 0),
                        'timestamp': datetime.now().isoformat()
                    })
                    fundamental_data.append(fundamentals)
                
                # Pequena pausa
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Erro ao coletar fundamentos para {coin['symbol']}: {e}")
                continue
        
        # Salvar dados fundamentais
        if fundamental_data:
            import pandas as pd
            df_fundamentals = pd.DataFrame(fundamental_data)
            filename = f"data/fundamentals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_fundamentals.to_csv(filename, index=False)
            print(f"✅ Dados fundamentais salvos: {filename}")
        
        print("✅ Coleta de dados fundamentais concluída!")
        
    except Exception as e:
        print(f"❌ Erro geral na coleta de fundamentos: {e}")
        raise

async def main_async(args):
    """Função principal assíncrona"""
    try:
        if args.fundamentals:
            await collect_fundamental_data()
        else:
            symbols = args.symbols.split(',') if args.symbols else None
            await collect_market_data(symbols, args.timeframe, args.limit)
            
    except KeyboardInterrupt:
        print("\n⚠️ Coleta interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="IA GAIN - Data Collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_data_collector.py                    # Coletar dados das top 20 criptomoedas
  python run_data_collector.py --symbols BTC/USDT,ETH/USDT  # Coletar dados específicos
  python run_data_collector.py --timeframe 1d    # Coletar dados diários
  python run_data_collector.py --fundamentals     # Coletar apenas dados fundamentais
  python run_data_collector.py --limit 500        # Coletar 500 candles
        """
    )
    
    parser.add_argument('--symbols', '-s', 
                       help='Símbolos para coletar (ex: BTC/USDT,ETH/USDT)')
    parser.add_argument('--timeframe', '-t', 
                       default='1h',
                       choices=['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'],
                       help='Timeframe dos dados (padrão: 1h)')
    parser.add_argument('--limit', '-l', 
                       type=int, 
                       default=200,
                       help='Número de candles para coletar (padrão: 200)')
    parser.add_argument('--fundamentals', '-f',
                       action='store_true',
                       help='Coletar apenas dados fundamentais')
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar dependências')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║              IA GAIN - Data Collector                        ║
║         Coletor de Dados de Criptomoedas                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar dependências
    if args.check:
        print("🔍 Verificando dependências...")
        if check_dependencies():
            print("✅ Todas as dependências estão instaladas")
        else:
            print("❌ Dependências faltando")
            sys.exit(1)
        return
    
    # Verificar dependências antes de executar
    if not check_dependencies():
        sys.exit(1)
    
    # Configurar ambiente
    setup_environment()
    
    # Executar coleta
    print("🚀 Iniciando coleta de dados...")
    print(f"Timeframe: {args.timeframe}")
    print(f"Limit: {args.limit}")
    
    if args.fundamentals:
        print("📈 Modo: Coleta de dados fundamentais")
    else:
        print(f"📊 Modo: Coleta de dados de mercado")
        if args.symbols:
            print(f"Símbolos: {args.symbols}")
    
    try:
        asyncio.run(main_async(args))
        print("✅ Coleta de dados finalizada com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Coleta interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()