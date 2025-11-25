#!/bin/bash
# Script de configuração do Supabase para Purpose Food

echo "🚀 Configurador do Supabase para Purpose Food"
echo "=============================================="
echo ""
echo "📋 INSTRUÇÕES:"
echo "1. Acesse https://supabase.com e crie um projeto"
echo "2. Vá para Settings > API no painel do Supabase"
echo "3. Copie as credenciais solicitadas abaixo"
echo ""

# Solicitar credenciais ao usuário
read -p "🔗 URL do Projeto Supabase (ex: https://xyz.supabase.co): " SUPABASE_URL
read -p "🔑 Chave Anônima: " SUPABASE_ANON_KEY
read -p "🔐 Chave de Serviço: " SUPABASE_SERVICE_KEY
read -p "💳 Stripe Secret Key (opcional, pressione Enter para pular): " STRIPE_SECRET_KEY
read -p "💳 Stripe Publishable Key (opcional, pressione Enter para pular): " STRIPE_PUBLISHABLE_KEY

# Criar arquivo .env
cat > .env << EOF
# Supabase Configuration (Frontend)
VITE_SUPABASE_URL=$SUPABASE_URL
VITE_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY

# Stripe Configuration (Frontend)
VITE_STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY:-pk_test_your-stripe-publishable-key}

# API Configuration (Frontend)
VITE_API_URL=http://localhost:3001/api

# Backend Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_KEY
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-sk_test_your-stripe-secret-key}
FRONTEND_URL=http://localhost:5173
PORT=3001
EOF

echo ""
echo "✅ Arquivo .env criado com sucesso!"
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "1. Execute: npm run dev"
echo "2. Acesse: http://localhost:5173"
echo "3. Clique em 'Criar conta' para se registrar"
echo "4. Após se registrar, execute o SQL para criar o administrador"
echo ""
echo "📊 SQL para criar administrador (execute no SQL Editor do Supabase):"
echo "-- Copie e cole este SQL no Supabase após se registrar"
cat > setup_admin.sql << 'SQL'
-- Criar tabela de perfis de usuário
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Criar trigger para criar perfil automaticamente
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email)
  VALUES (new.id, new.email);
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Criar trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Conceder permissões
GRANT ALL ON profiles TO anon, authenticated;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Criar políticas de segurança
CREATE POLICY "Usuários podem ver próprio perfil" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Usuários podem atualizar próprio perfil" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Administradores podem ver todos perfis" ON profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );
SQL

cat setup_admin.sql
echo ""
echo "💡 Após se registrar no sistema, execute este comando para se tornar administrador:"
echo "UPDATE profiles SET role = 'admin' WHERE email = 'seu-email-de-cadastro';"