# 🧪 GUIA DE TESTE DO DASHBOARD - PURPOSE FOOD

## 📋 PASSO A PASSO PARA TESTAR O DASHBOARD

### 1️⃣ PRIMEIRO: Popular o Banco de Dados

**Acesse o Supabase:**
1. Vá para https://supabase.com
2. Faça login com suas credenciais
3. Acesse o projeto: `xqsocdvvvbgdgrezoqlf`
4. Clique em "SQL Editor" no menu lateral
5. Cole o conteúdo do arquivo `dashboard_test.sql`
6. Clique em "RUN" para executar

**Resultado esperado:**
- ✅ 8 produtos inseridos
- ✅ 8 clientes inseridos  
- ✅ 10 pedidos inseridos
- ✅ Dados financeiros inseridos

### 2️⃣ SEGUNDO: Testar Funcionalidade dos Botões

**No navegador:**
1. Abra o console do navegador (F12)
2. Vá para a aba "Console"
3. Copie e cole o conteúdo do arquivo `browser_test_dashboard.js`
4. Pressione Enter para executar
5. Execute a função: `testDashboardButtons()`

**O que isso faz:**
- Adiciona event listeners temporários a TODOS os botões
- Mostra notificações visuais quando você clica
- Registra no console cada ação realizada

### 3️⃣ TERCEIRO: Verificar Estado do Sistema

**Execute no console:**
```javascript
checkSystemStatus();
```

**Isso verifica:**
- Se você está autenticado
- URL atual
- Disponibilidade do Supabase

### 4️⃣ QUARTO: Testar Cada Botão do Dashboard

**Teste estes botões específicos:**

#### 📊 Cards de Métricas (clique em cada um):
- ✅ Total de Pedidos
- ✅ Faturamento do Mês
- ✅ Clientes Ativos
- ✅ Ticket Médio
- ✅ Lucro Estimado
- ✅ Produtos em Estoque

#### 🔗 Links de Navegação:
- ✅ Dashboard (Home)
- ✅ Produtos
- ✅ Pedidos
- ✅ Clientes
- ✅ Financeiro
- ✅ Relatórios
- ✅ Vendas
- ✅ Redes Sociais
- ✅ Notas Fiscais

#### ➕ Botões de Ação:
- ✅ "Novo Pedido" (se existir)
- ✅ "Adicionar Produto" (se existir)
- ✅ "Novo Cliente" (se existir)
- ✅ Botões de editar/excluir

### 5️⃣ QUINTO: Verificar Respostas no Console

**Abra o console (F12) e observe:**
- Mensagens de sucesso ao clicar botões
- Notificações visuais no canto superior direito
- Erros ou warnings (se houver)

## 🎯 RESULTADOS ESPERADOS

### Se TUDO estiver funcionando:
- ✅ Todos os botões respondem ao clique
- ✅ Notificações verdes aparecem no canto superior direito
- ✅ Console mostra mensagens de sucesso
- ✅ Navegação entre páginas funciona

### Se ALGO não estiver funcionando:
- ❌ Botões não respondem
- ❌ Nenhuma notificação aparece
- ❌ Console mostra erros vermelhos
- ❌ Páginas não carregam

## 🔧 SOLUÇÕES PARA PROBLEMAS COMUNS

### Problema: "Botões não fazem nada"
**Solução:**
1. Verifique se o script de teste foi executado
2. Recarregue a página (F5)
3. Execute o script novamente no console
4. Tente clicar em diferentes áreas do botão

### Problema: "Não consigo acessar o Supabase"
**Solução:**
1. Verifique suas credenciais no arquivo `.env`
2. Confirme que o projeto está ativo
3. Teste a conexão com: `curl -H "apikey: SUA_CHAVE" https://xqsocdvvvbgdgrezoqlf.supabase.co/rest/v1/products`

### Problema: "Dados não aparecem no dashboard"
**Solução:**
1. Execute o script SQL no Supabase
2. Verifique se as permissões estão corretas
3. Confirme que está autenticado no sistema

## 📊 TESTES ESPECÍFICOS PARA CADA MÓDULO

### Dashboard:
- [ ] Cards de métricas clicáveis
- [ ] Gráficos visíveis
- [ ] Tabela de pedidos recentes
- [ ] Alertas de estoque

### Produtos:
- [ ] Lista de produtos carrega
- [ ] Botão "Novo Produto" funciona
- [ ] Busca e filtros funcionam
- [ ] Edição e exclusão de produtos

### Pedidos:
- [ ] Kanban de pedidos visível
- [ ] Arrastar pedidos entre colunas
- [ ] Detalhes do pedido ao clicar
- [ ] Criar novo pedido

### Clientes:
- [ ] Lista de clientes carrega
- [ ] Adicionar novo cliente
- [ ] Filtrar por tipo (individual/empresa)
- [ ] Ver histórico de pedidos

### Financeiro:
- [ ] Resumo financeiro visível
- [ ] Adicionar receita/despesa
- [ ] Gráficos de tendência
- [ ] Relatório mensal

## 🚨 COMO REPORTAR PROBLEMAS

Quando encontrar um problema, forneça:
1. **O que você estava tentando fazer?**
2. **O que aconteceu exatamente?**
3. **Mensagem de erro no console (se houver)**
4. **Screenshots se possível**
5. **Passos para reproduzir o problema**

## 📞 SUPORTE

Se precisar de ajuda adicional:
1. Verifique o console do navegador (F12)
2. Teste com o script de diagnóstico
3. Verifique a conexão com Supabase
4. Confirme que está autenticado

---
**Bons testes! 🎉**