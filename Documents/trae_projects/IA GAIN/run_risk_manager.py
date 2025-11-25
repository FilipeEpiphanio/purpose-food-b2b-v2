#!/usr/bin/env python3
"""
IA GAIN - Risk Manager Executor
Script executável para gerenciamento de risco e análise de exposição
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
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
            logging.FileHandler('risk_manager.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Verificar dependências necessárias"""
    required_packages = [
        'pandas', 'numpy', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install pandas numpy python-dotenv")
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
        
        if 'risk_management' not in config:
            print("⚠️  Atenção: Configuração de risco não encontrada")
            print("Use a interface gráfica para configurar o gerenciamento de risco")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

async def analyze_portfolio_risk(risk_manager, symbols: List[str] = None):
    """Analisar risco da carteira"""
    try:
        print("📊 Analisando risco da carteira...")
        
        # Análise de exposição total
        exposure = risk_manager.calculate_total_exposure(symbols)
        print(f"💰 Exposição Total: {exposure:.2f}%")
        
        # Análise por símbolo
        if symbols:
            print("\n📈 Risco por Símbolo:")
            for symbol in symbols:
                symbol_risk = risk_manager.get_symbol_risk(symbol)
                print(f"  {symbol}: Risco {symbol_risk:.2f}%")
        
        # Verificar limites de risco
        limits_check = risk_manager.check_risk_limits()
        print(f"\n🛡️  Limites de Risco:")
        print(f"  Máximo por Trade: {limits_check['max_per_trade']:.2f}%")
        print(f"  Exposição Máxima: {limits_check['max_exposure']:.2f}%")
        print(f"  Drawdown Máximo: {limits_check['max_drawdown']:.2f}%")
        
        if limits_check['within_limits']:
            print("✅ Todos os limites de risco respeitados")
        else:
            print("⚠️  ALERTA: Limites de risco excedidos!")
            for violation in limits_check['violations']:
                print(f"  ❌ {violation}")
        
        return exposure
        
    except Exception as e:
        print(f"❌ Erro na análise de risco: {e}")
        return 0

async def monitor_risk_realtime(risk_manager, interval: int = 60):
    """Monitorar risco em tempo real"""
    print(f"🔍 Monitorando risco a cada {interval} segundos...")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        while True:
            # Análise de risco atual
            risk_analysis = risk_manager.analyze_current_risk()
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📊 Análise de Risco:")
            print(f"  Exposição Atual: {risk_analysis.get('current_exposure', 0):.2f}%")
            print(f"  Drawdown: {risk_analysis.get('current_drawdown', 0):.2f}%")
            print(f"  Trades Ativos: {risk_analysis.get('active_trades', 0)}")
            
            # Verificar alertas
            alerts = risk_manager.check_risk_alerts()
            if alerts:
                print("🚨 Alertas de Risco:")
                for alert in alerts:
                    print(f"  ⚠️  {alert}")
            
            await asyncio.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n✅ Monitoramento de risco finalizado")

async def backtest_risk_management(risk_manager, days: int = 30):
    """Backtest do gerenciamento de risco"""
    print(f"📈 Executando backtest de risco ({days} dias)...")
    
    try:
        # Simular cenários históricos
        scenarios = [
            {"name": "Mercado em Alta", "volatility": 0.02, "trend": "up"},
            {"name": "Mercado em Baixa", "volatility": 0.05, "trend": "down"},
            {"name": "Mercado Lateral", "volatility": 0.01, "trend": "sideways"},
            {"name": "Alta Volatilidade", "volatility": 0.08, "trend": "volatile"}
        ]
        
        print("\n📊 Resultados do Backtest:")
        for scenario in scenarios:
            result = risk_manager.simulate_risk_scenario(
                scenario["volatility"],
                scenario["trend"],
                days
            )
            
            print(f"\n  {scenario['name']}:")
            print(f"    Retorno Médio: {result.get('avg_return', 0):.2f}%")
            print(f"    Máximo Drawdown: {result.get('max_drawdown', 0):.2f}%")
            print(f"    Sharpe Ratio: {result.get('sharpe_ratio', 0):.2f}")
            print(f"    Dias com Perda: {result.get('losing_days', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no backtest: {e}")
        return False

async def main_async(args):
    """Função principal assíncrona"""
    try:
        # Importar módulos
        from risk.risk_manager import RiskManager
        from utils.config_manager import ConfigManager
        from utils.logger import setup_logger
        
        # Configurar logger
        logger = setup_logger(
            name="risk_manager",
            log_file="logs/risk_manager.log",
            level=args.log_level
        )
        
        # Carregar configuração
        config_manager = ConfigManager(args.config)
        config = config_manager.get_config()
        
        # Inicializar Risk Manager
        risk_manager = RiskManager(config.get('risk_management', {}))
        
        print(f"\n🛡️  IA GAIN - Risk Manager")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Executar ação baseada nos argumentos
        if args.analyze:
            symbols = args.symbols.split(',') if args.symbols else None
            await analyze_portfolio_risk(risk_manager, symbols)
            
        elif args.monitor:
            await monitor_risk_realtime(risk_manager, args.interval)
            
        elif args.backtest:
            await backtest_risk_management(risk_manager, args.days)
            
        elif args.check:
            # Verificação completa do sistema de risco
            print("🔍 Verificando sistema de risco...")
            
            # Verificar configurações
            risk_config = config.get('risk_management', {})
            print(f"✅ Configurações de risco: {len(risk_config)} parâmetros")
            
            # Verificar limites
            limits = risk_manager.get_risk_limits()
            print(f"✅ Limites configurados: {len(limits)} regras")
            
            # Verificar histórico
            history = risk_manager.get_risk_history(limit=10)
            print(f"✅ Histórico de risco: {len(history)} registros")
            
            print("\n✅ Sistema de risco verificado com sucesso!")
            
        else:
            # Análise padrão
            await analyze_portfolio_risk(risk_manager)
        
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
        description='IA GAIN - Risk Manager - Gerenciamento de Risco',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Analisar risco da carteira
  python run_risk_manager.py --analyze
  
  # Analisar risco para símbolos específicos
  python run_risk_manager.py --analyze --symbols BTC/USDT,ETH/USDT
  
  # Monitorar risco em tempo real
  python run_risk_manager.py --monitor --interval 30
  
  # Executar backtest de risco
  python run_risk_manager.py --backtest --days 60
  
  # Verificar sistema de risco
  python run_risk_manager.py --check
        """
    )
    
    parser.add_argument('--config', '-c',
                       type=str,
                       default=None,
                       help='Caminho do arquivo de configuração')
    
    parser.add_argument('--analyze', '-a',
                       action='store_true',
                       help='Analisar risco da carteira')
    
    parser.add_argument('--monitor', '-m',
                       action='store_true',
                       help='Monitorar risco em tempo real')
    
    parser.add_argument('--backtest', '-b',
                       action='store_true',
                       help='Executar backtest de risco')
    
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar sistema de risco')
    
    parser.add_argument('--symbols', '-s',
                       type=str,
                       help='Símbolos para análise (separados por vírgula)')
    
    parser.add_argument('--interval', '-i',
                       type=int,
                       default=60,
                       help='Intervalo de monitoramento em segundos (padrão: 60)')
    
    parser.add_argument('--days', '-d',
                       type=int,
                       default=30,
                       help='Dias para backtest (padrão: 30)')
    
    parser.add_argument('--log-level',
                       type=str,
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='Nível de log (padrão: INFO)')
    
    parser.add_argument('--test',
                       action='store_true',
                       help='Executar em modo teste')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║            IA GAIN - Risk Manager                          ║
║         Gerenciamento de Risco com IA                    ║
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