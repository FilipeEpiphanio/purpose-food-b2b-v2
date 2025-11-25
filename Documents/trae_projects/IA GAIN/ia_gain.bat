@echo off
REM IA GAIN - Windows Launcher Script
REM Script para facilitar a execução dos módulos no Windows

title IA GAIN - Sistema Inteligente de Trading

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Por favor, instale Python 3.11+ e tente novamente.
    pause
    exit /b 1
)

REM Configurar ambiente
setlocal enabledelayedexpansion

REM Criar diretório de logs se não existir
if not exist "logs" mkdir logs

REM Função para executar módulo
:execute_module
set module=%1
set args=%2 %3 %4 %5 %6 %7 %8 %9

echo.
echo 🚀 Executando %module%...
echo ⏰ Início: %date% %time%
echo.

python %module% %args%

set result=%errorlevel%

echo.
echo ⏰ Término: %date% %time%

if %result% equ 0 (
    echo ✅ %module% executado com sucesso!
) else (
    echo ❌ Erro ao executar %module% (código: %result%)
)

echo.
echo Pressione qualquer tecla para continuar...
pause >nul
exit /b %result%

REM Menu principal
:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        IA GAIN - MENU PRINCIPAL                           ║
echo ║              Sistema Inteligente de Trading com ML                         ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 1️⃣  Sistema Principal (Interface Gráfica)
echo 2️⃣  Coletor de Dados
echo 3️⃣  Seletor de Criptomoedas
echo 4️⃣  Trading Automatizado
echo 5️⃣  Machine Learning
echo 6️⃣  Sistema de Alertas
echo 7️⃣  Configuração GUI
echo 8️⃣  Verificar Sistema
echo 9️⃣  Launcher Unificado
echo 🔟  Sair
echo.

set /p choice=📝 Escolha uma opção (1-10): 

if "%choice%"=="1" goto main_gui
if "%choice%"=="2" goto data_collector
if "%choice%"=="3" goto crypto_selector
if "%choice%"=="4" goto automated_trading
if "%choice%"=="5" goto ml_model
if "%choice%"=="6" goto alert_system
if "%choice%"=="7" goto config_gui
if "%choice%"=="8" goto system_check
if "%choice%"=="9" goto unified_launcher
if "%choice%"=="10" goto exit

echo ❌ Opção inválida. Por favor, escolha entre 1-10.
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
goto menu

REM Executar módulos
:main_gui
call :execute_module ia_gain.py --gui
goto menu

:data_collector
echo.
echo 📊 Coletor de Dados
echo.
echo Opções:
echo 1. Coletar dados de símbolo específico
echo 2. Coletar top criptomoedas
echo 3. Coletar dados fundamentais
echo 4. Voltar
set /p data_choice=📝 Escolha uma opção (1-4): 

if "%data_choice%"=="1" (
    set /p symbol=💰 Digite o símbolo (ex: BTC/USDT): 
    if "!symbol!"=="" set symbol=BTC/USDT
    call :execute_module run_data_collector.py --symbol !symbol!
) else if "%data_choice%"=="2" (
    call :execute_module run_data_collector.py --top 50
) else if "%data_choice%"=="3" (
    call :execute_module run_data_collector.py --fundamental
) else if "%data_choice%"=="4" (
    goto menu
) else (
    echo ❌ Opção inválida
    pause
)
goto data_collector

:crypto_selector
call :execute_module run_crypto_selector.py
goto menu

:automated_trading
echo.
echo 💰 Trading Automatizado
echo.
echo ⚠️  AVISO: Este módulo pode usar dinheiro real!
echo.
echo Opções:
echo 1. Modo Teste (Recomendado)
echo 2. Modo Real (⚠️  Cuidado)
echo 3. Backtest
echo 4. Voltar
set /p trading_choice=📝 Escolha uma opção (1-4): 

if "%trading_choice%"=="1" (
    call :execute_module run_automated_trading.py --test
) else if "%trading_choice%"=="2" (
    echo ⚠️  Você está prestes a usar dinheiro real!
    echo.
    set /p confirm=Tem certeza? (s/N): 
    if /i "!confirm!"=="s" (
        call :execute_module run_automated_trading.py --real
    ) else (
        echo ✅ Cancelado. Usando modo de teste.
        call :execute_module run_automated_trading.py --test
    )
) else if "%trading_choice%"=="3" (
    set /p days=Quantos dias para backtest (padrão: 30): 
    if "!days!"=="" set days=30
    call :execute_module run_automated_trading.py --backtest --days !days!
) else if "%trading_choice%"=="4" (
    goto menu
) else (
    echo ❌ Opção inválida
    pause
)
goto menu

:ml_model
echo.
echo 🧠 Machine Learning
echo.
echo Opções:
echo 1. Treinar modelo
echo 2. Fazer predição
echo 3. Executar backtest
echo 4. Atualizar todos os modelos
echo 5. Listar modelos
echo 6. Voltar
set /p ml_choice=📝 Escolha uma opção (1-6): 

if "%ml_choice%"=="1" (
    set /p symbol=💰 Digite o símbolo (ex: BTC/USDT) [padrão: BTC/USDT]: 
    if "!symbol!"=="" set symbol=BTC/USDT
    set /p timeframe=Timeframe [padrão: 1h]: 
    if "!timeframe!"=="" set timeframe=1h
    call :execute_module run_ml_model.py --train !symbol! --timeframe !timeframe!
) else if "%ml_choice%"=="2" (
    set /p symbol=💰 Digite o símbolo (ex: BTC/USDT) [padrão: BTC/USDT]: 
    if "!symbol!"=="" set symbol=BTC/USDT
    call :execute_module run_ml_model.py --predict !symbol!
) else if "%ml_choice%"=="3" (
    set /p symbol=💰 Digite o símbolo (ex: BTC/USDT) [padrão: BTC/USDT]: 
    if "!symbol!"=="" set symbol=BTC/USDT
    set /p days=Quantos dias para backtest [padrão: 30]: 
    if "!days!"=="" set days=30
    call :execute_module run_ml_model.py --backtest !symbol! --days !days!
) else if "%ml_choice%"=="4" (
    call :execute_module run_ml_model.py --update-all
) else if "%ml_choice%"=="5" (
    call :execute_module run_ml_model.py --list
) else if "%ml_choice%"=="6" (
    goto menu
) else (
    echo ❌ Opção inválida
    pause
)
goto menu

:alert_system
echo.
echo 🚨 Sistema de Alertas
echo.
echo Opções:
echo 1. Iniciar monitoramento
echo 2. Enviar alerta de teste
echo 3. Criar alerta de preço
echo 4. Listar alertas ativos
echo 5. Enviar relatório diário
echo 6. Voltar
set /p alert_choice=📝 Escolha uma opção (1-6): 

if "%alert_choice%"=="1" (
    call :execute_module run_alert_system.py --start
) else if "%alert_choice%"=="2" (
    call :execute_module run_alert_system.py --test
) else if "%alert_choice%"=="3" (
    set /p symbol=💰 Digite o símbolo (ex: BTC/USDT): 
    if "!symbol!"=="" set symbol=BTC/USDT
    set /p price=💰 Digite o preço alvo: 
    set /p condition=Condição (above/below) [padrão: above]: 
    if "!condition!"=="" set condition=above
    call :execute_module run_alert_system.py --price !symbol! !price! --!condition!
) else if "%alert_choice%"=="4" (
    call :execute_module run_alert_system.py --list
) else if "%alert_choice%"=="5" (
    call :execute_module run_alert_system.py --daily-report
) else if "%alert_choice%"=="6" (
    goto menu
) else (
    echo ❌ Opção inválida
    pause
)
goto menu

:config_gui
call :execute_module run_config_gui.py
goto menu

:system_check
echo.
echo 🔧 Verificação do Sistema
echo.
echo Verificando...
echo.

call :execute_module ia_gain.py --check

echo.
echo Verificação concluída!
pause
goto menu

:unified_launcher
echo.
echo 🚀 Launcher Unificado
echo.
echo Iniciando launcher unificado...
echo.

call :execute_module launcher.py

goto menu

:exit
echo.
echo 👋 Obrigado por usar IA GAIN!
echo.
echo Desenvolvido com ❤️  para a comunidade de trading
echo.
pause
exit /b 0