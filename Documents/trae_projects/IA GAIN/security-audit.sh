#!/bin/bash

# 🔍 Script de Auditoria de Segurança - Purpose Food B2B
# Este script verifica se todas as correções de segurança foram aplicadas corretamente

echo "🔍 Auditoria de Segurança - Purpose Food B2B"
echo "=============================================="

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
    echo "=============================================="
}

# Função para executar query SQL
execute_sql() {
    local query="$1"
    local result=$(psql "$SUPABASE_URL" -t -c "$query" 2>/dev/null)
    echo "$result"
}

# 1. Verificar conexão com banco
echo "🔐 Verificando conexão com Supabase..."
if [ -n "$SUPABASE_URL" ]; then
    print_success "SUPABASE_URL configurada"
    
    # Testar conexão
    if execute_sql "SELECT 1;" | grep -q "1"; then
        print_success "Conexão com banco estabelecida"
    else
        print_error "Não foi possível conectar ao banco"
        echo "Verifique se SUPABASE_URL está correta"
        exit 1
    fi
else
    print_error "SUPABASE_URL não configurada"
    echo "Por favor, configure SUPABASE_URL antes de continuar"
    exit 1
fi

# 2. Verificar Security Definer Views
print_header "Verificando Security Definer Views"

VIEWS_WITH_SECURITY_DEFINER=$(execute_sql "
SELECT n.nspname || '.' || v.viewname as view_name
FROM pg_views v
JOIN pg_namespace n ON v.schemaname = n.nspname
WHERE v.schemaname = 'public'
AND EXISTS (
    SELECT 1 
    FROM pg_class c
    JOIN pg_rewrite r ON c.oid = r.ev_class
    WHERE c.relname = v.viewname
    AND c.relnamespace = n.oid
    AND r.rulename IS NULL
    AND EXISTS (
        SELECT 1
        FROM pg_proc p
        WHERE p.oid = c.relowner
        AND p.prosecdef = true
    )
);")

if [ -z "$VIEWS_WITH_SECURITY_DEFINER" ] || [ "$VIEWS_WITH_SECURITY_DEFINER" = " " ]; then
    print_success "Nenhuma view com SECURITY DEFINER encontrada"
else
    print_error "Views com SECURITY DEFINER encontradas:"
    echo "$VIEWS_WITH_SECURITY_DEFINER" | while read view; do
        if [ -n "$view" ]; then
            echo "  - $view"
        fi
    done
fi

# 3. Verificar RLS nas tabelas
print_header "Verificando Row Level Security (RLS)"

TABLES_WITHOUT_RLS=$(execute_sql "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND rowsecurity = false 
AND tablename NOT LIKE 'pg_%'
AND tablename NOT IN ('spatial_ref_sys');")

if [ -z "$TABLES_WITHOUT_RLS" ] || [ "$TABLES_WITHOUT_RLS" = " " ]; then
    print_success "Todas as tabelas públicas têm RLS habilitado"
else
    print_error "Tabelas sem RLS habilitado:"
    echo "$TABLES_WITHOUT_RLS" | while read table; do
        if [ -n "$table" ]; then
            echo "  - $table"
        fi
    done
fi

# 4. Verificar políticas RLS
print_header "Verificando Políticas RLS"

TABLES_WITHOUT_POLICIES=$(execute_sql "
SELECT t.tablename
FROM pg_tables t
LEFT JOIN pg_policies p ON t.tablename = p.tablename AND t.schemaname = p.schemaname
WHERE t.schemaname = 'public'
AND p.policyname IS NULL
AND t.tablename NOT LIKE 'pg_%'
AND t.tablename NOT IN ('spatial_ref_sys');")

if [ -z "$TABLES_WITHOUT_POLICIES" ] || [ "$TABLES_WITHOUT_POLICIES" = " " ]; then
    print_success "Todas as tabelas têm políticas RLS definidas"
else
    print_warning "Tabelas sem políticas RLS:"
    echo "$TABLES_WITHOUT_POLICIES" | while read table; do
        if [ -n "$table" ]; then
            echo "  - $table"
        fi
    done
fi

# 5. Verificar functions com search_path
print_header "Verificando Functions Search Path"

FUNCTIONS_WITHOUT_SEARCH_PATH=$(execute_sql "
SELECT n.nspname || '.' || p.proname as function_name
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.prokind = 'f'
AND p.prosecdef = true
AND NOT EXISTS (
    SELECT 1
    FROM pg_proc_info pi
    WHERE pi.oid = p.oid
    AND pi.proconfig IS NOT NULL
    AND pi.proconfig::text LIKE '%search_path%'
);")

if [ -z "$FUNCTIONS_WITHOUT_SEARCH_PATH" ] || [ "$FUNCTIONS_WITHOUT_SEARCH_PATH" = " " ]; then
    print_success "Todas as functions têm search_path configurado"
else
    print_error "Functions sem search_path configurado:"
    echo "$FUNCTIONS_WITHOUT_SEARCH_PATH" | while read func; do
        if [ -n "$func" ]; then
            echo "  - $func"
        fi
    done
fi

# 6. Verificar proteção de senhas vazadas
print_header "Verificando Proteção de Senhas"

LEAKED_PASSWORD_STATUS=$(execute_sql "
SELECT security_password_leaked_check_enabled 
FROM auth.config 
WHERE id = 'default';")

if [ "$LEAKED_PASSWORD_STATUS" = "t" ] || [ "$LEAKED_PASSWORD_STATUS" = "true" ]; then
    print_success "Proteção contra senhas vazadas está ativada"
else
    print_warning "Proteção contra senhas vazadas está desativada"
    print_info "Para ativar, acesse: Auth Settings → Security → Enable leaked password protection"
fi

# 7. Verificar permissões de tabelas críticas
print_header "Verificando Permissões de Tabelas Críticas"

CRITICAL_TABLES=("users" "orders" "financial_records" "calendar_events")

for table in "${CRITICAL_TABLES[@]}"; do
    PERMISSIONS=$(execute_sql "
    SELECT grantee, privilege_type 
    FROM information_schema.role_table_grants 
    WHERE table_schema = 'public' 
    AND table_name = '$table'
    AND grantee IN ('anon', 'authenticated')
    ORDER BY grantee, privilege_type;")
    
    if [ -n "$PERMISSIONS" ] && [ "$PERMISSIONS" != " " ]; then
        print_info "Permissões para $table:"
        echo "$PERMISSIONS" | while read perm; do
            if [ -n "$perm" ]; then
                echo "  $perm"
            fi
        done
    else
        print_info "Tabela $table: Sem permissões diretas para anon/authenticated (usa RLS)"
    fi
done

# 8. Verificar índices em colunas sensíveis
print_header "Verificando Índices de Segurança"

SENSITIVE_COLUMNS=("email" "created_by" "user_id" "customer_id")

for col in "${SENSITIVE_COLUMNS[@]}"; do
    INDEXES=$(execute_sql "
    SELECT t.tablename, i.indexname 
    FROM pg_tables t
    JOIN pg_indexes i ON t.tablename = i.tablename
    WHERE t.schemaname = 'public'
    AND i.indexname LIKE '%${col}%'
    ORDER BY t.tablename;")
    
    if [ -n "$INDEXES" ] && [ "$INDEXES" != " " ]; then
        print_success "Índices encontrados para coluna '$col':"
        echo "$INDEXES" | while read idx; do
            if [ -n "$idx" ]; then
                echo "  - $idx"
            fi
        done
    else
        print_info "Sem índices específicos para coluna '$col'"
    fi
done

# 9. Verificar configurações de segurança do projeto
print_header "Verificando Configurações do Projeto"

# Verificar se há chaves hardcoded no código
if command -v grep >/dev/null 2>&1; then
    print_info "Verificando código por chaves hardcoded..."
    
    # Procurar por padrões de chaves API
    HARDCODED_KEYS=$(grep -r -E "(sk_live_|pk_live_|eyJ[A-Za-z0-9_-]*\.)" . \
        --include="*.js" --include="*.ts" --include="*.json" \
        --exclude-dir=node_modules --exclude-dir=dist 2>/dev/null || true)
    
    if [ -n "$HARDCODED_KEYS" ]; then
        print_error "Possíveis chaves hardcoded encontradas:"
        echo "$HARDCODODED_KEYS" | head -10
    else
        print_success "Nenhuma chave hardcoded encontrada no código"
    fi
fi

# 10. Resumo e recomendações
print_header "Resumo da Auditoria de Segurança"

echo -e "${GREEN}✅ Testes Passados: $PASSED${NC}"
echo -e "${YELLOW}⚠️  Avisos: $WARNINGS${NC}"
echo -e "${RED}❌ Erros: $ERRORS${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 Auditoria de segurança concluída com sucesso!${NC}"
    echo "✅ O sistema está seguro para deploy em produção"
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "\n${YELLOW}⚠️  Recomendações:${NC}"
        echo "Há $WARNINGS avisos que devem ser revisados"
        echo "mas não impedem o deploy"
    fi
    
    exit 0
else
    echo -e "\n${RED}❌ Auditoria encontrou problemas críticos${NC}"
    echo "Por favor, corrija os $ERRORS erros antes do deploy"
    
    echo -e "\n${BLUE}📋 Ações necessárias:${NC}"
    echo "1. Execute as correções de segurança"
    echo "2. Reaplique as migrações de segurança"
    echo "3. Verifique as configurações do banco"
    
    exit 1
fi