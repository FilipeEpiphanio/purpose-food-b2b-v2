-- Adicionar coluna ingredients à tabela products
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS ingredients TEXT;

-- Adicionar coluna delivery_address à tabela orders
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS delivery_address TEXT;

-- Adicionar coluna customer_name à tabela orders (também parece estar faltando baseado nos erros)
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS customer_name TEXT;

-- Adicionar coluna order_type à tabela orders (para diferenciar delivery de pickup)
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS order_type TEXT DEFAULT 'pickup' CHECK (order_type IN ('delivery', 'pickup', 'in_store'));

-- Adicionar coluna scheduled_date à tabela orders (para agendamentos)
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS scheduled_date TIMESTAMP WITH TIME ZONE;

-- Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_orders_delivery_address ON orders(delivery_address);
CREATE INDEX IF NOT EXISTS idx_orders_customer_name ON orders(customer_name);
CREATE INDEX IF NOT EXISTS idx_orders_order_type ON orders(order_type);
CREATE INDEX IF NOT EXISTS idx_products_ingredients ON products(ingredients);