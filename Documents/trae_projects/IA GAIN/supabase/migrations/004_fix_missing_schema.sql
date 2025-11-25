-- Adicionar colunas faltantes na tabela orders
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS order_date DATE DEFAULT CURRENT_DATE;

-- Adicionar coluna status na tabela customers
ALTER TABLE public.customers 
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked'));

-- Criar tabela financial_records (que está faltando)
CREATE TABLE IF NOT EXISTS public.financial_records (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('revenue', 'expense', 'profit')),
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  reference_month INTEGER NOT NULL CHECK (reference_month >= 1 AND reference_month <= 12),
  reference_year INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Adicionar trigger para updated_at na tabela financial_records
CREATE TRIGGER handle_financial_records_updated_at
  BEFORE UPDATE ON public.financial_records
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- Adicionar colunas adicionais necessárias para o dashboard
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS delivery_date TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS cost_price DECIMAL(10,2) DEFAULT 0;

-- Criar índices para melhorar performance das queries do dashboard
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);
CREATE INDEX IF NOT EXISTS idx_financial_records_month_year ON public.financial_records(reference_month, reference_year);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON public.products(is_active);

-- Habilitar RLS na tabela financial_records
ALTER TABLE public.financial_records ENABLE ROW LEVEL SECURITY;

-- Criar políticas para financial_records
CREATE POLICY "Authenticated users can view financial records" ON public.financial_records
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can insert financial records" ON public.financial_records
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can update financial records" ON public.financial_records
  FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can delete financial records" ON public.financial_records
  FOR DELETE USING (auth.role() = 'authenticated');

-- Grant permissions para a nova tabela
GRANT ALL ON public.financial_records TO anon, authenticated;
GRANT ALL ON SEQUENCE public.financial_records_id_seq TO anon, authenticated;