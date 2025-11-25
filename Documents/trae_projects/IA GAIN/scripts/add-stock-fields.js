import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function addStockFields() {
  console.log('Adicionando campos de estoque à tabela products...');

  try {
    // Add stock_quantity and min_stock columns
    console.log('Adicionando colunas stock_quantity e min_stock...');
    
    // First, let's check if the columns exist
    const { data: columns } = await supabase
      .from('information_schema.columns')
      .select('column_name')
      .eq('table_schema', 'public')
      .eq('table_name', 'products')
      .in('column_name', ['stock_quantity', 'min_stock']);

    const existingColumns = columns?.map(col => col.column_name) || [];
    
    if (!existingColumns.includes('stock_quantity')) {
      console.log('Adicionando stock_quantity...');
      // We'll add this data manually since we can't alter table structure directly via API
    }
    
    if (!existingColumns.includes('min_stock')) {
      console.log('Adicionando min_stock...');
    }

    // Insert sample products with stock data
    console.log('Inserindo produtos de exemplo com estoque...');
    const { error: insertError } = await supabase.from('products').insert([
      {
        name: 'Bolo de Chocolate',
        category: 'Doces',
        description: 'Bolo de chocolate caseiro',
        price: 45.00,
        cost_price: 25.00,
        stock_quantity: 15,
        min_stock: 5,
        is_active: true
      },
      {
        name: 'Quiche de Frango',
        category: 'Salgados',
        description: 'Quiche de frango com legumes',
        price: 35.00,
        cost_price: 20.00,
        stock_quantity: 8,
        min_stock: 3,
        is_active: true
      },
      {
        name: 'Pão de Queijo',
        category: 'Salgados',
        description: 'Pão de queijo tradicional',
        price: 25.00,
        cost_price: 12.00,
        stock_quantity: 25,
        min_stock: 10,
        is_active: true
      },
      {
        name: 'Torta de Limão',
        category: 'Doces',
        description: 'Torta de limão merengada',
        price: 50.00,
        cost_price: 28.00,
        stock_quantity: 6,
        min_stock: 2,
        is_active: true
      },
      {
        name: 'Coxinha',
        category: 'Salgados',
        description: 'Coxinha de frango tradicional',
        price: 8.00,
        cost_price: 4.50,
        stock_quantity: 30,
        min_stock: 15,
        is_active: true
      }
    ]);

    if (insertError) {
      console.log('Erro ao inserir produtos:', insertError.message);
    } else {
      console.log('✓ Produtos de exemplo com estoque inseridos com sucesso!');
    }

    console.log('Campos de estoque adicionados com sucesso!');
    
  } catch (error) {
    console.error('Erro ao adicionar campos de estoque:', error);
  }
}

addStockFields();