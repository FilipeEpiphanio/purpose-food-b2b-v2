#!/usr/bin/env python3
"""
IA GAIN - Unified Launcher
Launcher unificado para todos os módulos do sistema IA GAIN
"""

import os
import sys
import subprocess
import argparse
import json
import platform
import webbrowser
from pathlib import Path
from datetime import datetime

def setup_environment():
    """Configurar ambiente e paths"""
    # Adicionar o diretório src ao path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))

def clear_screen():
    """Limpar tela do console"""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def display_banner():
    """Exibir banner do sistema"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██╗ █████╗ ████████╗ █████╗ ██████╗ ██╗  ██╗    ██████╗ ███████╗██╗    ║
║    ██║██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██║ ██╔╝    ██╔══██╗██╔════╝██║    ║
║    ██║███████║   ██║   ███████║█████╔╝█████╔╝     ██████╔╝█████╗  ██║    ║
║    ██║██╔══██║   ██║   ██╔══██║██╔══██╗██╔═██╗     ██╔══██╗██╔══╝  ██║    ║
║    ██║██║  ██║   ██║   ██║  ██║██║  ██║██║  ██╗    ██║  ██║███████╗╚█████╗╗
║    ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝ ╚════╝╝
║                                                                              ║
║         Sistema Inteligente de Trading com Machine Learning                  ║
║                    Versão 1.0 - Python 3.11                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"🕐 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💻 Sistema Operacional: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")
    print("=" * 80)

def check_python_version():
    """Verificar versão do Python"""
    current_version = sys.version_info
    required_version = (3, 11)
    
    if current_version < required_version:
        print(f"❌ Python {current_version.major}.{current_version.minor} detectado")
        print(f"⚠️  Recomendado: Python {required_version[0]}.{required_version[1]}+")
        return False
    
    print(f"✅ Python {current_version.major}.{current_version.minor} detectado")
    return True

def check_dependencies():
    """Verificar dependências principais"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'ccxt', 'pandas', 'numpy', 'requests', 'python-dotenv',
        'scikit-learn', 'joblib', 'ta-lib', 'sqlite3', 'sqlalchemy',
        'flask', 'flask-cors', 'flask-socketio', 'tkinter',
        'python-telegram-bot', 'smtplib', 'email-validator',
        'asyncio', 'aiohttp', 'aiofiles', 'matplotlib', 'seaborn',
        'plotly', 'python-dateutil', 'pytz', 'colorama', 'tqdm',
        'cryptography', 'bcrypt', 'psutil', 'pytest'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'ta-lib':
                # Verificar se TA-Lib está disponível
                try:
                    import talib
                except ImportError:
                    # Tentar importar com nome alternativo
                    import ta
            elif package == 'sqlite3':
                # sqlite3 é built-in
                continue
            elif package == 'tkinter':
                import tkinter
            elif package == 'smtplib':
                # smtplib é built-in
                continue
            elif package == 'asyncio':
                # asyncio é built-in
                continue
            elif package == 'python-telegram-bot':
                import telegram
            elif package == 'email-validator':
                import email_validator
            else:
                __import__(package)
                
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {len(missing_packages)}")
        print("📦 Instalando pacotes faltantes...")
        
        # Tentar instalar pacotes faltantes
        for package in missing_packages:
            try:
                print(f"📦 Instalando {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} instalado")
            except subprocess.CalledProcessError:
                print(f"❌ Falha ao instalar {package}")
                return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def check_executables():
    """Verificar se todos os executáveis existem"""
    print("🔍 Verificando executáveis...")
    
    executables = [
        'ia_gain.py',
        'run_data_collector.py',
        'run_crypto_selector.py',
        'run_automated_trading.py',
        'run_ml_model.py',
        'run_alert_system.py',
        'run_config_gui.py',
        'run_risk_manager.py',
        'run_strategy_manager.py',
        'run_exchange_manager.py',
        'run_examples.py'
    ]
    
    missing_executables = []
    
    for executable in executables:
        if not os.path.exists(executable):
            missing_executables.append(executable)
    
    if missing_executables:
        print(f"❌ Executáveis faltando: {missing_executables}")
        return False
    
    print("✅ Todos os executáveis estão presentes")
    return True

def check_config():
    """Verificar configuração"""
    print("🔍 Verificando configuração...")
    
    config_file = 'config.json'
    
    if not os.path.exists(config_file):
        print("⚠️  Arquivo config.json não encontrado")
        print("📄 Criando configuração padrão...")
        
        # Criar configuração padrão
        default_config = {
            "general": {
                "debug": False,
                "log_level": "INFO",
                "timezone": "America/Sao_Paulo"
            },
            "trading": {
                "max_positions": 5,
                "position_size": 0.1,
                "stop_loss": 0.02,
                "take_profit": 0.05,
                "trailing_stop": 0.01
            },
            "api": {
                "binance": {
                    "api_key": "",
                    "api_secret": "",
                    "testnet": True
                },
                "coinbase": {
                    "api_key": "",
                    "api_secret": "",
                    "passphrase": ""
                },
                "coingecko": {
                    "api_key": ""
                }
            },
            "alerts": {
                "telegram": {
                    "enabled": False,
                    "bot_token": "",
                    "chat_id": ""
                },
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": ""
                }
            },
            "ml": {
                "enabled": True,
                "model_update_interval": 24,
                "prediction_confidence": 0.7,
                "features": ["rsi", "macd", "bollinger_bands", "volume"]
            }
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            print("✅ Configuração padrão criada")
        except Exception as e:
            print(f"❌ Erro ao criar configuração: {e}")
            return False
    else:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ Configuração encontrada e válida")
        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
            return False
    
    return True

def create_directories():
    """Criar diretórios necessários"""
    print("📁 Verificando diretórios...")
    
    directories = [
        'logs',
        'data',
        'backups',
        'reports',
        'ml_models',
        'src',
        'src/alerts',
        'src/automated_trading',
        'src/crypto_selector',
        'src/data_collector',
        'src/ml',
        'src/utils'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"📁 Criado: {directory}")
            except Exception as e:
                print(f"❌ Erro ao criar {directory}: {e}")
                return False
    
    print("✅ Todos os diretórios estão presentes")
    return True

def run_system_check():
    """Executar verificação completa do sistema"""
    print("🔧 Executando verificação do sistema...")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependências", check_dependencies),
        ("Executáveis", check_executables),
        ("Configuração", check_config),
        ("Diretórios", create_directories)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}...")
        if not check_func():
            print(f"❌ {check_name} falhou")
            all_passed = False
        else:
            print(f"✅ {check_name} OK")
    
    return all_passed

def run_module(module_name, args=None):
    """Executar módulo específico"""
    print(f"🚀 Executando {module_name}...")
    
    modules = {
        'main': 'ia_gain.py',
        'data_collector': 'run_data_collector.py',
        'crypto_selector': 'run_crypto_selector.py',
        'automated_trading': 'run_automated_trading.py',
        'ml_model': 'run_ml_model.py',
        'alert_system': 'run_alert_system.py',
        'config_gui': 'run_config_gui.py',
        'risk_manager': 'run_risk_manager.py',
        'strategy_manager': 'run_strategy_manager.py',
        'exchange_manager': 'run_exchange_manager.py',
        'examples': 'run_examples.py',
        'ai_trading': 'run_ai_trading.py',
        'backtest': 'run_backtest.py',
        'portfolio': 'run_portfolio.py',
        'metatrader_trading': 'run_metatrader_trading.py',
        'copy_trading': 'run_copy_trading.py',
        'momentum_analysis': 'run_momentum_analysis.py',
        'pattern_recognition': 'run_pattern_recognition.py',
        'sentiment_analysis': 'run_sentiment_analysis.py',
        'advanced_analysis': 'run_advanced_analysis.py',
        'ai_trading_dashboard': 'run_ai_trading_dashboard.py'
    }
    
    if module_name not in modules:
        print(f"❌ Módulo desconhecido: {module_name}")
        return False
    
    executable = modules[module_name]
    
    if not os.path.exists(executable):
        print(f"❌ Executável não encontrado: {executable}")
        return False
    
    try:
        cmd = [sys.executable, executable]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {module_name} executado com sucesso")
            return True
        else:
            print(f"❌ Erro ao executar {module_name}")
            if result.stderr:
                print(f"Erro: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar {module_name}: {e}")
        return False

def show_menu():
    """Exibir menu principal"""
    print("\n" + "="*80)
    print("🎯 IA GAIN - MENU PRINCIPAL")
    print("="*80)
    print("1️⃣  Executar Sistema Principal")
    print("2️⃣  Coletor de Dados")
    print("3️⃣  Seletor de Criptomoedas")
    print("4️⃣  Trading Automatizado")
    print("5️⃣  Machine Learning")
    print("6️⃣  Sistema de Alertas")
    print("7️⃣  Configuração GUI")
    print("8️⃣  Gerenciador de Risco")
    print("9️⃣  Gerenciador de Estratégias")
    print("🔟  Gerenciador de Exchanges")
    print("1️⃣1️⃣  Exemplos e Backtesting")
    print("1️⃣2️⃣  Verificar Sistema")
    print("1️⃣3️⃣  Abrir Documentação")
    print("1️⃣4️⃣  🆕 MetaTrader 5 Trading")
    print("1️⃣5️⃣  🆕 Copy Trading")
    print("1️⃣6️⃣  🆕 Análise de Momento")
    print("1️⃣7️⃣  🆕 Reconhecimento de Padrões")
    print("1️⃣8️⃣  🆕 Análise de Sentimento (IA)")
    print("1️⃣9️⃣  🆕 Análise Avançada (IA)")
    print("2️⃣0️⃣  🆕 Dashboard de Trading IA (Web)")
    print("2️⃣1️⃣  Sair")
    print("="*80)

def get_user_choice():
    """Obter escolha do usuário"""
    try:
        choice = input("\n📝 Escolha uma opção (1-14): ").strip()
        return choice
    except KeyboardInterrupt:
        return '14'

def handle_choice(choice):
    """Processar escolha do usuário"""
    if choice == '1':
        print("\n🚀 Iniciando Sistema Principal...")
        run_module('main', ['--gui'])
        
    elif choice == '2':
        print("\n📊 Iniciando Coletor de Dados...")
        symbol = input("Símbolo (ex: BTC/USDT) [pressione Enter para pular]: ").strip()
        args = []
        if symbol:
            args.extend(['--symbol', symbol])
        run_module('data_collector', args)
        
    elif choice == '3':
        print("\n🎯 Iniciando Seletor de Criptomoedas...")
        run_module('crypto_selector')
        
    elif choice == '4':
        print("\n💰 Iniciando Trading Automatizado...")
        print("Modos disponíveis:")
        print("1. Modo Real (⚠️  Cuidado - usa dinheiro real)")
        print("2. Modo Teste (Recomendado)")
        mode = input("Escolha o modo (1-2) [padrão: 2]: ").strip() or '2'
        
        if mode == '1':
            confirm = input("⚠️  Tem certeza que deseja usar dinheiro real? (s/N): ").strip().lower()
            if confirm == 's':
                run_module('automated_trading', ['--real'])
            else:
                print("✅ Usando modo de teste")
                run_module('automated_trading', ['--test'])
        else:
            run_module('automated_trading', ['--test'])
        
    elif choice == '5':
        print("\n🧠 Iniciando Machine Learning...")
        print("Opções disponíveis:")
        print("1. Treinar modelo")
        print("2. Fazer predição")
        print("3. Executar backtest")
        ml_choice = input("Escolha uma opção (1-3): ").strip()
        
        if ml_choice == '1':
            symbol = input("Símbolo (ex: BTC/USDT): ").strip() or 'BTC/USDT'
            run_module('ml_model', ['--train', symbol])
        elif ml_choice == '2':
            symbol = input("Símbolo (ex: BTC/USDT): ").strip() or 'BTC/USDT'
            run_module('ml_model', ['--predict', symbol])
        elif ml_choice == '3':
            symbol = input("Símbolo (ex: BTC/USDT): ").strip() or 'BTC/USDT'
            run_module('ml_model', ['--backtest', symbol])
        else:
            print("❌ Opção inválida")
        
    elif choice == '6':
        print("\n🚨 Iniciando Sistema de Alertas...")
        print("Opções disponíveis:")
        print("1. Iniciar monitoramento")
        print("2. Enviar alerta de teste")
        print("3. Criar alerta de preço")
        alert_choice = input("Escolha uma opção (1-3): ").strip()
        
        if alert_choice == '1':
            run_module('alert_system', ['--start'])
        elif alert_choice == '2':
            run_module('alert_system', ['--test'])
        elif alert_choice == '3':
            symbol = input("Símbolo (ex: BTC/USDT): ").strip() or 'BTC/USDT'
            price = input("Preço alvo: ").strip()
            condition = input("Condição (above/below) [padrão: above]: ").strip() or 'above'
            run_module('alert_system', ['--price', symbol, price, f'--{condition}'])
        else:
            print("❌ Opção inválida")
        
    elif choice == '7':
        print("\n⚙️  Iniciando Configuração GUI...")
        run_module('config_gui')
        
    elif choice == '8':
        print("\n⚠️  Iniciando Gerenciador de Risco...")
        run_module('risk_manager')
        
    elif choice == '9':
        print("\n📈 Iniciando Gerenciador de Estratégias...")
        run_module('strategy_manager')
        
    elif choice == '10':
        print("\n🏦 Iniciando Gerenciador de Exchanges...")
        run_module('exchange_manager')
        
    elif choice == '11':
        print("\n📚 Iniciando Exemplos e Backtesting...")
        run_module('examples')
        
    elif choice == '12':
        print("\n🔧 Verificando Sistema...")
        run_system_check()
        
    elif choice == '13':
        print("\n📖 Abrindo Documentação...")
        try:
            if os.path.exists('README.md'):
                if platform.system() == 'Windows':
                    os.startfile('README.md')
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', 'README.md'])
                else:  # Linux
                    subprocess.run(['xdg-open', 'README.md'])
            else:
                webbrowser.open('https://github.com/seu-usuario/ia-gain')
        except Exception as e:
            print(f"❌ Erro ao abrir documentação: {e}")
        
    elif choice == '14':
        print("\n🚀 Iniciando MetaTrader 5 Trading...")
        run_module('metatrader_trading')
    elif choice == '15':
        print("\n🔄 Iniciando Copy Trading...")
        run_module('copy_trading')
    elif choice == '16':
        print("\n📈 Iniciando Análise de Momento...")
        run_module('momentum_analysis')
    elif choice == '17':
        print("\n🔍 Iniciando Reconhecimento de Padrões...")
        run_module('pattern_recognition')
    elif choice == '18':
        print("\n🧠 Iniciando Análise de Sentimento (IA)...")
        run_module('sentiment_analysis')
    elif choice == '19':
        print("\n🤖 Iniciando Análise Avançada (IA)...")
        run_module('advanced_analysis')
    elif choice == '20':
        print("\n🌐 Iniciando Dashboard de Trading IA (Web)...")
        run_module('ai_trading_dashboard')
    elif choice == '21':
        print("\n👋 Obrigado por usar IA GAIN!")
        return False
        
    else:
        print("❌ Opção inválida. Por favor, escolha entre 1-14.")
    
    return True

def main():
    """Função principal"""
    # Configurar ambiente
    setup_environment()
    
    # Parse argumentos de linha de comando
    parser = argparse.ArgumentParser(
        description="IA GAIN - Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python launcher.py                          # Menu interativo
  python launcher.py --check                  # Verificar sistema
  python launcher.py --module main --args --gui # Executar módulo específico
  python launcher.py --auto                   # Executar modo automático
        """
    )
    
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar sistema e dependências')
    parser.add_argument('--module',
                       choices=['main', 'data_collector', 'crypto_selector', 
                               'automated_trading', 'ml_model', 'alert_system', 'config_gui',
                               'risk_manager', 'strategy_manager', 'exchange_manager', 'examples'],
                       help='Executar módulo específico')
    parser.add_argument('--args',
                       nargs=argparse.REMAINDER,
                       help='Argumentos para o módulo')
    parser.add_argument('--auto',
                       action='store_true',
                       help='Executar modo automático')
    parser.add_argument('--version',
                       action='version',
                       version='IA GAIN 1.0 - Python 3.11')
    
    args = parser.parse_args()
    
    # Limpar tela e exibir banner
    clear_screen()
    display_banner()
    
    try:
        if args.check:
            # Modo de verificação
            run_system_check()
            
        elif args.module:
            # Executar módulo específico
            module_args = args.args if args.args else []
            run_module(args.module, module_args)
            
        elif args.auto:
            # Modo automático
            print("🤖 Iniciando modo automático...")
            if run_system_check():
                print("\n🚀 Executando todos os módulos em sequência...")
                modules = ['data_collector', 'crypto_selector', 'ml_model', 'automated_trading']
                for module in modules:
                    print(f"\n{'='*50}")
                    run_module(module)
            else:
                print("❌ Verificação do sistema falhou")
                
        else:
            # Menu interativo
            while True:
                show_menu()
                choice = get_user_choice()
                if not handle_choice(choice):
                    break
                
                input("\n📝 Pressione Enter para continuar...")
                clear_screen()
                display_banner()
        
        print("\n✅ Operação concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação interrompida pelo usuário")
        print("👋 Obrigado por usar IA GAIN!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()