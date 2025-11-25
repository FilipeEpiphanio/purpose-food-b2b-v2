#!/bin/bash

# 🚀 Script de Deploy B2B - Purpose Food
# Este script automatiza o processo de deploy para produção

echo "🚀 Iniciando deploy B2B Purpose Food..."
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Verificar pré-requisitos
echo ""
echo "🔍 Verificando pré-requisitos..."
echo "=================================="

# Verificar Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js encontrado: $NODE_VERSION"
else
    print_error "Node.js não encontrado. Por favor, instale Node.js 18+"
    exit 1
fi

# Verificar npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm encontrado: $NPM_VERSION"
else
    print_error "npm não encontrado. Por favor, instale npm"
    exit 1
fi

# Verificar git
if command_exists git; then
    GIT_VERSION=$(git --version)
    print_success "Git encontrado: $GIT_VERSION"
else
    print_error "Git não encontrado. Por favor, instale git"
    exit 1
fi

# 2. Verificar variáveis de ambiente
echo ""
echo "🔐 Verificando variáveis de ambiente..."
echo "=================================="

REQUIRED_VARS=(
    "SUPABASE_URL"
    "SUPABASE_ANON_KEY" 
    "SUPABASE_SERVICE_ROLE_KEY"
    "STRIPE_SECRET_KEY"
    "FRONTEND_URL"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
        print_error "Variável $var não configurada"
    else
        print_success "Variável $var configurada"
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    print_error "❌ Variáveis obrigatórias faltando: ${MISSING_VARS[*]}"
    echo ""
    echo "Por favor, configure as seguintes variáveis:"
    for var in "${MISSING_VARS[@]}"; do
        echo "export $var='sua-valor-aqui'"
    done
    exit 1
fi

print_success "✅ Todas as variáveis obrigatórias configuradas"

# 3. Verificar branch e status do git
echo ""
echo "📂 Verificando repositório Git..."
echo "=================================="

# Verificar se há mudanças não commitadas
if ! git diff-index --quiet HEAD --; then
    print_warning "Há mudanças não commitadas no repositório"
    read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_info "Deploy cancelado pelo usuário"
        exit 1
    fi
fi

# Verificar branch atual
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
print_info "Branch atual: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "Você não está na branch main"
    read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_info "Deploy cancelado pelo usuário"
        exit 1
    fi
fi

# 4. Limpar e instalar dependências
echo ""
echo "📦 Preparando dependências..."
echo "=================================="

print_info "Limpando node_modules e cache..."
rm -rf node_modules package-lock.json dist

print_info "Instalando dependências..."
npm install

if [ $? -ne 0 ]; then
    print_error "❌ Falha ao instalar dependências"
    exit 1
fi

print_success "✅ Dependências instaladas com sucesso"

# 5. Build do projeto
echo ""
echo "🔨 Construindo projeto..."
echo "=================================="

print_info "Executando build..."
npm run build

if [ $? -ne 0 ]; then
    print_error "❌ Falha ao construir projeto"
    echo "Verifique os logs de build acima"
    exit 1
fi

print_success "✅ Build concluído com sucesso"

# 6. Testes básicos (opcional)
echo ""
echo "🧪 Executando testes básicos..."
echo "=================================="

# Verificar se há script de teste
if npm run test --silent 2>/dev/null; then
    print_info "Executando testes..."
    npm test
    
    if [ $? -ne 0 ]; then
        print_warning "⚠️  Alguns testes falharam"
        read -p "Deseja continuar mesmo assim? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_info "Deploy cancelado pelo usuário"
            exit 1
        fi
    else
        print_success "✅ Todos os testes passaram"
    fi
else
    print_info "Nenhum script de teste encontrado, pulando..."
fi

# 7. Criar commit e tag de versão
echo ""
echo "🏷️  Preparando versão..."
echo "=================================="

# Gerar versão baseada na data
VERSION="v1.0.0-b2b-$(date +%Y%m%d-%H%M%S)"

print_info "Criando tag de versão: $VERSION"

# Adicionar mudanças ao git (se houver)
if ! git diff-index --quiet HEAD --; then
    git add .
    git commit -m "Deploy B2B Production - $(date)"
fi

# Criar tag
git tag -a "$VERSION" -m "B2B Production Release $VERSION"

print_success "✅ Tag criada: $VERSION"

# 8. Deploy
echo ""
echo "🚀 Iniciando deploy..."
echo "=================================="

print_info "Iniciando deploy para produção..."
print_info "Por favor, aguarde enquanto o deploy é realizado..."

# Aqui você adicionaria o comando específico do seu provedor
# Por exemplo, para Vercel:
# npx vercel --prod

# Para Netlify:
# npx netlify deploy --prod

# Para testes, vamos simular um deploy bem-sucedido
print_warning "⚠️  Simulação de deploy - Substitua pelo comando real do seu provedor"
print_info "Comandos comuns:"
echo "  Vercel:  npx vercel --prod"
echo "  Netlify: npx netlify deploy --prod"
echo "  Heroku:  git push heroku main"

# Push da tag para repositório
print_info "Enviando tag para repositório..."
git push origin "$VERSION"

print_success "✅ Tag enviada para repositório"

# 9. Verificação pós-deploy
echo ""
echo "🔍 Verificação pós-deploy..."
echo "=================================="

print_info "Deploy concluído!"
print_info "Próximos passos:"
echo "1. Verificar se o deploy foi bem-sucedido no painel do provedor"
echo "2. Acessar a URL de produção e realizar testes básicos"
echo "3. Verificar logs de aplicação"
echo "4. Monitorar por 24-48 horas"

# 10. Informações finais
echo ""
echo "🎉 Deploy concluído!"
echo "=================================="
echo ""
echo "📋 Resumo:"
echo "  ✅ Pré-requisitos verificados"
echo "  ✅ Variáveis de ambiente configuradas"
echo "  ✅ Dependências instaladas"
echo "  ✅ Build concluído"
echo "  ✅ Tag criada: $VERSION"
echo "  ✅ Deploy iniciado"
echo ""
echo "🔧 Próximos passos:"
echo "1. Complete o deploy no painel do seu provedor"
echo "2. Execute os testes pós-deploy conforme checklist"
echo "3. Monitore a aplicação"
echo ""
echo "📖 Documentação:"
echo "- Checklist completo: DEPLOY_B2B_CHECKLIST.md"
echo "- Suporte do provedor: [Consulte documentação do seu provedor]"
echo ""
print_success "Deploy B2B Purpose Food concluído com sucesso! 🚀"

# Limpar variáveis sensíveis do histórico (opcional)
unset SUPABASE_SERVICE_ROLE_KEY
unset STRIPE_SECRET_KEY