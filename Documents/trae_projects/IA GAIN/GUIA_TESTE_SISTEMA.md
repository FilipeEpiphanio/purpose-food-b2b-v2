# 🚀 GUIA PASSO A PASSO - REINICIAR E TESTAR SISTEMA

## PASSO 3: REINICIAR O SERVIDOR

### 3.1 Parar o servidor atual
1. **Vá para o terminal** onde está rodando o `npm run dev`
2. **Pressione `Ctrl + C`** para parar o servidor
3. **Aguarde** aparecer o prompt de comando novamente

### 3.2 Reiniciar o servidor
```bash
npm run dev
```

### 3.3 Verificar se reiniciou corretamente
Você deve ver algo assim:
```
[0] VITE v6.4.1  ready in 2313 ms
[0] 
[0]   ➜  Local:   http://localhost:5173/
[1] 🚀 Server running on port 3001
```

## PASSO 4: ACESSAR O SISTEMA

### 4.1 Abrir no navegador
- **URL:** http://localhost:5173
- **Deve aparecer:** Tela de login com "Entrar" e "Criar conta"

### 4.2 Se aparecer erro de conexão
1. Verifique se o servidor está rodando (Passo 3.3)
2. Tente: http://127.0.0.1:5173
3. Verifique se a porta 5173 não está em uso

## PASSO 5: REGISTRAR-SE

### 5.1 Criar nova conta
1. **Clique em "Criar conta"**
2. **Preencha:**
   - Email: seu-email@exemplo.com
   - Senha: mínimo 6 caracteres
   - Confirmar senha: mesma senha
3. **Clique em "Registrar"**

### 5.2 Se der erro ao registrar
1. **Verifique no console do navegador** (F12 → Console)
2. **Verifique no terminal** se aparece algum erro
3. **Verifique se o SQL foi executado corretamente** no Supabase

### 5.3 Verificar registro no Supabase
1. Acesse: https://supabase.com
2. Vá para seu projeto
3. Clique em **"Authentication"** → **"Users"**
4. Seu usuário deve aparecer na lista

## PASSO 6: TESTAR FUNCIONALIDADES

### 6.1 Após login bem-sucedido
Você verá o **Dashboard** com:
- Cards de métricas (Total de Vendas, Pedidos, etc.)
- Gráficos de vendas
- Lista de pedidos recentes

### 6.2 Testar cada módulo

#### 📦 **PRODUTOS**
1. Clique em **"Produtos"** no menu lateral
2. Deve aparecer lista com 6 produtos de exemplo
3. Teste:
   - Adicionar novo produto
   - Editar produto existente
   - Excluir produto

#### 👥 **CLIENTES**
1. Clique em **"Clientes"** no menu lateral
2. Deve aparecer lista com 5 clientes de exemplo
3. Teste:
   - Adicionar novo cliente
   - Editar cliente existente

#### 📋 **PEDIDOS**
1. Clique em **"Pedidos"** no menu lateral
2. Deve aparecer o sistema Kanban
3. Teste:
   - Criar novo pedido
   - Mover pedido entre colunas
   - Visualizar detalhes do pedido

#### 💰 **FINANCEIRO**
1. Clique em **"Financeiro"** no menu lateral
2. Deve aparecer:
   - Resumo financeiro
   - Transações recentes
   - Gráficos de receitas/despesas

#### 📊 **RELATÓRIOS**
1. Clique em **"Relatórios"** no menu lateral
2. Teste:
   - Gerar relatório de vendas
   - Exportar relatório
   - Filtrar por período

#### 🛒 **VENDAS**
1. Clique em **"Vendas"** no menu lateral
2. Teste:
   - Adicionar produtos ao carrinho
   - Selecionar cliente
   - Finalizar venda

#### 📱 **REDES SOCIAIS**
1. Clique em **"Redes Sociais"** no menu lateral
2. Teste:
   - Criar novo post
   - Agendar postagem
   - Enviar mensagem WhatsApp

#### 📄 **NOTAS FISCAIS**
1. Clique em **"Notas Fiscais"** no menu lateral
2. Teste:
   - Emitir nova nota fiscal
   - Visualizar notas existentes

## 🆘 PROBLEMAS COMUNS E SOLUÇÕES

### Erro: "Failed to fetch"
- Verifique se o backend está rodando na porta 3001
- Verifique se as URLs no .env estão corretas

### Erro: "Permission denied"
- Execute o SQL para promover seu usuário a admin
- Verifique se está logado no sistema

### Erro: "Network error"
- Verifique se não há conflito de portas
- Tente reiniciar o servidor

### Página em branco
- Verifique o console do navegador (F12)
- Verifique se há erros no terminal

## 📞 PRECISA DE AJUDA?

**Me diga qual etapa você está e qual erro aparece!**
- Está no Passo 3, 4, 5 ou 6?
- Qual mensagem de erro aparece?
- O que você está tentando fazer?