-- 🛠️ Script de Correção de Schema - Purpose Food
-- Execute estes comandos no SQL Editor do Supabase (https://app.supabase.com/project/_/sql)

-- 1. Adicionar coluna order_date na tabela orders (se não existir)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'orders' 
    AND column_name = 'order_date'
  ) THEN
    ALTER TABLE public.orders ADD COLUMN order_date DATE DEFAULT CURRENT_DATE;
    RAISE NOTICE '✅ Coluna order_date adicionada com sucesso!';
  ELSE
    RAISE NOTICE 'ℹ️ Coluna order_date já existe';
  END IF;
END $$;

-- 2. Adicionar coluna status na tabela customers (se não existir)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'customers' 
    AND column_name = 'status'
  ) THEN
    ALTER TABLE public.customers ADD COLUMN status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked'));
    RAISE NOTICE '✅ Coluna status adicionada com sucesso!';
  ELSE
    RAISE NOTICE 'ℹ️ Coluna status já existe';
  END IF;
END $$;

-- 3. Criar tabela financial_records (se não existir)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'financial_records'
  ) THEN
    CREATE TABLE public.financial_records (
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
    RAISE NOTICE '✅ Tabela financial_records criada com sucesso!';
  ELSE
    RAISE NOTICE 'ℹ️ Tabela financial_records já existe';
  END IF;
END $$;

-- 4. Criar função handle_updated_at (se não existir)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_proc 
    WHERE proname = 'handle_updated_at'
    AND pronamespace = 'public'::regnamespace
  ) THEN
    CREATE OR REPLACE FUNCTION public.handle_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.updated_at = timezone('utc'::text, now());
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    RAISE NOTICE '✅ Função handle_updated_at criada com sucesso!';
  ELSE
    RAISE NOTICE 'ℹ️ Função handle_updated_at já existe';
  END IF;
END $$;

-- 5. Adicionar trigger para updated_at na tabela financial_records
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger 
    WHERE tgname = 'handle_financial_records_updated_at'
    AND tgrelid = 'public.financial_records'::regclass
  ) THEN
    CREATE TRIGGER handle_financial_records_updated_at
      BEFORE UPDATE ON public.financial_records
      FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
    RAISE NOTICE '✅ Trigger criado com sucesso!';
  ELSE
    RAISE NOTICE 'ℹ️ Trigger já existe';
  END IF;
END $$;

-- 6. Adicionar colunas adicionais necessárias
-- delivery_date em orders
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'orders' 
    AND column_name = 'delivery_date'
  ) THEN
    ALTER TABLE public.orders ADD COLUMN delivery_date TIMESTAMP WITH TIME ZONE;
    RAISE NOTICE '✅ Coluna delivery_date adicionada!';
  ELSE
    RAISE NOTICE 'ℹ️ Coluna delivery_date já existe';
  END IF;
END $$;

-- cost_price em products
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'products' 
    AND column_name = 'cost_price'
  ) THEN
    ALTER TABLE public.products ADD COLUMN cost_price DECIMAL(10,2) DEFAULT 0;
    RAISE NOTICE '✅ Coluna cost_price adicionada!';
  ELSE
    RAISE NOTICE 'ℹ️ Coluna cost_price já existe';
  END IF;
END $$;

-- 6. Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);
CREATE INDEX IF NOT EXISTS idx_financial_records_month_year ON public.financial_records(reference_month, reference_year);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON public.products(is_active);

-- 8. Habilitar RLS na tabela financial_records
ALTER TABLE public.financial_records ENABLE ROW LEVEL SECURITY;

-- 9. Criar políticas para financial_records
DO $$
BEGIN
  -- Política de SELECT
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'financial_records' 
    AND policyname = 'Authenticated users can view financial records'
  ) THEN
    CREATE POLICY "Authenticated users can view financial records" ON public.financial_records
      FOR SELECT USING (auth.role() = 'authenticated');
    RAISE NOTICE '✅ Política de SELECT criada!';
  END IF;

  -- Política de INSERT
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'financial_records' 
    AND policyname = 'Authenticated users can insert financial records'
  ) THEN
    CREATE POLICY "Authenticated users can insert financial records" ON public.financial_records
      FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    RAISE NOTICE '✅ Política de INSERT criada!';
  END IF;

  -- Política de UPDATE
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'financial_records' 
    AND policyname = 'Authenticated users can update financial records'
  ) THEN
    CREATE POLICY "Authenticated users can update financial records" ON public.financial_records
      FOR UPDATE USING (auth.role() = 'authenticated');
    RAISE NOTICE '✅ Política de UPDATE criada!';
  END IF;

  -- Política de DELETE
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = 'financial_records' 
    AND policyname = 'Authenticated users can delete financial records'
  ) THEN
    CREATE POLICY "Authenticated users can delete financial records" ON public.financial_records
      FOR DELETE USING (auth.role() = 'authenticated');
    RAISE NOTICE '✅ Política de DELETE criada!';
  END IF;
END $$;

-- 10. Grant permissions
GRANT ALL ON public.financial_records TO anon, authenticated;
GRANT ALL ON SEQUENCE public.financial_records_id_seq TO anon, authenticated;

-- 🎉 Finalização
RAISE NOTICE '🎉 Correções de schema aplicadas com sucesso!';
RAISE NOTICE '💡 Reinicie o servidor backend e atualize o dashboard!';