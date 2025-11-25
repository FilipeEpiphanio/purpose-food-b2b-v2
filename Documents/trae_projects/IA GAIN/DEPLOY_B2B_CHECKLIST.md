# 🚀 Checklist de Deploy B2B - Purpose Food

## 📋 **Preparação do Ambiente de Produção**

### 🔐 **1. Segurança e Variáveis de Ambiente**

#### ✅ **Variáveis Obrigatórias (Adicionar ao provedor de deploy):**
```bash
# Supabase
SUPABASE_URL=https://sua-url-producao.supabase.co
SUPABASE_ANON_KEY=sua-anon-key-producao
SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key-producao

# Stripe
STRIPE_SECRET_KEY=sk_live_sua_chave_stripe_producao
STRIPE_PUBLISHABLE_KEY=pk_live_sua_chave_publica_stripe

# Frontend
FRONTEND_URL=https://sua-url-producao.com
VITE_SUPABASE_URL=https://sua-url-producao.supabase.co
VITE_SUPABASE_ANON_KEY=sua-anon-key-producao

# Google Calendar (opcional, se for usar)
GOOGLE_CLIENT_ID=seu-client-id-google
GOOGLE_CLIENT_SECRET=seu-client-secret-google
GOOGLE_REDIRECT_URI=https://sua-url-producao.com/api/calendar/auth/callback
```

#### ⚠️ **Crítico - NUNCA exponha no código:**
- ✅ Removido fallback de chaves hardcoded em `api/routes/stripe.js`
- ✅ Configurado para lançar erro se variáveis não estiverem presentes
- ✅ Service role key apenas no backend, NUNCA no frontend

### 🗄️ **2. Banco de Dados - Migrações**

#### **Aplicar migrações em ordem:**
```bash
# Conectar ao banco de produção e executar:
supabase migration up

# Ou aplicar manualmente os arquivos:
1. supabase/migrations/001_create_tables.sql
2. supabase/migrations/002_add_order_type.sql
3. supabase/migrations/003_add_customer_fields.sql
4. supabase/migrations/004_add_product_fields.sql
5. supabase/migrations/005_create_notifications.sql
6. supabase/migrations/006_fix_schema_final.sql
7. supabase/migrations/007_fix_order_type_column.sql
8. supabase/migrations/008_create_calendar_events.sql
9. supabase/migrations/009_add_invoice_fields_to_orders.sql
```

#### **Verificar após migrações:**
- ✅ Tabela `orders` com campos corretos
- ✅ Tabela `calendar_events` criada
- ✅ Índices aplicados
- ✅ RLS policies configuradas
- ✅ Funções e triggers funcionando

### 🌐 **3. Configurações de Deploy**

#### **Vercel (recomendado)**
```json
// vercel.json já configurado
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index.ts" }
  ]
}
```

#### **Build Settings:**
```bash
# Build Command:
npm run build

# Output Directory:
dist

# Install Command:
npm install
```

### 🔄 **4. Processo de Deploy Passo-a-Passo**

#### **Passo 1: Preparação (5 minutos)**
```bash
# 1.1. Commit das últimas alterações
git add .
git commit -m "Deploy B2B Production - $(date)"

# 1.2. Criar tag de versão
git tag -a v1.0.0-b2b -m "B2B Production Release v1.0.0"

# 1.3. Push para repositório
git push origin main --tags
```

#### **Passo 2: Configuração do Ambiente (10 minutos)**
```bash
# 2.1. Configurar variáveis no provedor de deploy
# Adicionar todas as variáveis do item 1 acima

# 2.2. Verificar conexão com Supabase
# Testar endpoint: https://sua-url/api/health

# 2.3. Configurar domínio customizado (se aplicável)
# Configurar DNS e SSL
```

#### **Passo 3: Deploy (15 minutos)**
```bash
# 3.1. Iniciar deploy pelo painel do provedor
# Aguardar build e deploy automático

# 3.2. Monitorar logs de build
# Verificar se não há erros de compilação

# 3.3. Verificar deploy
# Acessar URL de produção e testar
```

### 🧪 **5. Testes Pós-Deploy**

#### **Testes Críticos (Realizar em Produção):**

**🔐 Autenticação:**
```bash
# 1. Testar login
- Acessar https://sua-url.com/login
- Fazer login com credenciais válidas
- Verificar redirecionamento para dashboard

# 2. Testar sessão
- Navegar entre páginas
- Verificar se não há logout indevido
- Testar atualização de página (F5)
```

**📊 Dashboard:**
```bash
# 1. Verificar métricas
- Total de vendas aparece corretamente?
- Gráficos estão carregando?
- Widget de eventos está funcionando?

# 2. Testar navegação
- Todos os menus estão acessíveis?
- Navegação entre módulos está fluida?
```

**📦 Produtos:**
```bash
# 1. CRUD básico
- Listar produtos
- Criar novo produto
- Editar produto existente
- Excluir produto (cuidado!)

# 2. Verificar integrações
- Imagens estão carregando?
- Estoque está correto?
```

**📋 Pedidos:**
```bash
# 1. Listar pedidos
- Pedidos estão aparecendo?
- Status estão corretos?
- Filtros estão funcionando?

# 2. Testar SAT SEF/SC
- Clicar em "Gerar NF" em um pedido
- Verificar se abre SAT em nova aba
- Confirmar que não causa logout
```

**📅 Calendário:**
```bash
# 1. Visualizar calendário
- Eventos estão aparecendo?
- Navegação entre meses funciona?

# 2. Testar integração (se configurada)
- Google Calendar sync está funcionando?
```

### 📱 **6. Configurações Mobile/Responsivo**
- ✅ Testar em dispositivos móveis
- ✅ Verificar touch interactions
- ✅ Confirmar menus mobile
- ✅ Testar formulários em mobile

### 🔍 **7. Performance e SEO**
- ✅ Verificar tempo de carregamento (< 3s ideal)
- ✅ Confirmar meta tags básicas
- ✅ Testar PWA (se aplicável)
- ✅ Verificar console de erros

### 🛡️ **8. Segurança Final**
- ✅ HTTPS ativado e funcionando
- ✅ Headers de segurança configurados
- ✅ CORS configurado corretamente
- ✅ Rate limiting implementado
- ✅ Validações de input funcionando

### 📧 **9. Notificações e Integrações**
- ✅ Testar sistema de notificações (se configurado)
- ✅ Verificar envio de emails (se aplicável)
- ✅ Confirmar integrações externas

### 📊 **10. Monitoramento**
- ✅ Configurar Google Analytics
- ✅ Configurar Sentry para error tracking (recomendado)
- ✅ Configurar uptime monitoring
- ✅ Configurar logs de aplicação

## 🚨 **Rollback Plan (Se algo der errado)**

### **Procedimento de Emergência:**
1. **Identificar problema crítico**
2. **Avaliar impacto**
3. **Se necessário, fazer rollback:**
   ```bash
   # Reverter para versão anterior no painel do provedor
   # Ou fazer deploy de versão anterior via git
   git revert v1.0.0-b2b
   git push origin main
   ```

### **Contatos de Emergência:**
- **Provedor de Deploy**: [Suporte do seu provedor]
- **Supabase**: [Suporte Supabase]
- **Stripe**: [Suporte Stripe]
- **Time de Desenvolvimento**: [Seu contato]

## ✅ **Confirmação Final**

### **Antes de liberar para usuários:**
- [ ] Todos os testes críticos passaram
- [ ] Nenhum erro crítico no console
- [ ] Performance aceitável
- [ ] Backup do banco atualizado
- [ ] Documentação atualizada
- [ ] Time treinado sobre novas funcionalidades

### **Após deploy bem-sucedido:**
- [ ] Monitorar logs por 24-48h
- [ ] Coletar feedback inicial
- [ ] Preparar hotfixes se necessário
- [ ] Documentar lições aprendidas

---

**📞 Suporte**: Em caso de dúvidas durante o deploy, consulte:
- Documentação do provedor de deploy
- Logs de aplicação
- Console do navegador
- Dashboard do Supabase

**🎉 Boa sorte com o deploy!**