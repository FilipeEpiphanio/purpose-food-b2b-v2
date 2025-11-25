@echo off
REM 📝 Script de Configuração de Ambiente - Purpose Food B2B (Windows)
REM Este script ajuda a configurar as variáveis de ambiente para deploy

echo 📝 Configurador de Ambiente - Purpose Food B2B
echo ==================================

echo Este script irá ajudá-lo a configurar as variáveis de ambiente necessárias.
echo.

REM Função para solicitar input seguro
:get_input
set "input="
set "prompt=%~1"
set "is_sensitive=%~2"

:prompt_loop
if "%is_sensitive%"=="true" (
    set /p "input=%prompt%: " <nul
    REM Usar PowerShell para input seguro
    for /f "usebackq delims=" %%i in (`powershell -command "$input = Read-Host -AsSecureString; $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($input); [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr); [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)" 2^>nul`) do set "input=%%i"
) else (
    set /p "input=%prompt%: "
)

if "%input%"=="" (
    echo ⚠️ Este campo é obrigatório!
    goto prompt_loop
)
exit /b 0

REM Obter informações do usuário
echo 🔐 Configuração Supabase:
echo ==================================
call :get_input "URL do Supabase (ex: https://sua-url.supabase.co)" "false"
set SUPABASE_URL=%input%

call :get_input "Supabase Anon Key" "true"
set SUPABASE_ANON_KEY=%input%

call :get_input "Supabase Service Role Key" "true"
set SUPABASE_SERVICE_ROLE_KEY=%input%

echo.
echo 💳 Configuração Stripe:
echo ==================================
call :get_input "Stripe Secret Key (live)" "true"
set STRIPE_SECRET_KEY=%input%

call :get_input "Stripe Publishable Key (live)" "false"
set STRIPE_PUBLISHABLE_KEY=%input%

echo.
echo 🌐 Configuração Frontend:
echo ==================================
call :get_input "URL do frontend em produção (ex: https://app.purposefood.com)" "false"
set FRONTEND_URL=%input%

echo.
echo 📅 Google Calendar Integration (opcional):
set /p configure_google=Deseja configurar Google Calendar? (s/n): 
if /i "%configure_google%"=="s" (
    call :get_input "Google Client ID" "false"
    set GOOGLE_CLIENT_ID=%input%
    
    call :get_input "Google Client Secret" "true"
    set GOOGLE_CLIENT_SECRET=%input%
    
    set GOOGLE_REDIRECT_URI=%FRONTEND_URL%/api/calendar/auth/callback
)

REM Criar arquivo de configuração
echo.
echo Criando arquivo de configuracao...
echo ==================================

REM Criar arquivo batch para configurar variáveis
(
echo @echo off
echo REM Configuracao de Ambiente - Purpose Food B2B
echo REM Execute este script antes de rodar o deploy
echo.
echo REM Supabase Configuration
echo set SUPABASE_URL=%SUPABASE_URL%
echo set SUPABASE_ANON_KEY=%SUPABASE_ANON_KEY%
echo set SUPABASE_SERVICE_ROLE_KEY=%SUPABASE_SERVICE_ROLE_KEY%
echo.
echo REM Stripe Configuration  
echo set STRIPE_SECRET_KEY=%STRIPE_SECRET_KEY%
echo set STRIPE_PUBLISHABLE_KEY=%STRIPE_PUBLISHABLE_KEY%
echo.
echo REM Frontend Configuration
echo set FRONTEND_URL=%FRONTEND_URL%
echo set VITE_SUPABASE_URL=%SUPABASE_URL%
echo set VITE_SUPABASE_ANON_KEY=%SUPABASE_ANON_KEY%
echo.
echo REM Google Calendar (opcional)
) > configure-env.bat

if /i "%configure_google%"=="s" (
    (
    echo set GOOGLE_CLIENT_ID=%GOOGLE_CLIENT_ID%
    echo set GOOGLE_CLIENT_SECRET=%GOOGLE_CLIENT_SECRET%
    echo set GOOGLE_REDIRECT_URI=%GOOGLE_REDIRECT_URI%
    ) >> configure-env.bat
)

echo.
echo ✅ Arquivo configure-env.bat criado com sucesso!
echo.

REM Criar arquivo .env.production
echo # Environment Variables - Purpose Food B2B Production > .env.production
echo # Supabase Configuration >> .env.production
echo SUPABASE_URL=%SUPABASE_URL% >> .env.production
echo SUPABASE_ANON_KEY=%SUPABASE_ANON_KEY% >> .env.production
echo SUPABASE_SERVICE_ROLE_KEY=%SUPABASE_SERVICE_ROLE_KEY% >> .env.production
echo. >> .env.production
echo # Stripe Configuration >> .env.production
echo STRIPE_SECRET_KEY=%STRIPE_SECRET_KEY% >> .env.production
echo STRIPE_PUBLISHABLE_KEY=%STRIPE_PUBLISHABLE_KEY% >> .env.production
echo. >> .env.production
echo # Frontend Configuration >> .env.production
echo FRONTEND_URL=%FRONTEND_URL% >> .env.production
echo VITE_SUPABASE_URL=%SUPABASE_URL% >> .env.production
echo VITE_SUPABASE_ANON_KEY=%SUPABASE_ANON_KEY% >> .env.production

if /i "%configure_google%"=="s" (
echo. >> .env.production
echo # Google Calendar Configuration >> .env.production
echo GOOGLE_CLIENT_ID=%GOOGLE_CLIENT_ID% >> .env.production
echo GOOGLE_CLIENT_SECRET=%GOOGLE_CLIENT_SECRET% >> .env.production
echo GOOGLE_REDIRECT_URI=%GOOGLE_REDIRECT_URI% >> .env.production
)

echo ✅ Arquivo .env.production criado com sucesso!
echo.

REM Instruções para provedores
echo 📋 Instrucoes para Configuracao em Provedores:
echo ==================================
echo.
echo 🔧 Para usar estas configuracoes:
echo 1. Execute 'configure-env.bat' antes do deploy
echo 2. Ou configure manualmente no painel do seu provedor
echo 3. Copie as variaveis do arquivo .env.production
echo.
echo 🔧 Vercel:
echo 1. Acesse: https://vercel.com/dashboard
echo 2. Selecione seu projeto
echo 3. Va em Settings -^> Environment Variables
echo 4. Adicione as variaveis uma por uma
echo.
echo 🔧 Netlify:
echo 1. Acesse: https://app.netlify.com
echo 2. Selecione seu projeto
echo 3. Va em Site settings -^> Environment variables
echo 4. Clique em 'Add a variable' para cada uma
echo.
echo ⚠️  IMPORTANTE:
echo - NUNCA commite arquivos com senhas
echo - Adicione .env.production ao .gitignore
echo - Mantenha backups seguros das chaves
echo - Use chaves diferentes para desenvolvimento e producao
echo.
echo 🎉 Configuracao concluida!
echo Proximo passo: Execute deploy-b2b.bat para fazer o deploy
echo.
echo Pressione qualquer tecla para sair...
pause >nul