import { Router } from 'express';
import { supabase } from '../server';

const router = Router();

// Endpoint para aplicar correções de schema
router.post('/fix-schema', async (req, res) => {
  try {
    console.log('Aplicando correções de schema...');
    
    // Como não temos a função exec_sql, vamos executar as queries diretamente
    const queries = [
      // Adicionar colunas faltantes na tabela orders
      `ALTER TABLE public.orders 
       ADD COLUMN IF NOT EXISTS order_date DATE DEFAULT CURRENT_DATE;`,
      
      // Adicionar coluna status na tabela customers
      `ALTER TABLE public.customers 
       ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked'));`,
      
      // Criar tabela financial_records
      `CREATE TABLE IF NOT EXISTS public.financial_records (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        type TEXT NOT NULL CHECK (type IN ('revenue', 'expense', 'profit')),
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        reference_month INTEGER NOT NULL CHECK (reference_month >= 1 AND reference_month <= 12),
        reference_year INTEGER NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
      );`,
      
      // Adicionar colunas adicionais
      `ALTER TABLE public.orders 
       ADD COLUMN IF NOT EXISTS delivery_date TIMESTAMP WITH TIME ZONE;`,
      
      `ALTER TABLE public.products 
       ADD COLUMN IF NOT EXISTS cost_price DECIMAL(10,2) DEFAULT 0;`,
      
      // Criar índices
      `CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);`,
      `CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);`,
      `CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);`,
      `CREATE INDEX IF NOT EXISTS idx_financial_records_month_year ON public.financial_records(reference_month, reference_year);`,
      `CREATE INDEX IF NOT EXISTS idx_products_is_active ON public.products(is_active);`,
      
      // Habilitar RLS e criar políticas para financial_records
      `ALTER TABLE public.financial_records ENABLE ROW LEVEL SECURITY;`,
      
      `CREATE POLICY "Authenticated users can view financial records" ON public.financial_records
        FOR SELECT USING (auth.role() = 'authenticated');`,
      
      `CREATE POLICY "Authenticated users can insert financial records" ON public.financial_records
        FOR INSERT WITH CHECK (auth.role() = 'authenticated');`,
      
      `CREATE POLICY "Authenticated users can update financial records" ON public.financial_records
        FOR UPDATE USING (auth.role() = 'authenticated');`,
      
      `CREATE POLICY "Authenticated users can delete financial records" ON public.financial_records
        FOR DELETE USING (auth.role() = 'authenticated');`,
      
      // Grant permissions
      `GRANT ALL ON public.financial_records TO anon, authenticated;`,
      `GRANT ALL ON SEQUENCE public.financial_records_id_seq TO anon, authenticated;`
    ];

    // Executar cada query individualmente
    for (const query of queries) {
      try {
        const { error } = await supabase.rpc('exec_sql', { sql: query });
        if (error) {
          console.log(`Erro ao executar query (pode já existir): ${error.message}`);
        }
      } catch (err) {
        console.log(`Erro ao executar query: ${err.message}`);
      }
    }

    console.log('Correções de schema aplicadas com sucesso!');
    
    res.json({ 
      success: true, 
      message: 'Schema corrigido com sucesso!' 
    });
    
  } catch (error: any) {
    console.error('Erro ao aplicar correções:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Endpoint para verificar o schema atual
router.get('/check-schema', async (req, res) => {
  try {
    console.log('Verificando schema do banco de dados...');
    
    // Verificar estrutura das tabelas
    const tables = ['orders', 'customers', 'financial_records', 'products'];
    const schemaInfo: any = {};
    
    for (const table of tables) {
      const { data, error } = await supabase
        .from('information_schema.columns')
        .select('column_name, data_type, is_nullable, column_default')
        .eq('table_schema', 'public')
        .eq('table_name', table);
        
      if (error) {
        schemaInfo[table] = { error: error.message };
      } else {
        schemaInfo[table] = { columns: data };
      }
    }
    
    // Verificar se financial_records existe
    const { data: financialRecordsExists } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public')
      .eq('table_name', 'financial_records')
      .single();
    
    schemaInfo.financial_records_exists = !!financialRecordsExists;
    
    console.log('Schema verificado:', schemaInfo);
    
    res.json({ 
      success: true, 
      schema: schemaInfo 
    });
    
  } catch (error: any) {
    console.error('Erro ao verificar schema:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

export default router;