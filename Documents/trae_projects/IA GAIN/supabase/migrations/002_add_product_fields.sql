-- Adicionar novos campos à tabela de produtos
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS image_url TEXT,
ADD COLUMN IF NOT EXISTS ingredients TEXT[],
ADD COLUMN IF NOT EXISTS preparation_time NUMERIC(4,1),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Atualizar produtos existentes para ter o novo campo
UPDATE products SET is_active = true WHERE is_active IS NULL;

-- Criar índice para melhorar a busca por ingredientes
CREATE INDEX IF NOT EXISTS idx_products_ingredients ON products USING GIN (ingredients);

-- Adicionar comentários para documentação
COMMENT ON COLUMN products.image_url IS 'URL da imagem do produto';
COMMENT ON COLUMN products.ingredients IS 'Lista de ingredientes do produto';
COMMENT ON COLUMN products.preparation_time IS 'Tempo de preparo em horas';
COMMENT ON COLUMN products.is_active IS 'Indica se o produto está ativo para venda';

-- Verificar se a coluna status já existe e sincronizar com is_active
-- Se o produto estiver inativo no campo status, também inativar no is_active
UPDATE products SET is_active = false WHERE status = 'inactive';
UPDATE products SET is_active = true WHERE status = 'active';