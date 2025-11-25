-- Adicionar coluna is_active na tabela products
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Atualizar produtos existentes para ter is_active = true se status = 'active'
UPDATE products SET is_active = true WHERE status = 'active';
UPDATE products SET is_active = false WHERE status = 'inactive';

-- Criar índice para melhorar performance
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);