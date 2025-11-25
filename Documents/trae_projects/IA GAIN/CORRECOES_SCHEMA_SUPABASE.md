# 🛠️ Correções de Schema do Banco de Dados

Este arquivo contém os comandos SQL necessários para corrigir os erros de schema no Supabase.

## 📋 Comandos para Executar no Supabase Dashboard

1. **Acesse o seu Supabase Dashboard**: https://app.supabase.com
2. **Vá para SQL Editor**: https://app.supabase.com/project/_/sql
3. **Execute os comandos abaixo um por um**:

### 1. Adicionar coluna order_date na tabela orders
```sql
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS order_date DATE DEFAULT CURRENT_DATE;
```

### 2. Adicionar coluna status na tabela customers
```sql
ALTER TABLE public.customers 
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked'));
```

### 3. Criar tabela financial_records
```sql
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
```

### 4. Criar função handle_updated_at (se não existir)
```sql
-- Criar função handle_updated_at antes de criar o trigger
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
  END IF;
END $$;
```

### 5. Adicionar trigger para updated_at na tabela financial_records
```sql
-- Criar trigger apenas se não existir (versão compatível)
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
  END IF;
END $$;
```

**OU use o script completo abaixo que contém todas as correções:**

### 🚀 Script Completo (Recomendado)
Copie e cole todo o conteúdo do arquivo `supabase/migrations/006_fix_schema_final.sql` no SQL Editor do Supabase.

### 6. Adicionar colunas adicionais necessárias
```sql
-- Adicionar delivery_date em orders
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS delivery_date TIMESTAMP WITH TIME ZONE;

-- Adicionar cost_price em products
ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS cost_price DECIMAL(10,2) DEFAULT 0;
```

### 6. Criar índices para melhorar performance
```sql
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);
CREATE INDEX IF NOT EXISTS idx_financial_records_month_year ON public.financial_records(reference_month, reference_year);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON public.products(is_active);
```

### 8. Habilitar RLS na tabela financial_records
```sql
ALTER TABLE public.financial_records ENABLE ROW LEVEL SECURITY;
```

### 9. Criar políticas para financial_records
```sql
CREATE POLICY "Authenticated users can view financial records" ON public.financial_records
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can insert financial records" ON public.financial_records
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can update financial records" ON public.financial_records
  FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can delete financial records" ON public.financial_records
  FOR DELETE USING (auth.role() = 'authenticated');
```

### 10. Grant permissions
```sql
GRANT ALL ON public.financial_records TO anon, authenticated;
GRANT ALL ON SEQUENCE public.financial_records_id_seq TO anon, authenticated;
```

## ✅ Verificação

Após executar todos os comandos, você pode verificar se as correções foram aplicadas:

```sql
-- Verificar se as colunas foram adicionadas
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('orders', 'customers') 
AND column_name IN ('order_date', 'status');

-- Verificar se a tabela financial_records foi criada
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'financial_records';
```

## 🔄 Reinicialização

Após executar todos os comandos:
1. **Reinicie o servidor backend**: `npm run server:dev`
2. **Atualize a página do dashboard**
3. **Os erros devem estar resolvidos!**

## 🆘 Se ainda houver problemas

Se os erros persistirem após executar estes comandos:
1. Verifique os logs do navegador (F12 → Console)
2. Verifique se as colunas foram realmente criadas
3. Certifique-se de que as permissões foram aplicadas corretamente
4. Reinicie o servidor backend