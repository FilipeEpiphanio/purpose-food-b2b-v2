import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL || '',
  process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

async function fixSchema() {
  console.log('🔄 Iniciando correção de schema do banco de dados...');
  
  try {
    // 1. Adicionar colunas faltantes na tabela orders
    console.log('📅 Adicionando coluna order_date na tabela orders...');
    const { error: orderDateError } = await supabase
      .from('orders')
      .select('order_date')
      .limit(1);
    
    if (orderDateError && orderDateError.code === '42703') {
      // Coluna não existe, vamos adicionar
      const { error: addError } = await supabase.rpc('add_column_if_not_exists', {
        table_name: 'orders',
        column_name: 'order_date',
        column_type: 'DATE DEFAULT CURRENT_DATE'
      });
      
      if (addError) {
        console.log('⚠️ Erro ao adicionar order_date (pode já existir):', addError.message);
      } else {
        console.log('✅ Coluna order_date adicionada com sucesso!');
      }
    }

    // 2. Adicionar coluna status na tabela customers
    console.log('👥 Adicionando coluna status na tabela customers...');
    const { error: customerStatusError } = await supabase
      .from('customers')
      .select('status')
      .limit(1);
    
    if (customerStatusError && customerStatusError.code === '42703') {
      const { error: addError } = await supabase.rpc('add_column_if_not_exists', {
        table_name: 'customers',
        column_name: 'status',
        column_type: "TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked'))"
      });
      
      if (addError) {
        console.log('⚠️ Erro ao adicionar status (pode já existir):', addError.message);
      } else {
        console.log('✅ Coluna status adicionada com sucesso!');
      }
    }

    // 3. Criar tabela financial_records
    console.log('💰 Criando tabela financial_records...');
    const { error: tableExistsError } = await supabase
      .from('financial_records')
      .select('id')
      .limit(1);
    
    if (tableExistsError && tableExistsError.code === '42P01') {
      // Tabela não existe, vamos criar
      const { error: createError } = await supabase.rpc('create_financial_records_table');
      
      if (createError) {
        console.log('⚠️ Erro ao criar financial_records:', createError.message);
      } else {
        console.log('✅ Tabela financial_records criada com sucesso!');
      }
    }

    // 4. Adicionar outras colunas necessárias
    console.log('📦 Adicionando colunas adicionais...');
    
    // delivery_date em orders
    const { error: deliveryError } = await supabase
      .from('orders')
      .select('delivery_date')
      .limit(1);
    
    if (deliveryError && deliveryError.code === '42703') {
      await supabase.rpc('add_column_if_not_exists', {
        table_name: 'orders',
        column_name: 'delivery_date',
        column_type: 'TIMESTAMP WITH TIME ZONE'
      });
    }

    // cost_price em products
    const { error: costError } = await supabase
      .from('products')
      .select('cost_price')
      .limit(1);
    
    if (costError && costError.code === '42703') {
      await supabase.rpc('add_column_if_not_exists', {
        table_name: 'products',
        column_name: 'cost_price',
        column_type: 'DECIMAL(10,2) DEFAULT 0'
      });
    }

    console.log('✅ Correções de schema aplicadas com sucesso!');
    
  } catch (error: any) {
    console.error('❌ Erro ao aplicar correções:', error);
  }
}

// Executar o script
fixSchema().then(() => {
  console.log('🏁 Script de correção finalizado!');
  process.exit(0);
}).catch((error) => {
  console.error('💥 Erro fatal:', error);
  process.exit(1);
});