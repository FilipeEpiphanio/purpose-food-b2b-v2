#!/usr/bin/env python3
"""
IA GAIN - Crypto Selector Executor
Script executável para análise e seleção de criptomoedas
"""

import os
import sys
import argparse
import asyncio
import json
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
            logging.FileHandler('crypto_selector.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Verificar dependências necessárias"""
    required_packages = [
        'ccxt', 'pandas', 'numpy', 'aiohttp', 'requests', 'scikit-learn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install ccxt pandas numpy aiohttp requests scikit-learn")
        return False
    
    return True

async def analyze_cryptocurrencies(limit=50, min_volume=1000000, min_market_cap=10000000):
    """Analisar e selecionar as melhores criptomoedas"""
    try:
        from analysis.crypto_selector import CryptoSelector
        
        selector = CryptoSelector()
        await selector.initialize_exchanges()
        
        print(f"🔍 Analisando top {limit} criptomoedas...")
        print(f"Filtros: Volume mínimo: ${min_volume:,.0f}, Market Cap mínimo: ${min_market_cap:,.0f}")
        
        # Obter criptomoedas recomendadas
        recommendations = await selector.get_recommendations(
            top_coins_limit=limit,
            min_volume=min_volume,
            min_market_cap=min_market_cap
        )
        
        if not recommendations:
            print("❌ Nenhuma criptomoeda atendeu aos critérios")
            return
        
        print(f"\n✅ Encontradas {len(recommendations)} criptomoedas recomendadas:")
        print("-" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['symbol']} - Score: {rec['score']:.2f}/100")
            print(f"   Nome: {rec['name']}")
            print(f"   Preço: ${rec.get('current_price', 0):,.4f}")
            print(f"   Market Cap: ${rec.get('market_cap', 0):,.0f}")
            print(f"   Volume 24h: ${rec.get('total_volume', 0):,.0f}")
            print(f"   Recomendação: {rec['recommendation']}")
            
            if 'reasoning' in rec and rec['reasoning']:
                print(f"   Razões: {rec['reasoning']}")
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"crypto_analysis_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Resultados salvos em: {results_file}")
        
        # Gerar relatório em CSV também
        import pandas as pd
        df = pd.DataFrame(recommendations)
        csv_file = f"crypto_analysis_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
        print(f"✅ Relatório CSV salvo em: {csv_file}")
        
    except Exception as e:
        print(f"❌ Erro na análise de criptomoedas: {e}")
        raise

async def detailed_analysis(symbol):
    """Análise detalhada de uma criptomoeda específica"""
    try:
        from analysis.crypto_selector import CryptoSelector
        
        selector = CryptoSelector()
        await selector.initialize_exchanges()
        
        print(f"🔍 Análise detalhada para {symbol}...")
        
        # Analisar criptomoeda específica
        analysis = await selector.analyze_crypto(symbol)
        
        if not analysis:
            print(f"❌ Não foi possível analisar {symbol}")
            return
        
        print(f"\n📊 Resultados da análise para {symbol}:")
        print("-" * 60)
        
        print(f"Símbolo: {analysis.get('symbol', 'N/A')}")
        print(f"Nome: {analysis.get('name', 'N/A')}")
        print(f"Score: {analysis.get('score', 0):.2f}/100")
        print(f"Recomendação: {analysis.get('recommendation', 'N/A')}")
        
        if 'metrics' in analysis:
            metrics = analysis['metrics']
            print(f"\n📈 Métricas:")
            print(f"  Preço atual: ${metrics.get('current_price', 0):,.4f}")
            print(f"  Market Cap: ${metrics.get('market_cap', 0):,.0f}")
            print(f"  Volume 24h: ${metrics.get('total_volume', 0):,.0f}")
            print(f"  Market Cap Rank: #{metrics.get('market_cap_rank', 'N/A')}")
            print(f"  Supply circulante: {metrics.get('circulating_supply', 0):,.0f}")
            print(f"  Supply total: {metrics.get('total_supply', 0):,.0f}")
        
        if 'technical_analysis' in analysis:
            tech = analysis['technical_analysis']
            print(f"\n📊 Análise Técnica:")
            print(f"  RSI: {tech.get('rsi', 0):.2f}")
            print(f"  MACD: {tech.get('macd', 0):.4f}")
            print(f"  Sinal MACD: {tech.get('macd_signal', 0):.4f}")
            print(f"  Bollinger Upper: ${tech.get('bb_upper', 0):,.4f}")
            print(f"  Bollinger Middle: ${tech.get('bb_middle', 0):,.4f}")
            print(f"  Bollinger Lower: ${tech.get('bb_lower', 0):,.4f}")
        
        if 'volatility' in analysis:
            vol = analysis['volatility']
            print(f"\n📉 Volatilidade:")
            print(f"  Volatilidade 24h: {vol.get('volatility_24h', 0):.2f}%")
            print(f"  Volatilidade 7d: {vol.get('volatility_7d', 0):.2f}%")
            print(f"  Beta: {vol.get('beta', 0):.2f}")
        
        if 'reasoning' in analysis:
            print(f"\n💡 Razões da análise:")
            print(f"  {analysis['reasoning']}")
        
        # Salvar análise detalhada
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"detailed_analysis_{symbol.replace('/', '_')}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Análise detalhada salva em: {filename}")
        
    except Exception as e:
        print(f"❌ Erro na análise detalhada: {e}")
        raise

async def main_async(args):
    """Função principal assíncrona"""
    try:
        if args.symbol:
            await detailed_analysis(args.symbol)
        else:
            await analyze_cryptocurrencies(
                limit=args.limit,
                min_volume=args.min_volume,
                min_market_cap=args.min_market_cap
            )
            
    except KeyboardInterrupt:
        print("\n⚠️ Análise interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="IA GAIN - Crypto Selector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_crypto_selector.py                    # Analisar top 50 criptomoedas
  python run_crypto_selector.py --limit 20         # Analisar top 20
  python run_crypto_selector.py --symbol BTC/USDT  # Análise detalhada do BTC
  python run_crypto_selector.py --min-volume 5000000  # Filtrar por volume mínimo
  python run_crypto_selector.py --min-market-cap 50000000  # Filtrar por market cap mínimo
        """
    )
    
    parser.add_argument('--limit', '-l',
                       type=int,
                       default=50,
                       help='Número de criptomoedas para analisar (padrão: 50)')
    parser.add_argument('--symbol', '-s',
                       help='Análise detalhada de um símbolo específico (ex: BTC/USDT)')
    parser.add_argument('--min-volume',
                       type=float,
                       default=1000000,
                       help='Volume mínimo em USD (padrão: 1M)')
    parser.add_argument('--min-market-cap',
                       type=float,
                       default=10000000,
                       help='Market cap mínimo em USD (padrão: 10M)')
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar dependências')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║              IA GAIN - Crypto Selector                     ║
║         Seletor de Criptomoedas com IA                     ║
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
    
    # Executar análise
    if args.symbol:
        print(f"🔍 Executando análise detalhada para {args.symbol}...")
    else:
        print(f"🔍 Executando análise para top {args.limit} criptomoedas...")
        print(f"Filtros: Volume ≥ ${args.min_volume:,.0f}, Market Cap ≥ ${args.min_market_cap:,.0f}")
    
    try:
        asyncio.run(main_async(args))
        print("✅ Análise concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Análise interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()