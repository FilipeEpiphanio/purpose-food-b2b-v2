#!/usr/bin/env python3
"""
IA GAIN - Strategy Manager Executor
Script executável para gerenciamento e backtest de estratégias de trading
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Optional

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
            logging.FileHandler('strategy_manager.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Verificar dependências necessárias"""
    required_packages = [
        'pandas', 'numpy', 'python-dotenv', 'ccxt'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install pandas numpy python-dotenv ccxt")
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
        
        if 'strategies' not in config:
            print("⚠️  Atenção: Configuração de estratégias não encontrada")
            print("Use a interface gráfica para configurar as estratégias")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

async def list_available_strategies(strategy_manager):
    """Listar estratégias disponíveis"""
    try:
        strategies = strategy_manager.get_available_strategies()
        
        print("\n📋 Estratégias Disponíveis:")
        print("=" * 50)
        
        for strategy_name, strategy_info in strategies.items():
            print(f"\n🎯 {strategy_name}:")
            print(f"   Descrição: {strategy_info.get('description', 'N/A')}")
            print(f"   Tipo: {strategy_info.get('type', 'N/A')}")
            print(f"   Ativa: {'✅' if strategy_info.get('enabled', False) else '❌'}")
            print(f"   Parâmetros: {len(strategy_info.get('parameters', {}))}")
        
        return strategies
        
    except Exception as e:
        print(f"❌ Erro ao listar estratégias: {e}")
        return {}

async def backtest_strategy(strategy_manager, strategy_name: str, symbols: List[str], days: int):
    """Executar backtest de uma estratégia"""
    try:
        print(f"\n📈 Backtest da Estratégia: {strategy_name}")
        print(f"📊 Símbolos: {', '.join(symbols)}")
        print(f"📅 Período: {days} dias")
        print("=" * 50)
        
        # Executar backtest
        results = await strategy_manager.backtest_strategy(
            strategy_name=strategy_name,
            symbols=symbols,
            period_days=days
        )
        
        # Exibir resultados
        print(f"\n📊 Resultados do Backtest:")
        print(f"   Total de Trades: {results.get('total_trades', 0)}")
        print(f"   Trades Vencedores: {results.get('winning_trades', 0)}")
        print(f"   Trades Perdedores: {results.get('losing_trades', 0)}")
        print(f"   Taxa de Acerto: {results.get('win_rate', 0):.2f}%")
        print(f"   Retorno Total: {results.get('total_return', 0):.2f}%")
        print(f"   Retorno Médio por Trade: {results.get('avg_return', 0):.2f}%")
        print(f"   Máximo Drawdown: {results.get('max_drawdown', 0):.2f}%")
        print(f"   Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}")
        
        # Análise detalhada por símbolo
        if 'symbol_results' in results:
            print(f"\n📈 Resultados por Símbolo:")
            for symbol, symbol_result in results['symbol_results'].items():
                print(f"   {symbol}:")
                print(f"     Trades: {symbol_result.get('trades', 0)}")
                print(f"     Retorno: {symbol_result.get('return', 0):.2f}%")
                print(f"     Win Rate: {symbol_result.get('win_rate', 0):.2f}%")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no backtest: {e}")
        return {}

async def optimize_strategy(strategy_manager, strategy_name: str, symbols: List[str]):
    """Otimizar parâmetros de uma estratégia"""
    try:
        print(f"\n⚙️  Otimizando Estratégia: {strategy_name}")
        print(f"📊 Símbolos: {', '.join(symbols)}")
        print("=" * 50)
        
        # Executar otimização
        optimization_results = await strategy_manager.optimize_strategy(
            strategy_name=strategy_name,
            symbols=symbols
        )
        
        # Exibir resultados da otimização
        print(f"\n🔧 Parâmetros Otimizados:")
        optimized_params = optimization_results.get('optimized_parameters', {})
        for param, value in optimized_params.items():
            print(f"   {param}: {value}")
        
        print(f"\n📈 Performance Otimizada:")
        print(f"   Retorno: {optimization_results.get('optimized_return', 0):.2f}%")
        print(f"   Win Rate: {optimization_results.get('optimized_win_rate', 0):.2f}%")
        print(f"   Sharpe Ratio: {optimization_results.get('optimized_sharpe', 0):.2f}")
        
        return optimization_results
        
    except Exception as e:
        print(f"❌ Erro na otimização: {e}")
        return {}

async def execute_strategy_live(strategy_manager, strategy_name: str, symbols: List[str], test_mode: bool):
    """Executar estratégia em modo live"""
    try:
        mode = "TESTE" if test_mode else "REAL"
        print(f"\n🚀 Executando Estratégia: {strategy_name} (Modo: {mode})")
        print(f"📊 Símbolos: {', '.join(symbols)}")
        print("=" * 50)
        
        # Configurar modo
        strategy_manager.set_test_mode(test_mode)
        
        # Executar estratégia
        results = await strategy_manager.execute_live_strategy(
            strategy_name=strategy_name,
            symbols=symbols
        )
        
        # Exibir resultados
        print(f"\n📊 Resultados da Execução:")
        print(f"   Trades Executados: {results.get('executed_trades', 0)}")
        print(f"   Trades com Sucesso: {results.get('successful_trades', 0)}")
        print(f"   PnL Total: {results.get('total_pnl', 0):.2f}")
        print(f"   Tempo de Execução: {results.get('execution_time', 0):.2f}s")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        return {}

async def compare_strategies(strategy_manager, strategy_names: List[str], symbols: List[str], days: int):
    """Comparar múltiplas estratégias"""
    try:
        print(f"\n🔍 Comparando Estratégias: {', '.join(strategy_names)}")
        print(f"📊 Símbolos: {', '.join(symbols)}")
        print(f"📅 Período: {days} dias")
        print("=" * 60)
        
        # Executar comparação
        comparison_results = await strategy_manager.compare_strategies(
            strategy_names=strategy_names,
            symbols=symbols,
            period_days=days
        )
        
        # Tabela de comparação
        print(f"\n📊 Tabela Comparativa:")
        print(f"{'Estratégia':<20} {'Trades':<8} {'Win Rate':<10} {'Retorno':<10} {'Sharpe':<8} {'DD':<8}")
        print("-" * 70)
        
        for strategy_name, results in comparison_results.items():
            print(f"{strategy_name:<20} "
                  f"{results.get('total_trades', 0):<8} "
                  f"{results.get('win_rate', 0):<10.1f}% "
                  f"{results.get('total_return', 0):<10.2f}% "
                  f"{results.get('sharpe_ratio', 0):<8.2f} "
                  f"{results.get('max_drawdown', 0):<8.2f}%")
        
        # Melhor estratégia
        best_strategy = max(comparison_results.items(), 
                          key=lambda x: x[1].get('sharpe_ratio', 0))
        print(f"\n🏆 Melhor Estratégia: {best_strategy[0]} (Sharpe: {best_strategy[1].get('sharpe_ratio', 0):.2f})")
        
        return comparison_results
        
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")
        return {}

async def main_async(args):
    """Função principal assíncrona"""
    try:
        # Importar módulos
        from strategies.strategy_manager import StrategyManager
        from utils.config_manager import ConfigManager
        from utils.logger import setup_logger
        
        # Configurar logger
        logger = setup_logger(
            name="strategy_manager",
            log_file="logs/strategy_manager.log",
            level=args.log_level
        )
        
        # Carregar configuração
        config_manager = ConfigManager(args.config)
        config = config_manager.get_config()
        
        # Inicializar Strategy Manager
        strategy_manager = StrategyManager(config.get('strategies', {}))
        
        print(f"\n🎯 IA GAIN - Strategy Manager")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Executar ação baseada nos argumentos
        if args.list:
            await list_available_strategies(strategy_manager)
            
        elif args.backtest:
            if not args.strategy:
                print("❌ Nome da estratégia é obrigatório para backtest")
                return
            
            symbols = args.symbols.split(',') if args.symbols else ['BTC/USDT']
            await backtest_strategy(strategy_manager, args.strategy, symbols, args.days)
            
        elif args.optimize:
            if not args.strategy:
                print("❌ Nome da estratégia é obrigatório para otimização")
                return
            
            symbols = args.symbols.split(',') if args.symbols else ['BTC/USDT']
            await optimize_strategy(strategy_manager, args.strategy, symbols)
            
        elif args.execute:
            if not args.strategy:
                print("❌ Nome da estratégia é obrigatório para execução")
                return
            
            symbols = args.symbols.split(',') if args.symbols else ['BTC/USDT']
            await execute_strategy_live(strategy_manager, args.strategy, symbols, args.test)
            
        elif args.compare:
            if not args.strategies:
                print("❌ Nomes das estratégias são obrigatórios para comparação")
                return
            
            strategy_names = args.strategies.split(',')
            symbols = args.symbols.split(',') if args.symbols else ['BTC/USDT']
            await compare_strategies(strategy_manager, strategy_names, symbols, args.days)
            
        elif args.check:
            # Verificação completa do sistema de estratégias
            print("🔍 Verificando sistema de estratégias...")
            
            # Verificar configurações
            strategies_config = config.get('strategies', {})
            print(f"✅ Configurações de estratégias: {len(strategies_config)} parâmetros")
            
            # Verificar estratégias disponíveis
            available_strategies = strategy_manager.get_available_strategies()
            print(f"✅ Estratégias disponíveis: {len(available_strategies)}")
            
            # Verificar histórico de backtests
            backtest_history = strategy_manager.get_backtest_history(limit=5)
            print(f"✅ Histórico de backtests: {len(backtest_history)} registros")
            
            print("\n✅ Sistema de estratégias verificado com sucesso!")
            
        else:
            # Listar estratégias como padrão
            await list_available_strategies(strategy_manager)
        
        print("\n✅ Operação concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    # Configurar ambiente
    setup_environment()
    
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description='IA GAIN - Strategy Manager - Gerenciamento de Estratégias',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Listar estratégias disponíveis
  python run_strategy_manager.py --list
  
  # Executar backtest de uma estratégia
  python run_strategy_manager.py --backtest --strategy momentum --symbols BTC/USDT,ETH/USDT --days 30
  
  # Otimizar parâmetros de uma estratégia
  python run_strategy_manager.py --optimize --strategy mean_reversion --symbols BTC/USDT
  
  # Executar estratégia em modo live (teste)
  python run_strategy_manager.py --execute --strategy grid --symbols BTC/USDT --test
  
  # Comparar múltiplas estratégias
  python run_strategy_manager.py --compare --strategies momentum,mean_reversion --symbols BTC/USDT --days 60
  
  # Verificar sistema de estratégias
  python run_strategy_manager.py --check
        """
    )
    
    parser.add_argument('--config', '-c',
                       type=str,
                       default=None,
                       help='Caminho do arquivo de configuração')
    
    parser.add_argument('--list', '-l',
                       action='store_true',
                       help='Listar estratégias disponíveis')
    
    parser.add_argument('--backtest', '-b',
                       action='store_true',
                       help='Executar backtest de estratégia')
    
    parser.add_argument('--optimize', '-o',
                       action='store_true',
                       help='Otimizar parâmetros da estratégia')
    
    parser.add_argument('--execute', '-e',
                       action='store_true',
                       help='Executar estratégia em modo live')
    
    parser.add_argument('--compare',
                       action='store_true',
                       help='Comparar múltiplas estratégias')
    
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar sistema de estratégias')
    
    parser.add_argument('--strategy', '-s',
                       type=str,
                       help='Nome da estratégia')
    
    parser.add_argument('--strategies',
                       type=str,
                       help='Nomes das estratégias (separados por vírgula)')
    
    parser.add_argument('--symbols',
                       type=str,
                       help='Símbolos (separados por vírgula)')
    
    parser.add_argument('--days', '-d',
                       type=int,
                       default=30,
                       help='Dias para backtest/comparação (padrão: 30)')
    
    parser.add_argument('--test',
                       action='store_true',
                       help='Executar em modo teste')
    
    parser.add_argument('--log-level',
                       type=str,
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='Nível de log (padrão: INFO)')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║            IA GAIN - Strategy Manager                        ║
║         Gerenciamento de Estratégias de Trading           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar dependências
    print("🔍 Verificando dependências...")
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar configuração
    print("🔍 Verificando configuração...")
    if not check_config():
        sys.exit(1)
    
    # Executar função principal
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