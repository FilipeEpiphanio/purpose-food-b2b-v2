import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function checkProductsColumns() {
  console.log('Verificando colunas da tabela products...');

  try {
    const { data: columns } = await supabase
      .from('information_schema.columns')
      .select('column_name, data_type, is_nullable, column_default')
      .eq('table_schema', 'public')
      .eq('table_name', 'products')
      .order('ordinal_position');

    console.log('Colunas existentes na tabela products:');
    columns?.forEach(col => {
      console.log(`- ${col.column_name} (${col.data_type}) ${col.is_nullable === 'YES' ? 'NULL' : 'NOT NULL'} ${col.column_default ? `DEFAULT: ${col.column_default}` : ''}`);
    });

    // Try to select data to see what's available
    const { data: products, error } = await supabase
      .from('products')
      .select('*')
      .limit(1);

    if (error) {
      console.log('Erro ao buscar produtos:', error.message);
    } else {
      console.log('\nProduto exemplo:', products?.[0]);
    }

  } catch (error) {
    console.error('Erro ao verificar colunas:', error);
  }
}

checkProductsColumns();