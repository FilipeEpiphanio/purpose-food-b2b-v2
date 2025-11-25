-- 🚀 SQL CORRIGIDO - PURPOSE FOOD
-- Execute este SQL no SQL Editor do seu projeto Supabase
-- URL do seu projeto: https://xqsocdvvvbgdgrezoqlf.supabase.co

-- ==================================================
-- 1. CONFIGURAÇÃO DA AUTENTICAÇÃO E PERFIS
-- ==================================================

-- Criar tabela de perfis de usuário
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  role TEXT DEFAULT 'user',
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Criar trigger para criar perfil automaticamente quando usuário se registra
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (new.id, new.email, new.raw_user_meta_data->>'full_name');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Criar trigger que executa após inserção de novo usuário
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

-- ==================================================
-- 2. TABELAS DO SISTEMA PURPOSE FOOD
-- ==================================================

-- Tabela de produtos
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
  image_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabela de clientes
CREATE TABLE IF NOT EXISTS customers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  address TEXT,
  cpf_cnpj TEXT,
  type TEXT NOT NULL DEFAULT 'individual',
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Criar sequência para números de pedido (ANTES da tabela orders)
CREATE SEQUENCE IF NOT EXISTS order_seq START 1000;

-- Tabela de pedidos
CREATE TABLE IF NOT EXISTS orders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  order_number TEXT UNIQUE DEFAULT 'ORD' || TO_CHAR(NOW(), 'YYYYMMDD') || LPAD(NEXTVAL('order_seq')::TEXT, 4, '0'),
  total_amount DECIMAL(10,2) NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  payment_method TEXT,
  payment_status TEXT DEFAULT 'pending',
  notes TEXT,
  delivery_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabela de itens do pedido
CREATE TABLE IF NOT EXISTS order_items (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  quantity INTEGER NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabela de transações financeiras
CREATE TABLE IF NOT EXISTS transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  order_id UUID REFERENCES orders(id),
  type TEXT NOT NULL, -- 'income', 'expense'
  category TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  description TEXT,
  payment_method TEXT,
  transaction_date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabela de notas fiscais
CREATE TABLE IF NOT EXISTS invoices (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  order_id UUID REFERENCES orders(id),
  customer_id UUID REFERENCES customers(id),
  invoice_number TEXT UNIQUE,
  series TEXT DEFAULT '1',
  total_amount DECIMAL(10,2) NOT NULL,
  tax_amount DECIMAL(10,2) DEFAULT 0,
  status TEXT DEFAULT 'pending',
  issue_date DATE,
  due_date DATE,
  xml_content TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabela de posts de redes sociais
CREATE TABLE IF NOT EXISTS social_posts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  platform TEXT NOT NULL, -- 'instagram', 'facebook', 'whatsapp'
  content TEXT NOT NULL,
  image_url TEXT,
  status TEXT DEFAULT 'draft', -- 'draft', 'scheduled', 'published', 'failed'
  scheduled_date TIMESTAMP WITH TIME ZONE,
  published_date TIMESTAMP WITH TIME ZONE,
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  shares_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tabela de mensagens do WhatsApp
CREATE TABLE IF NOT EXISTS whatsapp_messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  message TEXT NOT NULL,
  status TEXT DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'failed'
  sent_date TIMESTAMP WITH TIME ZONE,
  response_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- ==================================================
-- 3. CONFIGURAÇÃO DE PERMISSÕES E SEGURANÇA
-- ==================================================

-- Conceder permissões para todas as tabelas
GRANT ALL ON products TO anon, authenticated;
GRANT ALL ON customers TO anon, authenticated;
GRANT ALL ON orders TO anon, authenticated;
GRANT ALL ON order_items TO anon, authenticated;
GRANT ALL ON transactions TO anon, authenticated;
GRANT ALL ON invoices TO anon, authenticated;
GRANT ALL ON social_posts TO anon, authenticated;
GRANT ALL ON whatsapp_messages TO anon, authenticated;
GRANT ALL ON order_seq TO anon, authenticated;

-- Ativar Row Level Security (RLS) em todas as tabelas
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;

-- Criar políticas de segurança (permissivas para testes)
CREATE POLICY "Permitir todas operações em produtos" ON products
  FOR ALL USING (true);

CREATE POLICY "Permitir todas operações em clientes" ON customers
  FOR ALL USING (true);

CREATE POLICY "Permitir todas operações em pedidos" ON orders
  FOR ALL USING (true);

CREATE POLICY "Permitir todas operações em itens do pedido" ON order_items
  FOR ALL USING (true);

CREATE POLICY "Permitir todas operações em transações" ON transactions
  FOR ALL USING (true);

CREATE POLICY "Permitir todas operações em notas fiscais" ON invoices
  FOR ALL USING (true);

CREATE POLICY "Permitir todas operações em posts sociais" ON social_posts
  FOR ALL USING (true);

CREATE POLICY "Permitir todas operações em mensagens WhatsApp" ON whatsapp_messages
  FOR ALL USING (true);

-- ==================================================
-- 4. DADOS INICIAIS DE EXEMPLO
-- ==================================================

-- Inserir categorias de produtos de exemplo
INSERT INTO products (name, category, price, cost, stock, min_stock, unit, description, status) VALUES
  ('Pão de Queijo Artesanal', 'Salgados', 25.90, 15.00, 50, 10, 'un', 'Pão de queijo tradicional mineiro, massa artesanal', 'active'),
  ('Coxinha de Frango com Catupiry', 'Salgados', 8.50, 4.20, 30, 15, 'un', 'Coxinha cremosa com frango desfiado e catupiry', 'active'),
  ('Bolo de Chocolate Meio Amargo', 'Doces', 45.00, 22.00, 15, 5, 'kg', 'Bolo de chocolate premium com cobertura de ganache', 'active'),
  ('Brigadeiro Gourmet Tradicional', 'Doces', 3.50, 1.20, 100, 20, 'un', 'Brigadeiro artesanal com chocolate belga', 'active'),
  ('Quiche de Alho poró', 'Salgados', 35.00, 18.00, 12, 5, 'kg', 'Quiche leve e saborosa, massa folhada crocante', 'active'),
  ('Torta de Limão Siciliano', 'Doces', 42.00, 20.00, 8, 3, 'kg', 'Torta ácida com base de biscoito e merengue', 'active');

-- Inserir clientes de exemplo
INSERT INTO customers (name, email, phone, address, cpf_cnpj, type, notes) VALUES
  ('Maria Silva', 'maria.silva@email.com', '(11) 98765-4321', 'Rua das Flores, 123 - São Paulo/SP', '123.456.789-00', 'individual', 'Cliente VIP, preferência por doces'),
  ('João Oliveira', 'joao.oliveira@email.com', '(11) 99876-5432', 'Av. Paulista, 1000 - São Paulo/SP', '987.654.321-00', 'individual', 'Pedidos frequentes para eventos corporativos'),
  ('Padaria Central', 'contato@padariacentral.com.br', '(11) 3234-5678', 'Rua da Padaria, 456 - São Paulo/SP', '12.345.678/0001-90', 'corporate', 'Cliente B2B, pedidos semanais'),
  ('Café Boutique', 'admin@cafeboutique.com.br', '(11) 3344-5566', 'Alameda Santos, 789 - São Paulo/SP', '98.765.432/0001-10', 'corporate', 'Parceiro para fornecimento de salgados'),
  ('Ana Costa', 'ana.costa@email.com', '(11) 91234-5678', 'Rua Augusta, 321 - São Paulo/SP', '111.222.333-44', 'individual', 'Cliente nova, interessada em opções saudáveis');

-- Inserir posts sociais de exemplo
INSERT INTO social_posts (platform, content, status, likes_count, comments_count, shares_count) VALUES
  ('instagram', '🍞 Nosso pão de queijo artesanal está mais cremoso do que nunca! Feito com ingredientes selecionados e muito amor ❤️ #paodequeijo #artesanal #purposefood', 'published', 45, 12, 8),
  ('facebook', '🎂 Bolo de chocolate meio amargo - o queridinho da casa! Perfeito para comemorações especiais. Encomende pelo WhatsApp (11) 98765-4321', 'published', 32, 8, 5),
  ('whatsapp', '☕ Quiche de alho poró - ideal para o almoço! Massa crocante e recheio leve. Faça seu pedido!', 'published', 0, 0, 0);

-- Inserir mensagens WhatsApp de exemplo
INSERT INTO whatsapp_messages (customer_name, phone, message, status) VALUES
  ('Carlos Mendes', '(11) 94567-8901', 'Olá, gostaria de fazer um pedido de 50 coxinhas para sexta-feira', 'pending'),
  ('Patricia Lima', '(11) 92345-6789', 'Bom dia! Vocês fazem bolo de aniversário temático?', 'pending'),
  ('Roberto Alves', '(11) 93456-7890', 'Quero encomendar a quiche para semana que vem', 'pending');

-- Criar um pedido de exemplo
INSERT INTO orders (customer_id, total_amount, status, payment_method, payment_status, delivery_date, notes) VALUES
  ((SELECT id FROM customers LIMIT 1), 127.50, 'delivered', 'credit_card', 'paid', CURRENT_DATE + INTERVAL '7 days', 'Pedido para festa de aniversário');

-- Adicionar itens ao pedido
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
  ((SELECT id FROM orders LIMIT 1), (SELECT id FROM products WHERE name = 'Pão de Queijo Artesanal' LIMIT 1), 10, 25.90, 259.00),
  ((SELECT id FROM orders LIMIT 1), (SELECT id FROM products WHERE name = 'Brigadeiro Gourmet Tradicional' LIMIT 1), 20, 3.50, 70.00);

-- Atualizar valor total do pedido
UPDATE orders 
SET total_amount = (SELECT SUM(total_price) FROM order_items WHERE order_id = orders.id)
WHERE id = (SELECT id FROM orders LIMIT 1);

-- Criar transação financeira para o pedido
INSERT INTO transactions (order_id, type, category, amount, description, payment_method, transaction_date) VALUES
  ((SELECT id FROM orders LIMIT 1), 'income', 'sales', 127.50, 'Venda de produtos para festa', 'credit_card', CURRENT_DATE);

-- ==================================================
-- 5. VERIFICAÇÃO DA INSTALAÇÃO
-- ==================================================

-- Verificar se tudo foi criado corretamente
SELECT 
  'profiles' as tabela,
  COUNT(*) as total_registros
FROM profiles
UNION ALL
SELECT 
  'products' as tabela,
  COUNT(*) as total_registros
FROM products
UNION ALL
SELECT 
  'customers' as tabela,
  COUNT(*) as total_registros
FROM customers
UNION ALL
SELECT 
  'orders' as tabela,
  COUNT(*) as total_registros
FROM orders
UNION ALL
SELECT 
  'social_posts' as tabela,
  COUNT(*) as total_registros
FROM social_posts
UNION ALL
SELECT 
  'whatsapp_messages' as tabela,
  COUNT(*) as total_registros
FROM whatsapp_messages;