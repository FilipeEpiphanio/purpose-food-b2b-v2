#!/usr/bin/env python3
"""
IA GAIN - Script de Instalação
Instala todas as dependências necessárias para o projeto
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def print_banner():
    """Exibe banner de instalação"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        IA GAIN - INSTALAÇÃO                               ║
║              Sistema Inteligente de Trading com ML                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verifica versão do Python"""
    print("🔍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("⚠️  Este projeto requer Python 3.11 ou superior")
        print("📥 Por favor, atualize seu Python em: https://www.python.org/downloads/")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def install_package(package, description=""):
    """Instala um pacote específico"""
    if description:
        print(f"📦 Instalando {description}...")
    else:
        print(f"📦 Instalando {package}...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package, "--upgrade"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package} instalado com sucesso")
            return True
        else:
            print(f"❌ Erro ao instalar {package}")
            print(f"Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao instalar {package}: {e}")
        return False

def create_config_file():
    """Cria arquivo de configuração padrão"""
    print("⚙️  Criando arquivo de configuração...")
    
    config = {
        "trading": {
            "default_symbol": "BTC/USDT",
            "timeframe": "1h",
            "risk_percentage": 2.0,
            "max_positions": 5,
            "stop_loss_percentage": 3.0,
            "take_profit_percentage": 6.0,
            "trailing_stop": True,
            "trailing_stop_distance": 2.0
        },
        "risk_management": {
            "max_drawdown": 20.0,
            "position_sizing": "kelly",
            "use_stop_loss": True,
            "use_take_profit": True,
            "emergency_stop": True
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
            "ema_periods": [9, 21, 50, 200]
        },
        "exchanges": {
            "binance": {
                "enabled": True,
                "sandbox": True,
                "api_key": "",
                "api_secret": ""
            },
            "coinbase": {
                "enabled": False,
                "sandbox": True,
                "api_key": "",
                "api_secret": ""
            },
            "kraken": {
                "enabled": False,
                "sandbox": True,
                "api_key": "",
                "api_secret": ""
            },
            "bybit": {
                "enabled": False,
                "sandbox": True,
                "api_key": "",
                "api_secret": ""
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
                "password": "",
                "to_email": ""
            },
            "webhook": {
                "enabled": False,
                "url": ""
            }
        },
        "machine_learning": {
            "enabled": True,
            "model_type": "random_forest",
            "training_days": 90,
            "prediction_threshold": 0.6,
            "retrain_interval": 7,
            "feature_importance": True,
            "cross_validation": True
        },
        "crypto_selector": {
            "min_volume_usd": 1000000,
            "min_market_cap_usd": 50000000,
            "max_selection": 20,
            "include_stablecoins": False,
            "include_meme_coins": False,
            "analysis_depth": "comprehensive"
        },
        "system": {
            "log_level": "INFO",
            "log_to_file": True,
            "max_log_size_mb": 100,
            "backup_count": 5,
            "timezone": "America/Sao_Paulo",
            "language": "pt_BR"
        }
    }
    
    try:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("✅ Arquivo config.json criado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar config.json: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print("📁 Criando diretórios...")
    
    directories = [
        "logs",
        "data",
        "models",
        "backups",
        "reports",
        "temp"
    ]
    
    created = 0
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            created += 1
        except Exception as e:
            print(f"⚠️  Erro ao criar diretório {directory}: {e}")
    
    print(f"✅ {created} diretórios criados")
    return True

def create_env_file():
    """Cria arquivo .env com variáveis de ambiente"""
    print("🌍 Criando arquivo .env...")
    
    env_content = """# IA GAIN - Configurações de Ambiente
# Configure suas chaves de API aqui

# Binance API
BINANCE_API_KEY=sua_chave_aqui
BINANCE_API_SECRET=seu_segredo_aqui

# Coinbase API
COINBASE_API_KEY=sua_chave_aqui
COINBASE_API_SECRET=seu_segredo_aqui

# Kraken API
KRAKEN_API_KEY=sua_chave_aqui
KRAKEN_API_SECRET=seu_segredo_aqui

# Bybit API
BYBIT_API_KEY=sua_chave_aqui
BYBIT_API_SECRET=seu_segredo_aqui

# Telegram Bot (opcional)
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Email (opcional)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_app
EMAIL_TO=destinatario@gmail.com

# Configurações de segurança
RISK_WARNING_ENABLED=true
MAX_POSITION_SIZE_PERCENT=10
EMERGENCY_STOP_ENABLED=true
"""
    
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com sucesso")
        print("⚠️  Lembre-se de configurar suas chaves de API no arquivo .env")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def install_requirements():
    """Instala todos os requisitos"""
    print("\n📥 Instalando dependências do projeto...")
    
    # Dependências principais
    packages = [
        ("ccxt", "CCXT - Biblioteca de exchanges"),
        ("pandas", "Pandas - Análise de dados"),
        ("numpy", "NumPy - Computação numérica"),
        ("requests", "Requests - Requisições HTTP"),
        ("python-dotenv", "Python-dotenv - Gerenciamento de variáveis"),
        ("scikit-learn", "Scikit-learn - Machine Learning"),
        ("joblib", "Joblib - Serialização de modelos"),
        ("python-telegram-bot", "Telegram Bot - Notificações"),
        ("aiohttp", "AioHTTP - Cliente assíncrono"),
        ("matplotlib", "Matplotlib - Gráficos"),
        ("seaborn", "Seaborn - Visualização de dados"),
        ("plotly", "Plotly - Gráficos interativos"),
        ("ta", "TA - Análise técnica"),
        ("yfinance", "YFinance - Dados do Yahoo Finance"),
        ("schedule", "Schedule - Agendamento de tarefas"),
        ("colorama", "Colorama - Cores no terminal"),
        ("rich", "Rich - Interface rica no terminal"),
        ("click", "Click - Interface de linha de comando"),
        ("loguru", "Loguru - Logging avançado"),
        ("email-validator", "Email Validator - Validação de email")
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package, description in packages:
        if install_package(package, description):
            success_count += 1
    
    print(f"\n📊 Resultado da instalação:")
    print(f"✅ {success_count}/{total_count} pacotes instalados com sucesso")
    
    if success_count < total_count:
        print("⚠️  Alguns pacotes podem não ter sido instalados corretamente")
        print("   Você pode tentar instalar manualmente os pacotes faltantes")
    
    return success_count == total_count

def main():
    """Função principal"""
    print_banner()
    
    if not check_python_version():
        return 1
    
    print("\n🚀 Iniciando instalação do IA GAIN...")
    print("⏰ Isso pode levar alguns minutos...")
    print("-" * 60)
    
    # Instalar dependências
    if not install_requirements():
        print("\n❌ Instalação de dependências falhou parcialmente")
        response = input("Deseja continuar mesmo assim? (s/N): ")
        if response.lower() != 's':
            return 1
    
    # Criar arquivos e diretórios
    create_config_file()
    create_env_file()
    create_directories()
    
    print("\n" + "="*60)
    print("🎉 INSTALAÇÃO CONCLUÍDA!")
    print("="*60)
    print("\n📋 Próximos passos:")
    print("1. Configure suas chaves de API no arquivo .env")
    print("2. Ajuste as configurações no arquivo config.json")
    print("3. Execute 'python ia_gain.py --check' para verificar o sistema")
    print("4. Use 'ia_gain.bat' para interface Windows ou 'python launcher.py' para launcher unificado")
    print("\n📖 Documentação:")
    print("   - Leia o README.md para mais informações")
    print("   - Execute 'python ia_gain.py --help' para ver opções")
    print("\n🌐 Suporte:")
    print("   - Verifique os logs em ./logs/")
    print("   - Configure notificações em config.json")
    print("\n⚠️  IMPORTANTE:")
    print("   - Sempre teste no modo sandbox antes de usar dinheiro real")
    print("   - Configure adequadamente o gerenciamento de risco")
    print("   - Monitore sempre suas operações")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())