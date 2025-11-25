#!/usr/bin/env python3
"""
IA GAIN - Sistema de Trading com IA
Script principal para execução fácil
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Verificar versão do Python"""
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8 ou superior é necessário")
        print(f"Versão atual: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def check_dependencies():
    """Verificar se as dependências estão instaladas"""
    required_packages = [
        'ccxt', 'pandas', 'numpy', 'sklearn', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Instalando dependências...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependências instaladas com sucesso")
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            print("Por favor, execute: pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ Todas as dependências estão instaladas")

def run_main():
    """Executar o sistema principal"""
    try:
        # Adicionar o diretório src ao path
        src_path = Path(__file__).parent / 'src'
        sys.path.insert(0, str(src_path))
        
        # Importar e executar o main
        from main import main
        main()
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("Verifique se todos os arquivos estão presentes no diretório src/")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao executar o sistema: {e}")
        sys.exit(1)

def run_gui():
    """Executar interface gráfica"""
    try:
        # Adicionar o diretório src ao path
        src_path = Path(__file__).parent / 'src'
        sys.path.insert(0, str(src_path))
        
        # Importar e executar a interface gráfica
        from interface.config_gui import ConfigInterface
        
        # Criar e executar a interface
        app = ConfigInterface()
        app.run()
        
    except ImportError as e:
        print(f"❌ Erro ao importar interface gráfica: {e}")
        print("Verifique se o arquivo config_gui.py está presente")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao executar interface gráfica: {e}")
        sys.exit(1)

def run_data_collector():
    """Executar coletor de dados"""
    try:
        # Adicionar o diretório src ao path
        src_path = Path(__file__).parent / 'src'
        sys.path.insert(0, str(src_path))
        
        # Importar e executar o data collector
        from data.data_collector import main
        main()
        
    except ImportError as e:
        print(f"❌ Erro ao importar data collector: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao executar data collector: {e}")
        sys.exit(1)

def create_config():
    """Criar arquivo de configuração padrão"""
    config_content = {
        "trading": {
            "enabled": True,
            "max_positions": 5,
            "risk_per_trade": 2.0,
            "min_balance": 100.0,
            "default_leverage": 1,
            "test_mode": True
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
        },
        "alerts": {
            "enabled": True,
            "email_enabled": False,
            "email_address": "",
            "email_password": "",
            "telegram_enabled": False,
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            "discord_enabled": False,
            "discord_webhook": ""
        },
        "machine_learning": {
            "enabled": True,
            "model_update_interval": 24,
            "prediction_threshold": 0.7,
            "backtest_period": 30
        },
        "crypto_selector": {
            "enabled": True,
            "top_coins_limit": 20,
            "min_volume": 1000000,
            "min_market_cap": 10000000
        },
        "system": {
            "log_level": "INFO",
            "data_retention_days": 30,
            "backup_enabled": True,
            "backup_interval": 24,
            "max_workers": 4
        }
    }
    
    config_file = "config.json"
    
    if os.path.exists(config_file):
        response = input("Arquivo config.json já existe. Sobrescrever? (s/N): ")
        if response.lower() != 's':
            print("✅ Configuração não alterada")
            return
    
    try:
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_content, f, indent=2, ensure_ascii=False)
        print(f"✅ Arquivo {config_file} criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar config.json: {e}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="IA GAIN - Sistema de Trading com Inteligência Artificial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python ia_gain.py              # Executar o sistema principal
  python ia_gain.py --gui        # Abrir interface gráfica
  python ia_gain.py --config     # Criar configuração padrão
  python ia_gain.py --data       # Executar coletor de dados
  python ia_gain.py --check      # Verificar dependências
        """
    )
    
    parser.add_argument('--gui', action='store_true', help='Abrir interface gráfica')
    parser.add_argument('--config', action='store_true', help='Criar configuração padrão')
    parser.add_argument('--data', action='store_true', help='Executar coletor de dados')
    parser.add_argument('--check', action='store_true', help='Verificar dependências')
    parser.add_argument('--version', action='version', version='IA GAIN v1.0.0')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    IA GAIN - v1.0.0                        ║
║         Sistema de Trading com Inteligência Artificial     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar Python
    check_python_version()
    
    # Executar comando solicitado
    if args.check:
        print("🔍 Verificando dependências...")
        check_dependencies()
        print("✅ Verificação concluída")
        
    elif args.config:
        print("⚙️  Criando configuração padrão...")
        create_config()
        
    elif args.gui:
        print("🖥️  Iniciando interface gráfica...")
        run_gui()
        
    elif args.data:
        print("📊 Executando coletor de dados...")
        run_data_collector()
        
    else:
        print("🚀 Iniciando IA GAIN...")
        print("Verificando dependências...")
        check_dependencies()
        print("\n⚠️  Importante:")
        print("- Certifique-se de configurar suas APIs antes de começar")
        print("- Use --config para criar um arquivo de configuração")
        print("- Use --gui para interface gráfica")
        print("\nPressione Enter para continuar ou Ctrl+C para cancelar...")
        
        try:
            input()
            run_main()
        except KeyboardInterrupt:
            print("\n❌ Operação cancelada pelo usuário")
            sys.exit(0)

if __name__ == "__main__":
    main()