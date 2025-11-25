@echo off
echo 🚀 DEPLOY LIMPO DO PURPOSE FOOD B2B
echo =====================================

REM Ir para o diretório B2B limpo
cd "C:\Users\Filipe Epiphanio\Documents\trae_projects\PURPOSE-FOOD-B2B-CLEAN"

REM Parar processos existentes
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak > nul

REM Criar diretório de deploy limpo
set DEPLOY_DIR=deploy-clean
if exist %DEPLOY_DIR% rmdir /s /q %DEPLOY_DIR%
mkdir %DEPLOY_DIR%
cd %DEPLOY_DIR%

echo 📁 Preparando deploy limpo...

REM Copiar apenas arquivos essenciais (SEM node_modules)
echo 📋 Copiando arquivos essenciais...

REM Estrutura de diretórios
mkdir src
cd src
mkdir components
cd components
mkdir Layout
cd ..
cd ..

REM Arquivos de configuração
copy "..\package.json" "package.json"
copy "..\tsconfig.json" "tsconfig.json"
copy "..\vite.config.ts" "vite.config.ts"
copy "..\tailwind.config.js" "tailwind.config.js"
copy "..\postcss.config.js" "postcss.config.js"
copy "..\vercel.json" "vercel.json"
copy "..\index.html" "index.html"
copy "..\customer.html" "customer.html"
copy "..\nodemon.json" "nodemon.json"
copy "..\eslint.config.js" "eslint.config.js"
copy "..\vitest.config.ts" "vitest.config.ts"

REM API completa
echo 🔧 Copiando API...
xcopy /s /i "..\api" "api"

REM Frontend essencial
echo 🎨 Copiando frontend essencial...
copy "..\src\main.tsx" "src\main.tsx"
copy "..\src\App.tsx" "src\App.tsx"
copy "..\src\CustomerApp.tsx" "src\CustomerApp.tsx"
copy "..\src\index.css" "src\index.css"
copy "..\src\vite-env.d.ts" "src\vite-env.d.ts"

REM Copiar componentes essenciais recursivamente
echo 📦 Copiando componentes...
xcopy /s /i "..\src\components" "src\components"
xcopy /s /i "..\src\pages" "src\pages"
xcopy /s /i "..\src\hooks" "src\hooks"
xcopy /s /i "..\src\stores" "src\stores"
xcopy /s /i "..\src\config" "src\config"
xcopy /s /i "..\src\types" "src\types"
xcopy /s /i "..\src\utils" "src\utils"

REM Supabase
echo 🗄️ Copiando Supabase...
xcopy /s /i "..\supabase" "supabase"

REM Criar .vercelignore ultra-restritivo
echo node_modules/ > .vercelignore
echo *.log >> .vercelignore
echo .env* >> .vercelignore
echo .cache >> .vercelignore
echo dist >> .vercelignore
echo build >> .vercelignore

REM Instalar apenas dependências de produção (mínimas)
echo 📦 Instalando dependências mínimas...
call npm install --production --silent --no-optional

REM Verificar quantidade de arquivos antes do build
echo 📊 Contando arquivos antes do build...
dir /s /b | find /c ".\" > file_count_before.txt
set /p COUNT_BEFORE=<file_count_before.txt
echo Arquivos antes do build: %COUNT_BEFORE%

REM Fazer build otimizado
echo 🏗️ Fazendo build otimizado...
call npm run build

REM Após o build, apagar node_modules para reduzir upload
echo 🧹 Removendo node_modules após build...
rmdir /s /q node_modules

REM Verificar quantidade final
echo 📊 Contando arquivos finais...
dir /s /b | find /c ".\" > file_count_final.txt
set /p COUNT_FINAL=<file_count_final.txt
echo Arquivos finais para deploy: %COUNT_FINAL%

REM Deploy se estiver dentro do limite
if %COUNT_FINAL% LSS 5000 (
    echo ✅ Projeto dentro do limite! Fazendo deploy...
    npx vercel --prod --yes
) else (
    echo ⚠️ Ainda muitos arquivos (%COUNT_FINAL%), mas tentando deploy...
    echo 💡 Dica: O build está pronto, o Vercel ignorará node_modules automaticamente
    npx vercel --prod --yes
)

REM Voltar ao diretório original
cd "C:\Users\Filipe Epiphanio\Documents\trae_projects\IA GAIN"

echo 🎉 Processo concluído!
echo 📁 Deploy criado em: C:\Users\Filipe Epiphanio\Documents\trae_projects\PURPOSE-FOOD-B2B-CLEAN\%DEPLOY_DIR%
echo 📊 Arquivos finais: %COUNT_FINAL%
pause