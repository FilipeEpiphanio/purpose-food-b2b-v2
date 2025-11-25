import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';

dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function createFunctionsAndFixSchema() {
  console.log('🔄 Criando funções RPC e aplicando correções de schema...');
  
  try {
    // 1. Criar função exec_sql
    console.log('🔧 Criando função exec_sql...');
    const { error: execSqlError } = await supabase.rpc('exec_sql', {
      sql_text: `
        CREATE OR REPLACE FUNCTION public.exec_sql(sql_text text)
        RETURNS void AS $$
        BEGIN
          EXECUTE sql_text;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        
        GRANT EXECUTE ON FUNCTION public.exec_sql(text) TO anon, authenticated;
      `
    });
    
    if (execSqlError) {
      console.log('⚠️ Erro ao criar exec_sql (pode já existir):', execSqlError.message);
    } else {
      console.log('✅ Função exec_sql criada com sucesso!');
    }

    // 2. Criar função add_column_if_not_exists
    console.log('🔧 Criando função add_column_if_not_exists...');
    const { error: addColumnError } = await supabase.rpc('exec_sql', {
      sql_text: `
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
        
        GRANT EXECUTE ON FUNCTION public.add_column_if_not_exists(text, text, text) TO anon, authenticated;
      `
    });
    
    if (addColumnError) {
      console.log('⚠️ Erro ao criar add_column_if_not_exists (pode já existir):', addColumnError.message);
    } else {
      console.log('✅ Função add_column_if_not_exists criada com sucesso!');
    }

    // 3. Aplicar correções de schema usando as funções
    console.log('📅 Adicionando coluna order_date em orders...');
    const { error: orderDateError } = await supabase.rpc('add_column_if_not_exists', {
      table_name: 'orders',
      column_name: 'order_date',
      column_definition: 'DATE DEFAULT CURRENT_DATE'
    });
    
    if (orderDateError) {
      console.log('⚠️ Erro ao adicionar order_date:', orderDateError.message);
    } else {
      console.log('✅ Coluna order_date adicionada com sucesso!');
    }

    console.log('👥 Adicionando coluna status em customers...');
    const { error: customerStatusError } = await supabase.rpc('add_column_if_not_exists', {
      table_name: 'customers',
      column_name: 'status',
      column_definition: "TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked'))"
    });
    
    if (customerStatusError) {
      console.log('⚠️ Erro ao adicionar status:', customerStatusError.message);
    } else {
      console.log('✅ Coluna status adicionada com sucesso!');
    }

    // 4. Criar tabela financial_records
    console.log('💰 Criando tabela financial_records...');
    const { error: createTableError } = await supabase.rpc('exec_sql', {
      sql_text: `
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
        
        ALTER TABLE public.financial_records ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Authenticated users can view financial records" ON public.financial_records
          FOR SELECT USING (auth.role() = 'authenticated');
        
        CREATE POLICY "Authenticated users can insert financial records" ON public.financial_records
          FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        
        CREATE POLICY "Authenticated users can update financial records" ON public.financial_records
          FOR UPDATE USING (auth.role() = 'authenticated');
        
        CREATE POLICY "Authenticated users can delete financial records" ON public.financial_records
          FOR DELETE USING (auth.role() = 'authenticated');
        
        GRANT ALL ON public.financial_records TO anon, authenticated;
        GRANT ALL ON SEQUENCE public.financial_records_id_seq TO anon, authenticated;
        
        CREATE TRIGGER IF NOT EXISTS handle_financial_records_updated_at
          BEFORE UPDATE ON public.financial_records
          FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
      `
    });
    
    if (createTableError) {
      console.log('⚠️ Erro ao criar financial_records:', createTableError.message);
    } else {
      console.log('✅ Tabela financial_records criada com sucesso!');
    }

    // 5. Adicionar outras colunas necessárias
    console.log('📦 Adicionando colunas adicionais...');
    
    await supabase.rpc('add_column_if_not_exists', {
      table_name: 'orders',
      column_name: 'delivery_date',
      column_definition: 'TIMESTAMP WITH TIME ZONE'
    });
    
    await supabase.rpc('add_column_if_not_exists', {
      table_name: 'products',
      column_name: 'cost_price',
      column_definition: 'DECIMAL(10,2) DEFAULT 0'
    });

    console.log('✅ Correções de schema aplicadas com sucesso!');
    
  } catch (error: any) {
    console.error('❌ Erro ao aplicar correções:', error);
  }
}

// Executar o script
createFunctionsAndFixSchema().then(() => {
  console.log('🏁 Script de correção finalizado!');
  process.exit(0);
}).catch((error) => {
  console.error('💥 Erro fatal:', error);
  process.exit(1);
});