@echo off
echo 🚀 DEPLOY ULTRA-OTIMIZADO PURPOSE FOOD B2B
echo ========================================

REM Parar processos existentes
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak > nul

REM Criar diretório de build limpo
set BUILD_DIR=build-purified
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%
mkdir %BUILD_DIR%

echo 📁 Preparando arquivos essenciais...

REM Copiar estrutura mínima necessária
cd %BUILD_DIR%

REM Criar estrutura de diretórios essenciais
mkdir src
cd src
mkdir components
cd components
mkdir Dashboard
cd ..
cd ..

REM Copiar apenas arquivos CRÍTICOS do frontend (máximo 200 arquivos)
echo 📋 Copiando arquivos frontend essenciais...

REM Componentes principais
copy "..\src\main.tsx" "src\main.tsx"
copy "..\src\App.tsx" "src\App.tsx"
copy "..\src\index.css" "src\index.css"
copy "..\src\vite-env.d.ts" "src\vite-env.d.ts"

REM Componentes essenciais
copy "..\src\components\Layout\Layout.tsx" "src\components\Layout\Layout.tsx"
copy "..\src\components\Layout\Header.tsx" "src\components\Layout\Header.tsx"
copy "..\src\components\Layout\Sidebar.tsx" "src\components\Layout\Sidebar.tsx"

copy "..\src\components\ui\ProductFormModal.tsx" "src\components\ui\ProductFormModal.tsx"
copy "..\src\components\ui\OrderFormModal.tsx" "src\components\ui\OrderFormModal.tsx"
copy "..\src\components\ui\TransactionFormModal.tsx" "src\components\ui\TransactionFormModal.tsx"

copy "..\src\components\Dashboard\UpcomingEventsWidget.tsx" "src\components\Dashboard\UpcomingEventsWidget.tsx"

REM Páginas principais
copy "..\src\pages\Dashboard.tsx" "src\pages\Dashboard.tsx"
copy "..\src\pages\Products.tsx" "src\pages\Products.tsx"
copy "..\src\pages\Orders.tsx" "src\pages\Orders.tsx"
copy "..\src\pages\Calendar.tsx" "src\pages\Calendar.tsx"
copy "..\src\pages\Financial.tsx" "src\pages\Financial.tsx"
copy "..\src\pages\EventForm.tsx" "src\pages\EventForm.tsx"
copy "..\src\pages\Login.tsx" "src\pages\Login.tsx"

REM Hooks e stores
copy "..\src\hooks\usePreventLogout.ts" "src\hooks\usePreventLogout.ts"
copy "..\src\stores\authStore.ts" "src\stores\authStore.ts"

REM Configurações
copy "..\src\config\supabase.config.ts" "src\config\supabase.config.ts"

REM API completa (essencial para funcionamento)
echo 🔧 Copiando API completa...
mkdir api
cd api
mkdir routes
cd ..
xcopy /s /i "..\api" "api"

REM Arquivos de configuração essenciais
echo ⚙️ Copiando configurações...
copy "..\package-optimized.json" "package.json"
copy "..\tsconfig.json" "tsconfig.json"
copy "..\vite.config.ts" "vite.config.ts"
copy "..\tailwind.config.js" "tailwind.config.js"
copy "..\postcss.config.js" "postcss.config.js"
copy "..\vercel-optimized.json" "vercel.json"
copy "..\index.html" "index.html"

REM Criar .vercelignore ultra-restritivo
echo node_modules/ > .vercelignore
echo *.py >> .vercelignore
echo *.log >> .vercelignore
echo .env* >> .vercelignore

REM Instalar dependências mínimas
echo 📦 Instalando dependências mínimas...
npm install --production=false --silent --no-optional

REM Build otimizado
echo 🏗️ Fazendo build ultra-otimizado...
npm run build

REM Contar arquivos para verificar
echo 📊 Contando arquivos do projeto...
dir /s /b | find /c ".\" > file_count.txt
set /p FILE_COUNT=<file_count.txt
echo Total de arquivos: %FILE_COUNT%

REM Deploy se tiver menos de 5000 arquivos
if %FILE_COUNT% LSS 5000 (
    echo ✅ Projeto dentro do limite! Fazendo deploy...
    npx vercel --prod --yes
) else (
    echo ❌ Ainda muitos arquivos! Reduzindo mais...
    REM Apagar mais arquivos não-críticos
    del /s /q "src\*.py" 2>nul
    del /s /q "api\*.py" 2>nul
    del /s /q "*.log" 2>nul
    del /s /q "*.md" 2>nul
    
    echo 🔄 Tentando deploy novamente...
    npx vercel --prod --yes
)

REM Voltar e limpar
cd ..
echo 🧹 Limpando...

REM Opcional: manter build para debug
choice /C SN /M "Deseja manter o diretório de build para análise?"
if %errorlevel%==1 (
    echo ✅ Build mantido em %BUILD_DIR%
) else (
    rmdir /s /q %BUILD_DIR%
    echo 🗑️ Build removido
)

echo 🎉 Processo concluído!
pause