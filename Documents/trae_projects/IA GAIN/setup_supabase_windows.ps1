# Script de Configuração do Supabase - Windows
# Execute este script no PowerShell

Write-Host "🚀 CONFIGURADOR DO SUPABASE - PURPOSE FOOD" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Instruções
Write-Host "📋 INSTRUÇÕES PARA OBTER AS CREDENCIAIS:" -ForegroundColor Yellow
Write-Host "1. Acesse: https://supabase.com" -ForegroundColor White
Write-Host "2. Vá para seu projeto 'purposefood'" -ForegroundColor White
Write-Host "3. Clique em 'Settings' (engrenagem no canto inferior)" -ForegroundColor White
Write-Host "4. Clique em 'API'" -ForegroundColor White
Write-Host "5. Copie as informações solicitadas abaixo" -ForegroundColor White
Write-Host ""

# Solicitar credenciais
Write-Host "🔑 CREDENCIAIS DO SUPABASE:" -ForegroundColor Cyan
$supabaseUrl = Read-Host "🔗 URL do Projeto (ex: https://xyz.supabase.co)"
$supabaseAnonKey = Read-Host "🔑 Chave Anônima (anon key)"
$supabaseServiceKey = Read-Host "🔐 Service Role Key"

Write-Host ""
Write-Host "💳 CONFIGURAÇÕES OPCIONAIS DO STRIPE:" -ForegroundColor Cyan
Write-Host "(Pressione Enter para pular - você pode configurar depois)" -ForegroundColor Gray
$stripePublishableKey = Read-Host "💳 Stripe Publishable Key (opcional)"
$stripeSecretKey = Read-Host "🔐 Stripe Secret Key (opcional)"

# Criar arquivo .env
$envContent = @"
# Supabase Configuration (Frontend)
VITE_SUPABASE_URL=$supabaseUrl
VITE_SUPABASE_ANON_KEY=$supabaseAnonKey

# Stripe Configuration (Frontend)
VITE_STRIPE_PUBLISHABLE_KEY=$($stripePublishableKey -or "pk_test_your-stripe-publishable-key")

# API Configuration (Frontend)
VITE_API_URL=http://localhost:3001/api

# Backend Configuration
SUPABASE_URL=$supabaseUrl
SUPABASE_SERVICE_ROLE_KEY=$supabaseServiceKey
STRIPE_SECRET_KEY=$($stripeSecretKey -or "sk_test_your-stripe-secret-key")
FRONTEND_URL=http://localhost:5173
PORT=3001
"@

# Salvar arquivo .env
$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host ""
Write-Host "✅ ARQUIVO .ENV CRIADO COM SUCESSO!" -ForegroundColor Green
Write-Host ""

# Criar SQL para configuração do banco
$sqlContent = @"
-- SQL PARA CONFIGURAR O BANCO DE DADOS
-- Execute este SQL no SQL Editor do Supabase

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
RETURNS trigger AS \$\$
BEGIN
  INSERT INTO public.profiles (id, email)
  VALUES (new.id, new.email);
  RETURN new;
END;
\$\$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Conceder permissões
GRANT ALL ON profiles TO anon, authenticated;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Criar políticas de segurança
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
"@

# Salvar SQL
$sqlContent | Out-File -FilePath "setup_database.sql" -Encoding UTF8

Write-Host "📋 SQL PARA CONFIGURAR O BANCO SALVO EM: setup_database.sql" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎯 PRÓXIMOS PASSOS:" -ForegroundColor Green
Write-Host "1. Copie o conteúdo do arquivo 'setup_database.sql'" -ForegroundColor White
Write-Host "2. No painel do Supabase, vá para 'SQL Editor'" -ForegroundColor White
Write-Host "3. Cole o SQL e clique em 'RUN'" -ForegroundColor White
Write-Host "4. Reinicie o servidor: npm run dev" -ForegroundColor White
Write-Host "5. Acesse: http://localhost:5173" -ForegroundColor White
Write-Host "6. Clique em 'Criar conta' para se registrar" -ForegroundColor White
Write-Host ""
Write-Host "💡 PARA SE TORNAR ADMINISTRADOR:" -ForegroundColor Cyan
Write-Host "Após se registrar, execute este SQL no Supabase:" -ForegroundColor White
Write-Host "UPDATE profiles SET role = 'admin' WHERE email = 'seu-email@exemplo.com';" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ CONFIGURAÇÃO CONCLUÍDA!" -ForegroundColor Green