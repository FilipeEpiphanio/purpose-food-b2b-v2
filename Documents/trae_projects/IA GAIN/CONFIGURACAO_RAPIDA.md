# ✅ GUIA RÁPIDO - CONFIGURAÇÃO SUPABASE COMPLETA

## 🎯 SEU PROJETO SUPABASE ESTÁ CONFIGURADO!

**URL do Projeto:** https://xqsocdvvvbgdgrezoqlf.supabase.co
**Status:** ✅ Credenciais configuradas no .env

## 📋 PRÓXIMOS PASSOS:

### 1️⃣ CONFIGURAR O BANCO DE DADOS

1. **Acesse seu projeto Supabase:**
   - Vá para: https://supabase.com
   - Clique em seu projeto "purposefood"

2. **Execute o SQL de configuração:**
   - No painel lateral, clique em **"SQL Editor"**
   - Clique em **"New Query"**
   - Copie TODO o conteúdo do arquivo `setup_database_completo.sql`
   - Cole no editor SQL
   - Clique em **"RUN"** ou pressione Ctrl+Enter

3. **Verifique se deu certo:**
   - Você verá uma tabela com os totais de registros criados
   - Se aparecer "Query executed successfully" ✅ está tudo certo!

### 2️⃣ ATIVAR AUTENTICAÇÃO POR EMAIL

1. **No painel lateral, clique em "Authentication"**
2. **Clique em "Providers"**
3. **Ative "Email" clicando no toggle**
4. **Configure assim:**
   - Confirm email: **DISABLED** (para testes)
   - Secure email change: **DISABLED** (para testes)
   - Clique em **"Save"**

### 3️⃣ REINICIAR O SISTEMA

1. **Volte para o terminal e reinicie:**
   ```bash
   # Pare o servidor atual (Ctrl+C)
   npm run dev
   ```

2. **Acesse o sistema:**
   - URL: http://localhost:5173
   - Clique em **"Criar conta"**
   - Registre-se com seu email

### 4️⃣ TORNE-SE ADMINISTRADOR

Depois de se registrar, execute este SQL no Supabase:

```sql
-- Substitua 'seu-email@exemplo.com' pelo email que você usou para se cadastrar
UPDATE profiles SET role = 'admin' WHERE email = 'seu-email@exemplo.com';
```

## 🧪 TESTAR O SISTEMA

### **Login de Teste (após se registrar):**
- **Email:** Seu email de cadastro
- **Senha:** Sua senha de cadastro

### **Funcionalidades para testar:**
- ✅ Dashboard com métricas
- ✅ Cadastro de produtos
- ✅ Gestão de clientes
- ✅ Criação de pedidos
- ✅ Sistema financeiro
- ✅ Relatórios
- ✅ Integração com redes sociais
- ✅ Sistema de notas fiscais

## 📊 DADOS DE EXEMPLO JÁ CRIADOS

### **Produtos:**
- Pão de Queijo Artesanal - R$ 25,90
- Coxinha de Frango com Catupiry - R$ 8,50
- Bolo de Chocolate Meio Amargo - R$ 45,00
- Brigadeiro Gourmet - R$ 3,50
- Quiche de Alho poró - R$ 35,00
- Torta de Limão Siciliano - R$ 42,00

### **Clientes:**
- Maria Silva, João Oliveira, Padaria Central, Café Boutique, Ana Costa

### **Posts Sociais:**
- Posts no Instagram, Facebook e WhatsApp já criados

## 🆘 SE PRECISAR DE AJUDA

**Erro comum:** Se aparecer "permission denied" ao acessar alguma página:
1. Verifique se você está logado
2. Verifique se foi promovido a admin (Passo 4)
3. Verifique se reiniciou o servidor após configurar o .env

**Suporte:** Me diga qual erro aparece e eu te ajudo!