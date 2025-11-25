@echo off
echo 🔧 Preparando deploy otimizado do Purpose Food B2B...

REM Parar servidor se estiver rodando
taskkill /F /IM node.exe 2>nul

REM Limpar diretórios desnecessários
echo 🧹 Limpando diretórios grandes...
if exist node_modules rmdir /s /q node_modules
if exist .venv rmdir /s /q .venv  
if exist venv rmdir /s /q venv
if exist __pycache__ rmdir /s /q __pycache__
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist pycdc rmdir /s /q pycdc
if exist pycdc_bin rmdir /s /q pycdc_bin
if exist ea_agressivo rmdir /s /q ea_agressivo
if exist IA-GAIN-export rmdir /s /q IA-GAIN-export
if exist ia_gain rmdir /s /q ia_gain
if exist dist rmdir /s /q dist

REM Criar diretório temporário para build otimizado
mkdir build-optimized
cd build-optimized

REM Copiar apenas arquivos essenciais do frontend
echo 📁 Copiando arquivos essenciais...
xcopy /s /i "..\src" "src"
xcopy /s /i "..\public" "public" 
xcopy /s /i "..\api" "api"
xcopy /s /i "..\supabase" "supabase"
copy "..\package.json" "package.json"
copy "..\package-lock.json" "package-lock.json"
copy "..\vite.config.ts" "vite.config.ts"
copy "..\tsconfig.json" "tsconfig.json"
copy "..\tailwind.config.js" "tailwind.config.js"
copy "..\postcss.config.js" "postcss.config.js"
copy "..\vercel.json" "vercel.json"
copy "..\index.html" "index.html"
copy "..\customer.html" "customer.html"

REM Instalar apenas dependências de produção
echo 📦 Instalando dependências otimizadas...
npm ci --production=false --silent

REM Fazer build otimizado
echo 🏗️ Fazendo build otimizado...
npm run build

REM Deploy para Vercel
echo 🚀 Fazendo deploy otimizado...
npx vercel --prod --yes

REM Voltar ao diretório original
cd ..

REM Limpar diretório temporário
rmdir /s /q build-optimized

echo ✅ Deploy otimizado concluído!
pause