@echo off
echo ========================================
echo IA GAIN - Installation Script
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python não está instalado ou não está no PATH
    echo Por favor, instale Python 3.8 ou superior
    pause
    exit /b 1
)

echo Python encontrado:
python --version
echo.

REM Verificar se pip está instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip não está instalado
    pause
    exit /b 1
)

echo Pip encontrado:
pip --version
echo.

REM Criar ambiente virtual
echo Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Falha ao criar ambiente virtual
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Falha ao ativar ambiente virtual
    pause
    exit /b 1
)

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências
echo Instalando dependências...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Falha ao instalar algumas dependências
    echo Continuando mesmo assim...
)

REM Criar diretórios necessários
echo Criando diretórios...
mkdir logs 2>nul
mkdir data 2>nul
mkdir backups 2>nul
mkdir reports 2>nul

REM Criar arquivo de configuração padrão se não existir
if not exist "config.json" (
    echo Criando arquivo de configuração padrão...
    python -c "import json; config = {'trading': {'enabled': True, 'max_positions': 5, 'risk_per_trade': 2.0, 'min_balance': 100.0}, 'risk_management': {'stop_loss': 5.0, 'take_profit': 10.0, 'max_drawdown': 20.0}, 'technical_analysis': {'rsi_period': 14, 'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9, 'bollinger_period': 20, 'bollinger_std': 2}, 'alerts': {'enabled': True, 'email_enabled': False, 'telegram_enabled': False, 'discord_enabled': False}, 'system': {'log_level': 'INFO', 'data_retention_days': 30, 'backup_enabled': True}}; json.dump(config, open('config.json', 'w'), indent=2)"
)

echo.
echo ========================================
echo Instalação concluída!
echo ========================================
echo.
echo Para usar o IA GAIN:
echo 1. Ative o ambiente virtual: venv\Scripts\activate.bat
echo 2. Execute: python src\main.py
echo 3. Ou use a interface gráfica: python src\interface\config_gui.py
echo.
echo Arquivos importantes:
echo - config.json: Configurações do sistema
echo - requirements.txt: Dependências
echo - src\main.py: Arquivo principal
echo.
pause