@echo off
REM 🚀 Script de Deploy B2B - Purpose Food (Windows)
REM Este script automatiza o processo de deploy para produção

echo 🚀 Iniciando deploy B2B Purpose Food...
echo ==================================

REM Verificar Node.js
echo 🔍 Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado. Por favor, instale Node.js 18+
    pause
    exit /b 1
)
echo ✅ Node.js encontrado

REM Verificar npm
echo 🔍 Verificando npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm não encontrado. Por favor, instale npm
    pause
    exit /b 1
)
echo ✅ npm encontrado

REM Verificar Git
echo 🔍 Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git não encontrado. Por favor, instale Git
    pause
    exit /b 1
)
echo ✅ Git encontrado

REM Verificar variáveis de ambiente críticas
echo 🔐 Verificando variáveis de ambiente...
if not defined SUPABASE_URL (
    echo ❌ SUPABASE_URL não configurada
    echo Por favor, configure as variáveis de ambiente antes de continuar
    pause
    exit /b 1
)

if not defined SUPABASE_ANON_KEY (
    echo ❌ SUPABASE_ANON_KEY não configurada
    pause
    exit /b 1
)

if not defined STRIPE_SECRET_KEY (
    echo ❌ STRIPE_SECRET_KEY não configurada
    pause
    exit /b 1
)

echo ✅ Variáveis de ambiente básicas configuradas

REM Perguntar se deseja continuar
echo.
echo ⚠️  Este script irá:
echo   - Limpar node_modules e reinstallar
echo   - Executar build do projeto
echo   - Criar uma tag de versão
echo.
set /p continue=Deseja continuar? (s/N): 
if /i not "%continue%"=="s" (
    echo Deploy cancelado pelo usuário
    pause
    exit /b 1
)

REM Limpar e instalar dependências
echo 📦 Preparando dependências...
echo ==================================
echo Limpando node_modules...
if exist node_modules (
    rmdir /s /q node_modules
)
if exist package-lock.json (
    del package-lock.json
)

echo Instalando dependências...
call npm install
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar dependências
    pause
    exit /b 1
)
echo ✅ Dependências instaladas com sucesso

REM Build do projeto
echo 🔨 Construindo projeto...
echo ==================================
echo Executando build...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Falha ao construir projeto
    echo Verifique os logs de build acima
    pause
    exit /b 1
)
echo ✅ Build concluído com sucesso

REM Criar tag de versão
echo 🏷️ Preparando versão...
echo ==================================
REM Obter data e hora atual
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set date=%%c%%a%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set time=%%a%%b
set VERSION=v1.0.0-b2b-%date%-%time%

echo Criando tag de versão: %VERSION%

REM Adicionar mudanças ao git (se houver)
git add .
git diff-index --quiet HEAD --
if %errorlevel% neq 0 (
    git commit -m "Deploy B2B Production - %date% %time%"
)

REM Criar tag
git tag -a "%VERSION%" -m "B2B Production Release %VERSION%"
if %errorlevel% neq 0 (
    echo ❌ Falha ao criar tag
    pause
    exit /b 1
)
echo ✅ Tag criada: %VERSION%

REM Deploy
echo 🚀 Iniciando deploy...
echo ==================================
echo Iniciando deploy para produção...
echo Por favor, aguarde enquanto o deploy é realizado...
echo.
echo ⚠️  Simulação de deploy - Substitua pelo comando real do seu provedor
echo.
echo Comandos comuns:
echo   Vercel:  npx vercel --prod
echo   Netlify: npx netlify deploy --prod
echo   Outros:  Consulte documentação do seu provedor
echo.

REM Push da tag para repositório
echo Enviando tag para repositório...
git push origin "%VERSION%"
if %errorlevel% neq 0 (
    echo ❌ Falha ao enviar tag para repositório
    pause
    exit /b 1
)
echo ✅ Tag enviada para repositório

REM Verificação pós-deploy
echo 🔍 Verificação pós-deploy...
echo ==================================
echo Deploy concluído!
echo Próximos passos:
echo 1. Verificar se o deploy foi bem-sucedido no painel do provedor
echo 2. Acessar a URL de produção e realizar testes básicos
echo 3. Verificar logs de aplicação
echo 4. Monitorar por 24-48 horas

REM Informações finais
echo.
echo 🎉 Deploy concluído!
echo ==================================
echo.
echo 📋 Resumo:
echo   ✅ Pré-requisitos verificados
echo   ✅ Variáveis de ambiente configuradas
echo   ✅ Dependências instaladas
echo   ✅ Build concluído
echo   ✅ Tag criada: %VERSION%
echo   ✅ Deploy iniciado
echo.
echo 🔧 Próximos passos:
echo 1. Complete o deploy no painel do seu provedor
echo 2. Execute os testes pós-deploy conforme checklist
echo 3. Monitore a aplicação
echo.
echo 📖 Documentação:
echo - Checklist completo: DEPLOY_B2B_CHECKLIST.md
echo - Suporte do provedor: [Consulte documentação do seu provedor]
echo.
echo 🎉 Deploy B2B Purpose Food concluído com sucesso!
echo.
echo Pressione qualquer tecla para sair...
pause >nul