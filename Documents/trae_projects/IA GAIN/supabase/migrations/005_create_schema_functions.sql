-- Criar função para executar SQL dinamicamente
CREATE OR REPLACE FUNCTION public.exec_sql(sql_text text)
RETURNS void AS $$
BEGIN
  EXECUTE sql_text;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions to use the function
GRANT EXECUTE ON FUNCTION public.exec_sql(text) TO anon, authenticated;

-- Criar função para adicionar coluna se não existir
CREATE OR REPLACE FUNCTION public.add_column_if_not_exists(
  table_name text,
  column_name text,
  column_definition text
)
RETURNS void AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = table_name 
    AND column_name = column_name
  ) THEN
    EXECUTE format('ALTER TABLE public.%I ADD COLUMN %I %s', 
                   table_name, column_name, column_definition);
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.add_column_if_not_exists(text, text, text) TO anon, authenticated;

-- Criar função para criar tabela se não existir
CREATE OR REPLACE FUNCTION public.create_table_if_not_exists(
  table_name text,
  table_definition text
)
RETURNS void AS $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = table_name
  ) THEN
    EXECUTE format('CREATE TABLE public.%I (%s)', table_name, table_definition);
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.create_table_if_not_exists(text, text) TO anon, authenticated;

-- Agora aplicar as correções necessárias
-- 1. Adicionar coluna order_date na tabela orders
SELECT public.add_column_if_not_exists('orders', 'order_date', 'DATE DEFAULT CURRENT_DATE');

-- 2. Adicionar coluna status na tabela customers  
SELECT public.add_column_if_not_exists('customers', 'status', "TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked'))");

-- 3. Criar tabela financial_records
SELECT public.create_table_if_not_exists('financial_records', `
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('revenue', 'expense', 'profit')),
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  reference_month INTEGER NOT NULL CHECK (reference_month >= 1 AND reference_month <= 12),
  reference_year INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
`);

-- 4. Adicionar trigger para updated_at na tabela financial_records
CREATE TRIGGER IF NOT EXISTS handle_financial_records_updated_at
  BEFORE UPDATE ON public.financial_records
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- 5. Adicionar outras colunas necessárias
SELECT public.add_column_if_not_exists('orders', 'delivery_date', 'TIMESTAMP WITH TIME ZONE');
SELECT public.add_column_if_not_exists('products', 'cost_price', 'DECIMAL(10,2) DEFAULT 0');

-- 6. Criar índices
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);
CREATE INDEX IF NOT EXISTS idx_financial_records_month_year ON public.financial_records(reference_month, reference_year);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON public.products(is_active);

-- 7. Habilitar RLS na tabela financial_records
ALTER TABLE public.financial_records ENABLE ROW LEVEL SECURITY;

-- 8. Criar políticas para financial_records
CREATE POLICY "Authenticated users can view financial records" ON public.financial_records
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can insert financial records" ON public.financial_records
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can update financial records" ON public.financial_records
  FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can delete financial records" ON public.financial_records
  FOR DELETE USING (auth.role() = 'authenticated');

-- 9. Grant permissions
GRANT ALL ON public.financial_records TO anon, authenticated;
GRANT ALL ON SEQUENCE public.financial_records_id_seq TO anon, authenticated;