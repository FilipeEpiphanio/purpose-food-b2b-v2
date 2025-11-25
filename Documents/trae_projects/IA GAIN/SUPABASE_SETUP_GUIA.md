# 🚀 GUIA DE CONFIGURAÇÃO DO SUPABASE - PURPOSE FOOD

## Passo 1: Criar Conta e Projeto

1. Acesse: https://supabase.com
2. Clique em "Start your project"
3. Faça login (pode usar GitHub ou email)
4. Clique em "New Project"
5. Configure:
   - **Nome:** purposefood
   - **Senha do banco:** Crie uma senha forte e anote!
   - **Região:** Escolha São Paulo (se disponível) ou US East

## Passo 2: Obter Credenciais

1. Aguarde o projeto ser criado (2-3 minutos)
2. Vá para **Settings** (engrenagem no canto inferior)
3. Clique em **API**
4. Copie estas informações:
   - **URL:** `https://[seu-id].supabase.co`
   - **anon key:** (chave pública)
   - **service_role key:** (chave secreta)

## Passo 3: Ativar Autenticação

1. No painel lateral, clique em **Authentication**
2. Vá para **Providers**
3. Ative **Email**
4. Configure:
   - Confirm email: DISABLED (para testes)
   - Secure email change: DISABLED (para testes)

## Passo 4: Configurar Arquivo .env

Substitua o arquivo `.env` com suas credenciais reais:

```env
# Frontend Configuration
VITE_SUPABASE_URL=https://SEU-ID.supabase.co
VITE_SUPABASE_ANON_KEY=sua-chave-anon-aqui
VITE_API_URL=http://localhost:3001/api

# Backend Configuration
SUPABASE_URL=https://SEU-ID.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key-aqui
FRONTEND_URL=http://localhost:5173
PORT=3001
```

## Passo 5: Criar Tabelas no Banco

1. No painel do Supabase, vá para **SQL Editor**
2. Cole e execute este SQL:

```sql
-- Criar tabela de perfis
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Trigger para criar perfil automaticamente
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email)
  VALUES (new.id, new.email);
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Permissões
GRANT ALL ON profiles TO anon, authenticated;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Políticas de segurança
CREATE POLICY "Ver próprio perfil" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Ver todos perfis (admin)" ON profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Criar tabelas do sistema
CREATE TABLE IF NOT EXISTS products (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  cost DECIMAL(10,2) NOT NULL,
  stock INTEGER NOT NULL DEFAULT 0,
  min_stock INTEGER NOT NULL DEFAULT 0,
  unit TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  address TEXT,
  cpf_cnpj TEXT,
  type TEXT NOT NULL DEFAULT 'individual',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  total_amount DECIMAL(10,2) NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  payment_method TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Permissões para tabelas
GRANT ALL ON products TO anon, authenticated;
GRANT ALL ON customers TO anon, authenticated;
GRANT ALL ON orders TO anon, authenticated;

-- Ativar RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (permitir todas as operações para testes)
CREATE POLICY "Permitir tudo em produtos" ON products
  FOR ALL USING (true);

CREATE POLICY "Permitir tudo em clientes" ON customers
  FOR ALL USING (true);

CREATE POLICY "Permitir tudo em pedidos" ON orders
  FOR ALL USING (true);
```

## Passo 6: Testar o Sistema

1. Reinicie o servidor: `npm run dev`
2. Acesse: http://localhost:5173
3. Clique em "Criar conta"
4. Registre-se com seu email
5. Faça login

## Passo 7: Tornar-se Administrador

Depois de se registrar, execute este SQL (substitua pelo seu email):

```sql
UPDATE profiles SET role = 'admin' WHERE email = 'seu-email@cadastro.com';
```

## 🎯 PRONTO!

Seu sistema Purpose Food está totalmente configurado e funcionando!

**Precisa de ajuda?** Me diga em qual passo você está e eu te ajudo!