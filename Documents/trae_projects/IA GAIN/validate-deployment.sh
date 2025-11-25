#!/bin/bash

# 🔍 Script de Validação Final - Purpose Food B2B
# Este script verifica se tudo está pronto para deploy

echo "🔍 Validação Final - Purpose Food B2B"
echo "======================================"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Contadores
ERRORS=0
WARNINGS=0
PASSED=0

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

print_info() {
    echo -e "ℹ️  $1"
}

print_header() {
    echo -e "\n${BLUE}🔍 $1${NC}"
    echo "======================================"
}

# 1. Verificar estrutura do projeto
print_header "Estrutura do Projeto"

if [ -f "package.json" ]; then
    print_success "package.json encontrado"
else
    print_error "package.json não encontrado"
fi

if [ -f "vercel.json" ]; then
    print_success "vercel.json encontrado"
else
    print_warning "vercel.json não encontrado (usando configuração padrão)"
fi

if [ -d "src" ]; then
    print_success "Diretório src encontrado"
else
    print_error "Diretório src não encontrado"
fi

if [ -d "api" ]; then
    print_success "Diretório api encontrado"
else
    print_error "Diretório api não encontrado"
fi

if [ -d "supabase" ]; then
    print_success "Diretório supabase encontrado"
else
    print_warning "Diretório supabase não encontrado"
fi

# 2. Verificar dependências
print_header "Dependências"

if [ -d "node_modules" ]; then
    print_success "node_modules encontrado"
    
    # Verificar dependências críticas
    if [ -f "node_modules/react/package.json" ]; then
        print_success "React instalado"
    else
        print_error "React não instalado"
    fi
    
    if [ -f "node_modules/@supabase/supabase-js/package.json" ]; then
        print_success "Supabase instalado"
    else
        print_error "Supabase não instalado"
    fi
    
    if [ -f "node_modules/stripe/package.json" ]; then
        print_success "Stripe instalado"
    else
        print_error "Stripe não instalado"
    fi
else
    print_error "node_modules não encontrado - execute npm install"
fi

# 3. Verificar variáveis de ambiente
print_header "Variáveis de Ambiente"

REQUIRED_VARS=(
    "SUPABASE_URL"
    "SUPABASE_ANON_KEY"
    "SUPABASE_SERVICE_ROLE_KEY"
    "STRIPE_SECRET_KEY"
    "FRONTEND_URL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        print_success "$var configurada"
    else
        print_error "$var não configurada"
    fi
done

# 4. Verificar segurança
print_header "Segurança"

# Verificar se há chaves hardcoded
if grep -r "sk_test_" api/ --include="*.js" --include="*.ts" 2>/dev/null; then
    print_error "Chaves de teste hardcoded encontradas no código"
else
    print_success "Nenhuma chave hardcode encontrada"
fi

if grep -r "eyJ" api/ --include="*.js" --include="*.ts" 2>/dev/null | grep -v "process.env"; then
    print_warning "Possíveis tokens JWT hardcoded encontrados"
else
    print_success "Nenhum token hardcode encontrado"
fi

# 5. Verificar build
print_header "Build"

if [ -d "dist" ]; then
    print_success "Diretório dist encontrado"
    
    if [ -f "dist/index.html" ]; then
        print_success "index.html encontrado no dist"
    else
        print_error "index.html não encontrado no dist"
    fi
else
    print_warning "Diretório dist não encontrado - execute npm run build"
fi

# 6. Verificar migrações do banco
print_header "Banco de Dados"

MIGRATION_FILES=(
    "supabase/migrations/001_create_tables.sql"
    "supabase/migrations/008_create_calendar_events.sql"
    "supabase/migrations/009_add_invoice_fields_to_orders.sql"
)

for file in "${MIGRATION_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Migração $(basename "$file") encontrada"
    else
        print_warning "Migração $(basename "$file") não encontrada"
    fi
done

# 7. Verificar arquivos críticos
print_header "Arquivos Críticos"

CRITICAL_FILES=(
    "src/App.tsx"
    "src/main.tsx"
    "api/server.ts"
    "api/index.ts"
    "vercel.json"
    "package.json"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$(basename "$file") encontrado"
    else
        print_error "$(basename "$file") não encontrado"
    fi
done

# 8. Verificar integrações
print_header "Integrações"

# Google Calendar (opcional)
if [ -n "$GOOGLE_CLIENT_ID" ] && [ -n "$GOOGLE_CLIENT_SECRET" ]; then
    print_success "Google Calendar configurado"
else
    print_info "Google Calendar não configurado (opcional)"
fi

# Stripe
if [ -n "$STRIPE_SECRET_KEY" ]; then
    if [[ "$STRIPE_SECRET_KEY" == sk_live_* ]]; then
        print_success "Stripe configurado com chave de produção"
    else
        print_warning "Stripe configurado com chave de teste"
    fi
else
    print_error "Stripe não configurado"
fi

# 9. Verificar scripts de deploy
print_header "Scripts de Deploy"

if [ -f "deploy-b2b.sh" ] || [ -f "deploy-b2b.bat" ]; then
    print_success "Script de deploy encontrado"
else
    print_warning "Script de deploy não encontrado"
fi

if [ -f "setup-env.sh" ] || [ -f "setup-env.bat" ]; then
    print_success "Script de configuração encontrado"
else
    print_warning "Script de configuração não encontrado"
fi

# 10. Teste de sintaxe (se possível)
print_header "Testes de Sintaxe"

# Verificar TypeScript (se tsconfig existir)
if [ -f "tsconfig.json" ]; then
    print_info "Verificando TypeScript..."
    if npm run check --silent 2>/dev/null; then
        npm run check > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            print_success "TypeScript sem erros"
        else
            print_error "Erros de TypeScript encontrados"
        fi
    else
        print_info "Script de check não configurado"
    fi
fi

# 11. Resumo final
print_header "Resumo Final"

echo -e "${GREEN}✅ Testes Passados: $PASSED${NC}"
echo -e "${YELLOW}⚠️  Avisos: $WARNINGS${NC}"
echo -e "${RED}❌ Erros: $ERRORS${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 Sistema pronto para deploy!${NC}"
    echo "✅ Todas as verificações críticas passaram"
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "\n${YELLOW}⚠️  Atenção:${NC}"
        echo "Há $WARNINGS avisos que devem ser revisados"
        echo "mas não impedem o deploy"
    fi
    
    echo -e "\n${BLUE}🚀 Próximo passo:${NC}"
    echo "Execute o script de deploy para prosseguir"
    exit 0
else
    echo -e "\n${RED}❌ Sistema NÃO está pronto para deploy${NC}"
    echo "Por favor, corrija os $ERRORS erros antes de continuar"
    
    echo -e "\n${BLUE}📋 Ações necessárias:${NC}"
    echo "1. Configure todas as variáveis de ambiente obrigatórias"
    echo "2. Instale as dependências: npm install"
    echo "3. Execute o build: npm run build"
    echo "4. Configure as integrações necessárias"
    
    exit 1
fi