@echo off
echo 🔍 SEGREGANDO PROJETOS: Purpose Food B2B vs Trading
echo =====================================================

REM Criar diretório separado para Purpose Food B2B
set B2B_DIR=C:\Users\Filipe Epiphanio\Documents\trae_projects\PURPOSE-FOOD-B2B-CLEAN
set CURRENT_DIR=C:\Users\Filipe Epiphanio\Documents\trae_projects\IA GAIN

echo 📁 Criando estrutura limpa em: %B2B_DIR%

REM Criar diretório principal
if exist "%B2B_DIR%" rmdir /s /q "%B2B_DIR%"
mkdir "%B2B_DIR%"
cd "%B2B_DIR%"

REM Criar estrutura de diretórios essencial para B2B
echo 📂 Criando estrutura de diretórios...
mkdir src
mkdir src\components
mkdir src\components\Layout
mkdir src\components\ui
mkdir src\components\Dashboard
mkdir src\pages
mkdir src\pages\customer
mkdir src\hooks
mkdir src\stores
mkdir src\config
mkdir src\types
mkdir src\utils
mkdir api
mkdir api\routes
mkdir api\services
mkdir public
mkdir supabase
mkdir supabase\migrations

echo ✅ Estrutura criada!
echo.
echo 📋 Copiando arquivos ESSENCIAIS do Purpose Food B2B...
echo (Apenas arquivos que não são de trading)

REM ARQUIVOS DE CONFIGURAÇÃO ESSENCIAIS
echo 📄 Configurações...
copy "%CURRENT_DIR%\package.json" "package.json"
copy "%CURRENT_DIR%\package-lock.json" "package-lock.json"
copy "%CURRENT_DIR%\tsconfig.json" "tsconfig.json"
copy "%CURRENT_DIR%\vite.config.ts" "vite.config.ts"
copy "%CURRENT_DIR%\tailwind.config.js" "tailwind.config.js"
copy "%CURRENT_DIR%\postcss.config.js" "postcss.config.js"
copy "%CURRENT_DIR%\vercel.json" "vercel.json"
copy "%CURRENT_DIR%\index.html" "index.html"
copy "%CURRENT_DIR%\customer.html" "customer.html"
copy "%CURRENT_DIR%\nodemon.json" "nodemon.json"
copy "%CURRENT_DIR%\eslint.config.js" "eslint.config.js"
copy "%CURRENT_DIR%\vitest.config.ts" "vitest.config.ts"

REM ARQUIVOS DE SUPABASE (ESSENCIAIS)
echo 🗄️ Supabase...
copy "%CURRENT_DIR%\supabase\migrations\20241118_add_missing_columns.sql" "supabase\migrations\20241118_add_missing_columns.sql"
copy "%CURRENT_DIR%\supabase\migrations\001_create_tables.sql" "supabase\migrations\001_create_tables.sql"
copy "%CURRENT_DIR%\supabase\migrations\002_add_product_fields.sql" "supabase\migrations\002_add_product_fields.sql"
copy "%CURRENT_DIR%\supabase\migrations\008_create_calendar_events.sql" "supabase\migrations\008_create_calendar_events.sql"
copy "%CURRENT_DIR%\supabase\migrations\009_create_calendar_table.sql" "supabase\migrations\009_create_calendar_table.sql"

REM ARQUIVOS DE API (APENAS B2B - SEM TRADING)
echo 🔧 API Purpose Food B2B...
copy "%CURRENT_DIR%\api\index.ts" "api\index.ts"
copy "%CURRENT_DIR%\api\server.ts" "api\server.ts"
copy "%CURRENT_DIR%\api\app.ts" "api\app.ts"
copy "%CURRENT_DIR%\api\routes\auth.ts" "api\routes\auth.ts"
copy "%CURRENT_DIR%\api\routes\products.ts" "api\routes\products.ts"
copy "%CURRENT_DIR%\api\routes\orders.ts" "api\routes\orders.ts"
copy "%CURRENT_DIR%\api\routes\calendar.ts" "api\routes\calendar.ts"
copy "%CURRENT_DIR%\api\routes\customers.ts" "api\routes\customers.ts"
copy "%CURRENT_DIR%\api\routes\financial.ts" "api\routes\financial.ts"
copy "%CURRENT_DIR%\api\routes\invoices.ts" "api\routes\invoices.ts"
copy "%CURRENT_DIR%\api\routes\sales.ts" "api\routes\sales.ts"
copy "%CURRENT_DIR%\api\routes\socialMedia.ts" "api\routes\socialMedia.ts"
copy "%CURRENT_DIR%\api\routes\stripe.ts" "api\routes\stripe.ts"
copy "%CURRENT_DIR%\api\routes\fix-schema.ts" "api\routes\fix-schema.ts"
copy "%CURRENT_DIR%\api\services\googleCalendarAuth.ts" "api\services\googleCalendarAuth.ts"
copy "%CURRENT_DIR%\api\services\googleCalendarService.ts" "api\services\googleCalendarService.ts"

REM ARQUIVOS DE FRONTEND (APENAS B2B)
echo 🎨 Frontend Purpose Food B2B...

REM Arquivos principais
copy "%CURRENT_DIR%\src\main.tsx" "src\main.tsx"
copy "%CURRENT_DIR%\src\App.tsx" "src\App.tsx"
copy "%CURRENT_DIR%\src\CustomerApp.tsx" "src\CustomerApp.tsx"
copy "%CURRENT_DIR%\src\index.css" "src\index.css"
copy "%CURRENT_DIR%\src\vite-env.d.ts" "src\vite-env.d.ts"

REM Configurações
copy "%CURRENT_DIR%\src\config\supabase.config.ts" "src\config\supabase.config.ts"

REM Componentes essenciais
copy "%CURRENT_DIR%\src\components\Layout\Layout.tsx" "src\components\Layout\Layout.tsx"
copy "%CURRENT_DIR%\src\components\Layout\Header.tsx" "src\components\Layout\Header.tsx"
copy "%CURRENT_DIR%\src\components\Layout\Sidebar.tsx" "src\components\Layout\Sidebar.tsx"
copy "%CURRENT_DIR%\src\components\ProtectedRoute.tsx" "src\components\ProtectedRoute.tsx"
copy "%CURRENT_DIR%\src\components\Empty.tsx" "src\components\Empty.tsx"
copy "%CURRENT_DIR%\src\components\MetricCard.tsx" "src\components\MetricCard.tsx"

REM Componentes UI essenciais
copy "%CURRENT_DIR%\src\components\ui\DataTable.tsx" "src\components\ui\DataTable.tsx"
copy "%CURRENT_DIR%\src\components\ui\FormModal.tsx" "src\components\ui\FormModal.tsx"
copy "%CURRENT_DIR%\src\components\ui\ProductFormModal.tsx" "src\components\ui\ProductFormModal.tsx"
copy "%CURRENT_DIR%\src\components\ui\OrderFormModal.tsx" "src\components\ui\OrderFormModal.tsx"
copy "%CURRENT_DIR%\src\components\ui\TransactionFormModal.tsx" "src\components\ui\TransactionFormModal.tsx"
copy "%CURRENT_DIR%\src\components\ui\CustomerFormModal.tsx" "src\components\ui\CustomerFormModal.tsx"
copy "%CURRENT_DIR%\src\components\ui\InvoiceFormModal.tsx" "src\components\ui\InvoiceFormModal.tsx"
copy "%CURRENT_DIR%\src\components\ui\GoalFormModal.tsx" "src\components\ui\GoalFormModal.tsx"
copy "%CURRENT_DIR%\src\components\ui\ProductGrid.tsx" "src\components\ui\ProductGrid.tsx"
copy "%CURRENT_DIR%\src\components\ui\CustomerGrid.tsx" "src\components\ui\CustomerGrid.tsx"
copy "%CURRENT_DIR%\src\components\ui\MetricCard.tsx" "src\components\ui\MetricCard.tsx"
copy "%CURRENT_DIR%\src\components\ui\SalesChart.tsx" "src\components\ui\SalesChart.tsx"
copy "%CURRENT_DIR%\src\components\ui\CashFlowChart.tsx" "src\components\ui\CashFlowChart.tsx"
copy "%CURRENT_DIR%\src\components\ui\NotificationBell.tsx" "src\components\ui\NotificationBell.tsx"
copy "%CURRENT_DIR%\src\components\ui\AvailabilityInfo.tsx" "src\components\ui\AvailabilityInfo.tsx"
copy "%CURRENT_DIR%\src\components\ui\ProductAvailabilityNotification.tsx" "src\components\ui\ProductAvailabilityNotification.tsx"
copy "%CURRENT_DIR%\src\components\ui\PurposeFoodLogo.tsx" "src\components\ui\PurposeFoodLogo.tsx"
copy "%CURRENT_DIR%\src\components\ui\CustomerLayout.tsx" "src\components\ui\CustomerLayout.tsx"

REM Dashboard
copy "%CURRENT_DIR%\src\components\Dashboard\UpcomingEventsWidget.tsx" "src\components\Dashboard\UpcomingEventsWidget.tsx"

REM Páginas principais
copy "%CURRENT_DIR%\src\pages\Dashboard.tsx" "src\pages\Dashboard.tsx"
copy "%CURRENT_DIR%\src\pages\Products.tsx" "src\pages\Products.tsx"
copy "%CURRENT_DIR%\src\pages\Orders.tsx" "src\pages\Orders.tsx"
copy "%CURRENT_DIR%\src\pages\Calendar.tsx" "src\pages\Calendar.tsx"
copy "%CURRENT_DIR%\src\pages\Financial.tsx" "src\pages\Financial.tsx"
copy "%CURRENT_DIR%\src\pages\Customers.tsx" "src\pages\Customers.tsx"
copy "%CURRENT_DIR%\src\pages\Invoices.tsx" "src\pages\Invoices.tsx"
copy "%CURRENT_DIR%\src\pages\Sales.tsx" "src\pages\Sales.tsx"
copy "%CURRENT_DIR%\src\pages\SocialMedia.tsx" "src\pages\SocialMedia.tsx"
copy "%CURRENT_DIR%\src\pages\Reports.tsx" "src\pages\Reports.tsx"
copy "%CURRENT_DIR%\src\pages\Settings.tsx" "src\pages\Settings.tsx"
copy "%CURRENT_DIR%\src\pages\Profile.tsx" "src\pages\Profile.tsx"
copy "%CURRENT_DIR%\src\pages\Login.tsx" "src\pages\Login.tsx"
copy "%CURRENT_DIR%\src\pages\EventForm.tsx" "src\pages\EventForm.tsx"
copy "%CURRENT_DIR%\src\pages\Notifications.tsx" "src\pages\Notifications.tsx"

REM Páginas do cliente
copy "%CURRENT_DIR%\src\pages\customer\CustomerHome.tsx" "src\pages\customer\CustomerHome.tsx"
copy "%CURRENT_DIR%\src\pages\customer\CustomerProducts.tsx" "src\pages\customer\CustomerProducts.tsx"
copy "%CURRENT_DIR%\src\pages\customer\CustomerCart.tsx" "src\pages\customer\CustomerCart.tsx"
copy "%CURRENT_DIR%\src\pages\customer\CustomerCheckout.tsx" "src\pages\customer\CustomerCheckout.tsx"
copy "%CURRENT_DIR%\src\pages\customer\CustomerOrders.tsx" "src\pages\customer\CustomerOrders.tsx"
copy "%CURRENT_DIR%\src\pages\customer\CustomerProfile.tsx" "src\pages\customer\CustomerProfile.tsx"
copy "%CURRENT_DIR%\src\pages\customer\CustomerLogin.tsx" "src\pages\customer\CustomerLogin.tsx"
copy "%CURRENT_DIR%\src\pages\customer\CustomerRegister.tsx" "src\pages\customer\CustomerRegister.tsx"
copy "%CURRENT_DIR%\src\pages\customer\CustomerLayout.tsx" "src\pages\customer\CustomerLayout.tsx"
copy "%CURRENT_DIR%\src\pages\customer\OrderConfirmation.tsx" "src\pages\customer\OrderConfirmation.tsx"
copy "%CURRENT_DIR%\src\pages\customer\Checkout.tsx" "src\pages\customer\Checkout.tsx"

REM Hooks
copy "%CURRENT_DIR%\src\hooks\usePreventLogout.ts" "src\hooks\usePreventLogout.ts"
copy "%CURRENT_DIR%\src\hooks\useProductAvailability.ts" "src\hooks\useProductAvailability.ts"
copy "%CURRENT_DIR%\src\hooks\useTheme.ts" "src\hooks\useTheme.ts"

REM Stores
copy "%CURRENT_DIR%\src\stores\authStore.ts" "src\stores\authStore.ts"
copy "%CURRENT_DIR%\src\stores\customerStore.ts" "src\stores\customerStore.ts"

REM Types
copy "%CURRENT_DIR%\src\types\product.ts" "src\types\product.ts"

REM Utils
copy "%CURRENT_DIR%\src\utils\databaseHelpers.ts" "src\utils\databaseHelpers.ts"
copy "%CURRENT_DIR%\src\utils\customerIntegration.ts" "src\utils\customerIntegration.ts"

REM Arquivos de configuração do cliente
copy "%CURRENT_DIR%\src\customer-main.tsx" "src\customer-main.tsx"
copy "%CURRENT_DIR%\src\CustomerApp.tsx" "src\CustomerApp.tsx"

REM Arquivos públicos
copy "%CURRENT_DIR%\public\favicon.svg" "public\favicon.svg"

REM Arquivos de documentação relevantes
copy "%CURRENT_DIR%\README.md" "README.md"
copy "%CURRENT_DIR%\CONFIGURACAO_RAPIDA.md" "CONFIGURACAO_RAPIDA.md"
copy "%CURRENT_DIR%\CORRECOES_SCHEMA_SUPABASE.md" "CORRECOES_SCHEMA_SUPABASE.md"
copy "%CURRENT_DIR%\DEPLOY_B2B_CHECKLIST.md" "DEPLOY_B2B_CHECKLIST.md"
copy "%CURRENT_DIR%\ENV_EXAMPLE.txt" "ENV_EXAMPLE.txt"
copy "%CURRENT_DIR%\GUIA_TESTE_DASHBOARD.md" "GUIA_TESTE_DASHBOARD.md"
copy "%CURRENT_DIR%\GUIA_TESTE_SISTEMA.md" "GUIA_TESTE_SISTEMA.md"
copy "%CURRENT_DIR%\PROJETO_FINALIZADO.md" "PROJETO_FINALIZADO.md"
copy "%CURRENT_DIR%\SUPABASE_SETUP_GUIA.md" "SUPABASE_SETUP_GUIA.md"

echo.
echo 📊 Contando arquivos do projeto B2B...
dir /s /b | find /c ".\" > file_count.txt
set /p FILE_COUNT=<file_count.txt
echo Total de arquivos no B2B: %FILE_COUNT%

echo.
echo ✅ SEGREGAÇÃO CONCLUÍDA!
echo 📁 Projeto B2B limpo criado em: %B2B_DIR%
echo 📊 Total de arquivos: %FILE_COUNT%
echo.
echo 🎯 Próximos passos:
echo 1. cd "%B2B_DIR%"
echo 2. npm install
echo 3. npm run dev
echo 4. npm run build
echo 5. npx vercel --prod
echo.
pause