-- Adicionar campos de estoque à tabela products
ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS min_stock INTEGER DEFAULT 0;

-- Atualizar produtos existentes com valores padrão
UPDATE public.products 
SET stock_quantity = 10, min_stock = 5 
WHERE stock_quantity IS NULL;

-- Criar índice para consultas de estoque
CREATE INDEX IF NOT EXISTS idx_products_stock ON public.products(stock_quantity);
CREATE INDEX IF NOT EXISTS idx_products_min_stock ON public.products(min_stock);

-- Grant permissions
GRANT SELECT ON public.products TO anon;
GRANT ALL PRIVILEGES ON public.products TO authenticated;

-- Inserir alguns produtos de exemplo com estoque
INSERT INTO public.products (
    name, 
    category, 
    description, 
    price, 
    cost_price, 
    stock_quantity, 
    min_stock, 
    is_active
) VALUES 
    ('Bolo de Chocolate', 'Doces', 'Bolo de chocolate caseiro', 45.00, 25.00, 15, 5, true),
    ('Quiche de Frango', 'Salgados', 'Quiche de frango com legumes', 35.00, 20.00, 8, 3, true),
    ('Pão de Queijo', 'Salgados', 'Pão de queijo tradicional', 25.00, 12.00, 25, 10, true),
    ('Torta de Limão', 'Doces', 'Torta de limão merengada', 50.00, 28.00, 6, 2, true),
    ('Coxinha', 'Salgados', 'Coxinha de frango tradicional', 8.00, 4.50, 30, 15, true);