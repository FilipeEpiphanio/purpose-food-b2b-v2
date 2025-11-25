@echo off
REM 🔍 Script de Validação Final - Purpose Food B2B (Windows)
REM Este script verifica se tudo está pronto para deploy

echo 🔍 Validação Final - Purpose Food B2B
echo ======================================

REM Contadores
set ERRORS=0
set WARNINGS=0
set PASSED=0

echo.
echo 🔍 Verificando estrutura do projeto...
echo ======================================

REM Verificar arquivos críticos
if exist "package.json" (
    echo ✅ package.json encontrado
    set /a PASSED+=1
) else (
    echo ❌ package.json não encontrado
    set /a ERRORS+=1
)

if exist "vercel.json" (
    echo ✅ vercel.json encontrado
    set /a PASSED+=1
) else (
    echo ⚠️ vercel.json não encontrado (usando configuração padrão)
    set /a WARNINGS+=1
)

if exist "src" (
    echo ✅ Diretório src encontrado
    set /a PASSED+=1
) else (
    echo ❌ Diretório src não encontrado
    set /a ERRORS+=1
)

if exist "api" (
    echo ✅ Diretório api encontrado
    set /a PASSED+=1
) else (
    echo ❌ Diretório api não encontrado
    set /a ERRORS+=1
)

if exist "supabase" (
    echo ✅ Diretório supabase encontrado
    set /a PASSED+=1
) else (
    echo ⚠️ Diretório supabase não encontrado
    set /a WARNINGS+=1
)

echo.
echo 📦 Verificando dependências...
echo ==================================

if exist "node_modules" (
    echo ✅ node_modules encontrado
    set /a PASSED+=1
    
    REM Verificar dependências críticas
    if exist "node_modules\react\package.json" (
        echo ✅ React instalado
        set /a PASSED+=1
    ) else (
        echo ❌ React não instalado
        set /a ERRORS+=1
    )
    
    if exist "node_modules\@supabase\supabase-js\package.json" (
        echo ✅ Supabase instalado
        set /a PASSED+=1
    ) else (
        echo ❌ Supabase não instalado
        set /a ERRORS+=1
    )
    
    if exist "node_modules\stripe\package.json" (
        echo ✅ Stripe instalado
        set /a PASSED+=1
    ) else (
        echo ❌ Stripe não instalado
        set /a ERRORS+=1
    )
) else (
    echo ❌ node_modules não encontrado - execute npm install
    set /a ERRORS+=1
)

echo.
echo 🔐 Verificando variáveis de ambiente...
echo ==================================

REM Verificar variáveis críticas
if defined SUPABASE_URL (
    echo ✅ SUPABASE_URL configurada
    set /a PASSED+=1
) else (
    echo ❌ SUPABASE_URL não configurada
    set /a ERRORS+=1
)

if defined SUPABASE_ANON_KEY (
    echo ✅ SUPABASE_ANON_KEY configurada
    set /a PASSED+=1
) else (
    echo ❌ SUPABASE_ANON_KEY não configurada
    set /a ERRORS+=1
)

if defined SUPABASE_SERVICE_ROLE_KEY (
    echo ✅ SUPABASE_SERVICE_ROLE_KEY configurada
    set /a PASSED+=1
) else (
    echo ❌ SUPABASE_SERVICE_ROLE_KEY não configurada
    set /a ERRORS+=1
)

if defined STRIPE_SECRET_KEY (
    echo ✅ STRIPE_SECRET_KEY configurada
    set /a PASSED+=1
) else (
    echo ❌ STRIPE_SECRET_KEY não configurada
    set /a ERRORS+=1
)

if defined FRONTEND_URL (
    echo ✅ FRONTEND_URL configurada
    set /a PASSED+=1
) else (
    echo ❌ FRONTEND_URL não configurada
    set /a ERRORS+=1
)

echo.
echo 🛡️ Verificando segurança...
echo ==================================

REM Verificar se há chaves hardcoded (simplificado)
findstr /c:"sk_test_" api\*.js api\*.ts >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ Chaves de teste hardcoded encontradas no código
    set /a ERRORS+=1
) else (
    echo ✅ Nenhuma chave hardcode encontrada
    set /a PASSED+=1
)

echo.
echo 🔨 Verificando build...
echo ==================================

if exist "dist" (
    echo ✅ Diretório dist encontrado
    set /a PASSED+=1
    
    if exist "dist\index.html" (
        echo ✅ index.html encontrado no dist
        set /a PASSED+=1
    ) else (
        echo ❌ index.html não encontrado no dist
        set /a ERRORS+=1
    )
) else (
    echo ⚠️ Diretório dist não encontrado - execute npm run build
    set /a WARNINGS+=1
)

echo.
echo 🗄️ Verificando banco de dados...
echo ==================================

if exist "supabase\migrations\001_create_tables.sql" (
    echo ✅ Migrações encontradas
    set /a PASSED+=1
) else (
    echo ⚠️ Migrações não encontradas
    set /a WARNINGS+=1
)

echo.
echo 📄 Verificando arquivos críticos...
echo ==================================

if exist "src\App.tsx" (
    echo ✅ App.tsx encontrado
    set /a PASSED+=1
) else (
    echo ❌ App.tsx não encontrado
    set /a ERRORS+=1
)

if exist "api\server.ts" (
    echo ✅ server.ts encontrado
    set /a PASSED+=1
) else (
    echo ❌ server.ts não encontrado
    set /a ERRORS+=1
)

if exist "vercel.json" (
    echo ✅ vercel.json encontrado
    set /a PASSED+=1
) else (
    echo ⚠️ vercel.json não encontrado
    set /a WARNINGS+=1
)

echo.
echo 🔧 Verificando scripts de deploy...
echo ==================================

if exist "deploy-b2b.bat" (
    echo ✅ Script de deploy encontrado
    set /a PASSED+=1
) else (
    echo ⚠️ Script de deploy não encontrado
    set /a WARNINGS+=1
)

if exist "setup-env.bat" (
    echo ✅ Script de configuração encontrado
    set /a PASSED+=1
) else (
    echo ⚠️ Script de configuração não encontrado
    set /a WARNINGS+=1
)

echo.
echo 📊 RESUMO FINAL
echo ==================================
echo ✅ Testes Passados: %PASSED%
echo ⚠️  Avisos: %WARNINGS%
echo ❌ Erros: %ERRORS%
echo.

if %ERRORS% equ 0 (
    echo 🎉 Sistema pronto para deploy!
    echo ✅ Todas as verificações críticas passaram
    
    if %WARNINGS% gtr 0 (
        echo.
        echo ⚠️  Atenção:
        echo Há %WARNINGS% avisos que devem ser revisados
        echo mas não impedem o deploy
    )
    
    echo.
    echo 🔧 Próximo passo:
    echo Execute o script de deploy para prosseguir
    exit /b 0
) else (
    echo ❌ Sistema NÃO está pronto para deploy
    echo Por favor, corrija os %ERRORS% erros antes de continuar
    
    echo.
    echo 📋 Ações necessárias:
    echo 1. Configure todas as variáveis de ambiente obrigatórias
    echo 2. Instale as dependências: npm install
    echo 3. Execute o build: npm run build
    echo 4. Configure as integrações necessárias
    
    exit /b 1
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul