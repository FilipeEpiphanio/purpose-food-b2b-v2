#!/usr/bin/env python3
"""
IA GAIN - Automated Trading Executor
Script executável para trading automatizado de criptomoedas
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
            logging.FileHandler('automated_trading.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
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

def check_config():
    """Verificar configurações necessárias"""
    config_file = 'config.json'
    if not os.path.exists(config_file):
        print("❌ Arquivo config.json não encontrado")
        print("Execute: python ia_gain.py --config")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Verificar se pelo menos uma exchange está configurada
        exchanges_configured = False
        for exchange_name, exchange_config in config.get('exchanges', {}).items():
            if exchange_config.get('enabled', False):
                if exchange_config.get('api_key') and exchange_config.get('api_secret'):
                    exchanges_configured = True
                    break
        
        if not exchanges_configured:
            print("⚠️  Atenção: Nenhuma exchange configurada com API keys")
            print("O sistema funcionará em modo teste (simulação)")
            print("Configure suas APIs no config.json ou use a interface gráfica")
            
            response = input("Continuar em modo teste? (s/N): ")
            if response.lower() != 's':
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

async def start_trading(symbols=None, test_mode=True, max_positions=5):
    """Iniciar trading automatizado"""
    try:
        from trading.automated_trading import AutomatedTrading
        
        # Criar arquivo de configuração temporário se não existir
        config_file = 'config.json'
        if not os.path.exists(config_file):
            default_config = {
                "trading": {
                    "enabled": True,
                    "max_positions": max_positions,
                    "risk_per_trade": 2.0,
                    "min_balance": 100.0,
                    "default_leverage": 1,
                    "test_mode": test_mode
                },
                "risk_management": {
                    "stop_loss": 5.0,
                    "take_profit": 10.0,
                    "max_drawdown": 20.0,
                    "position_size_percentage": 10.0,
                    "max_daily_loss": 50.0
                },
                "technical_analysis": {
                    "rsi_period": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30,
                    "macd_fast": 12,
                    "macd_slow": 26,
                    "macd_signal": 9,
                    "bollinger_period": 20,
                    "bollinger_std": 2,
                    "ema_short": 12,
                    "ema_long": 26
                },
                "exchanges": {
                    "binance": {
                        "enabled": False,
                        "api_key": "",
                        "api_secret": "",
                        "sandbox": True
                    },
                    "bybit": {
                        "enabled": False,
                        "api_key": "",
                        "api_secret": "",
                        "sandbox": True
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        # Inicializar sistema de trading
        trading_system = AutomatedTrading(config_file)
        
        print("🚀 Iniciando sistema de trading automatizado...")
        print(f"Modo: {'TESTE' if test_mode else 'REAL'}")
        print(f"Máximo de posições: {max_positions}")
        
        if symbols:
            print(f"Símbolos configurados: {', '.join(symbols)}")
        
        # Configurar símbolos para trading
        if symbols:
            trading_system.config['trading']['symbols'] = symbols
        
        # Iniciar o sistema
        await trading_system.run()
        
    except KeyboardInterrupt:
        print("\n⚠️ Trading interrompido pelo usuário")
        raise
    except Exception as e:
        print(f"❌ Erro no trading: {e}")
        raise

async def backtest_strategy(symbols=None, days=30):
    """Executar backtest de estratégias"""
    try:
        from trading.automated_trading import AutomatedTrading
        
        print(f"📊 Executando backtest para os últimos {days} dias...")
        
        trading_system = AutomatedTrading()
        
        # Executar backtest
        results = await trading_system.backtest(
            symbols=symbols,
            days=days
        )
        
        print("\n📈 Resultados do Backtest:")
        print("-" * 50)
        print(f"Período: {results.get('period', 'N/A')}")
        print(f"Total de trades: {results.get('total_trades', 0)}")
        print(f"Trades vencedores: {results.get('winning_trades', 0)}")
        print(f"Trades perdedores: {results.get('losing_trades', 0)}")
        print(f"Taxa de acerto: {results.get('win_rate', 0):.2f}%")
        print(f"Retorno total: {results.get('total_return', 0):.2f}%")
        print(f"Retorno médio por trade: {results.get('avg_return', 0):.2f}%")
        print(f"Drawdown máximo: {results.get('max_drawdown', 0):.2f}%")
        print(f"Sharpe ratio: {results.get('sharpe_ratio', 0):.2f}")
        
        # Salvar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backtest_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Resultados salvos em: {filename}")
        
    except Exception as e:
        print(f"❌ Erro no backtest: {e}")
        raise

async def show_portfolio_summary():
    """Mostrar resumo da carteira"""
    try:
        from trading.automated_trading import AutomatedTrading
        
        trading_system = AutomatedTrading()
        
        # Obter resumo da carteira
        summary = await trading_system.get_portfolio_summary()
        
        print("\n💼 Resumo da Carteira:")
        print("-" * 50)
        print(f"Saldo total: ${summary.get('total_balance', 0):,.2f}")
        print(f"Saldo disponível: ${summary.get('available_balance', 0):,.2f}")
        print(f"Valor em posições: ${summary.get('positions_value', 0):,.2f}")
        print(f"Lucro/prejuízo total: ${summary.get('total_pnl', 0):,.2f}")
        print(f"Número de posições abertas: {summary.get('open_positions', 0)}")
        
        if 'positions' in summary and summary['positions']:
            print("\n📋 Posições Abertas:")
            for position in summary['positions']:
                print(f"  {position.get('symbol', 'N/A')}: "
                      f"Qtd: {position.get('amount', 0):,.4f}, "
                      f"P/L: ${position.get('pnl', 0):,.2f}")
        
    except Exception as e:
        print(f"❌ Erro ao obter resumo da carteira: {e}")
        raise

async def main_async(args):
    """Função principal assíncrona"""
    try:
        if args.backtest:
            await backtest_strategy(args.symbols, args.days)
        elif args.portfolio:
            await show_portfolio_summary()
        else:
            await start_trading(args.symbols, args.test, args.max_positions)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="IA GAIN - Automated Trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_automated_trading.py                    # Iniciar trading em modo teste
  python run_automated_trading.py --real            # Iniciar trading em modo real
  python run_automated_trading.py --symbols BTC/USDT,ETH/USDT  # Trading em símbolos específicos
  python run_automated_trading.py --backtest        # Executar backtest
  python run_automated_trading.py --portfolio       # Mostrar resumo da carteira
  python run_automated_trading.py --max-positions 3  # Limitar a 3 posições simultâneas
        """
    )
    
    parser.add_argument('--real',
                       action='store_true',
                       help='Executar em modo real (padrão: teste)')
    parser.add_argument('--test',
                       action='store_true',
                       default=True,
                       help='Executar em modo teste (padrão)')
    parser.add_argument('--symbols', '-s',
                       help='Símbolos para trading (ex: BTC/USDT,ETH/USDT)')
    parser.add_argument('--max-positions',
                       type=int,
                       default=5,
                       help='Máximo de posições simultâneas (padrão: 5)')
    parser.add_argument('--backtest',
                       action='store_true',
                       help='Executar backtest das estratégias')
    parser.add_argument('--portfolio',
                       action='store_true',
                       help='Mostrar resumo da carteira')
    parser.add_argument('--days',
                       type=int,
                       default=30,
                       help='Período do backtest em dias (padrão: 30)')
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar dependências e configuração')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║            IA GAIN - Automated Trading                     ║
║         Trading Automatizado com IA                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar dependências e configuração
    if args.check:
        print("🔍 Verificando dependências...")
        if not check_dependencies():
            sys.exit(1)
        
        print("🔍 Verificando configuração...")
        if not check_config():
            sys.exit(1)
        
        print("✅ Verificação concluída")
        return
    
    # Verificar dependências antes de executar
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar configuração
    if not check_config():
        sys.exit(1)
    
    # Processar argumentos
    if args.symbols:
        args.symbols = [s.strip() for s in args.symbols.split(',')]
    
    if args.real:
        args.test = False
    
    # Executar função principal
    if args.backtest:
        print("📊 Executando backtest...")
    elif args.portfolio:
        print("💼 Consultando carteira...")
    else:
        mode = "REAL" if not args.test else "TESTE"
        print(f"🚀 Iniciando trading automatizado (Modo: {mode})...")
        if args.symbols:
            print(f"Símbolos: {', '.join(args.symbols)}")
        print(f"Máximo de posições: {args.max_positions}")
    
    try:
        asyncio.run(main_async(args))
        print("✅ Operação concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()