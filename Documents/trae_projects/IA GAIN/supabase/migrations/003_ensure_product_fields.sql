-- Verificar e garantir que todos os campos novos existem
-- Esta migration é idempotente (pode ser executada várias vezes)

-- Adicionar campos novos se não existirem
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='products' AND column_name='image_url') THEN
        ALTER TABLE products ADD COLUMN image_url TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='products' AND column_name='ingredients') THEN
        ALTER TABLE products ADD COLUMN ingredients TEXT[] DEFAULT '{}';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='products' AND column_name='preparation_time') THEN
        ALTER TABLE products ADD COLUMN preparation_time NUMERIC(4,1) DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='products' AND column_name='is_active') THEN
        ALTER TABLE products ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;
END $$;

-- Atualizar valores padrão
UPDATE products SET 
    ingredients = COALESCE(ingredients, '{}'),
    preparation_time = COALESCE(preparation_time, 0),
    is_active = COALESCE(is_active, true)
WHERE ingredients IS NULL OR preparation_time IS NULL OR is_active IS NULL;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- Adicionar comentários de documentação
COMMENT ON COLUMN products.image_url IS 'URL da imagem do produto';
COMMENT ON COLUMN products.ingredients IS 'Lista de ingredientes do produto';
COMMENT ON COLUMN products.preparation_time IS 'Tempo de preparo em horas';
COMMENT ON COLUMN products.is_active IS 'Indica se o produto está ativo para venda';

-- Verificar resultado
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'products' 
ORDER BY ordinal_position;