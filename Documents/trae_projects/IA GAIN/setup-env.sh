#!/bin/bash

# 📝 Script de Configuração de Ambiente - Purpose Food B2B
# Este script ajuda a configurar as variáveis de ambiente para deploy

echo "📝 Configurador de Ambiente - Purpose Food B2B"
echo "=================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Este script irá ajudá-lo a configurar as variáveis de ambiente necessárias.${NC}"
echo ""

# Função para solicitar input seguro
get_input() {
    local prompt="$1"
    local is_sensitive="$2"
    local value=""
    
    while [ -z "$value" ]; do
        if [ "$is_sensitive" = "true" ]; then
            read -sp "$prompt: " value
            echo "" # Nova linha após input seguro
        else
            read -p "$prompt: " value
        fi
        
        if [ -z "$value" ]; then
            echo -e "${YELLOW}⚠️  Este campo é obrigatório!${NC}"
        fi
    done
    
    echo "$value"
}

# Criar arquivo .env.production
echo "Criando arquivo .env.production..."
echo "=================================="

# Supabase
SUPABASE_URL=$(get_input "URL do Supabase (ex: https://sua-url.supabase.co)")
SUPABASE_ANON_KEY=$(get_input "Supabase Anon Key" "true")
SUPABASE_SERVICE_ROLE_KEY=$(get_input "Supabase Service Role Key" "true")

# Stripe
STRIPE_SECRET_KEY=$(get_input "Stripe Secret Key (live)" "true")
STRIPE_PUBLISHABLE_KEY=$(get_input "Stripe Publishable Key (live)")

# Frontend
FRONTEND_URL=$(get_input "URL do frontend em produção (ex: https://app.purposefood.com)")

# Google Calendar (opcional)
echo ""
echo "Google Calendar Integration (opcional):"
read -p "Deseja configurar Google Calendar? (s/n): " configure_google

if [[ $configure_google =~ ^[Ss]$ ]]; then
    GOOGLE_CLIENT_ID=$(get_input "Google Client ID")
    GOOGLE_CLIENT_SECRET=$(get_input "Google Client Secret" "true")
    GOOGLE_REDIRECT_URI="$FRONTEND_URL/api/calendar/auth/callback"
fi

# Criar arquivo
cat > .env.production << EOF
# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY

# Stripe Configuration
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY

# Frontend Configuration
FRONTEND_URL=$FRONTEND_URL
VITE_SUPABASE_URL=$SUPABASE_URL
VITE_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY

# Google Calendar (opcional)
EOF

if [[ $configure_google =~ ^[Ss]$ ]]; then
    cat >> .env.production << EOF
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI=$GOOGLE_REDIRECT_URI
EOF
fi

echo ""
echo -e "${GREEN}✅ Arquivo .env.production criado com sucesso!${NC}"
echo ""

# Criar instruções para provedores
echo ""
echo "📋 Instruções para Configuração em Provedores:"
echo "=================================="

echo ""
echo "🔧 Vercel:"
echo "1. Acesse: https://vercel.com/dashboard"
echo "2. Selecione seu projeto"
echo "3. Vá em Settings → Environment Variables"
echo "4. Adicione as seguintes variáveis:"
echo ""

# Listar variáveis para copiar
echo "📋 Variáveis para copiar:"
echo "=================================="
cat .env.production | while IFS= read -r line; do
    if [[ $line =~ ^#.*$ ]] || [[ -z $line ]]; then
        continue
    fi
    echo "  $line"
done

echo ""
echo "🔧 Netlify:"
echo "1. Acesse: https://app.netlify.com"
echo "2. Selecione seu projeto"
echo "3. Vá em Site settings → Environment variables"
echo "4. Clique em 'Add a variable' para cada uma"

echo ""
echo "🔧 Outros Provedores:"
echo "Procure por 'Environment Variables' ou 'Config Vars'"
echo "nas configurações do seu projeto"

echo ""
echo "⚠️  IMPORTANTE:"
echo "- NUNCA commite o arquivo .env.production"
echo "- Adicione .env.production ao .gitignore"
echo "- Mantenha backups seguros das chaves"
echo "- Use chaves diferentes para desenvolvimento e produção"

echo ""
echo -e "${GREEN}🎉 Configuração concluída!${NC}"
echo "Próximo passo: Execute ./deploy-b2b.sh para fazer o deploy"

# Adicionar ao .gitignore se não existir
if ! grep -q ".env.production" .gitignore 2>/dev/null; then
    echo ".env.production" >> .gitignore
    echo -e "${GREEN}✅ .env.production adicionado ao .gitignore${NC}"
fi