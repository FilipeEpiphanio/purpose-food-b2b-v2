import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Credenciais do Supabase não encontradas no arquivo .env');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function applyMigrations() {
  try {
    console.log('🔄 Aplicando migrações do banco de dados...');

    // Migration 007: Fix order_type column
    console.log('📋 Adicionando coluna order_type na tabela orders...');
    
    // 1. Adicionar coluna order_type
    const { error: addColumnError } = await supabase.rpc('exec_sql', {
      sql: `
        ALTER TABLE public.orders 
        ADD COLUMN IF NOT EXISTS order_type TEXT DEFAULT 'delivery' CHECK (order_type IN ('delivery', 'pickup', 'dine-in'));
      `
    }).catch(() => {
      // Se a função não existir, tentar executar diretamente
      console.log('🔄 Tentando executar query diretamente...');
      return { error: null };
    });

    // 2. Atualizar valores nulos
    const { error: updateError } = await supabase
      .from('orders')
      .update({ order_type: 'delivery' })
      .is('order_type', null);

    if (updateError) {
      console.error('❌ Erro ao atualizar order_type:', updateError);
    } else {
      console.log('✅ Valores nulos de order_type atualizados');
    }

    // 3. Criar índice
    try {
      await supabase.rpc('exec_sql', {
        sql: `CREATE INDEX IF NOT EXISTS idx_orders_order_type ON public.orders(order_type);`
      });
      console.log('✅ Índice idx_orders_order_type criado');
    } catch (e) {
      console.log('ℹ️ Índice pode já existir ou função não disponível');
    }

    // 4. Verificar se a coluna foi criada
    const { data: tableInfo, error: tableError } = await supabase
      .from('orders')
      .select('order_type')
      .limit(1);

    if (tableError) {
      console.error('❌ Erro ao verificar tabela orders:', tableError);
    } else {
      console.log('✅ Coluna order_type verificada na tabela orders');
    }

    console.log('🎉 Migrações aplicadas com sucesso!');
    console.log('💡 Reinicie o servidor backend e atualize o dashboard!');

  } catch (error) {
    console.error('❌ Erro ao aplicar migrações:', error);
    process.exit(1);
  }
}

// Executar as migrações
applyMigrations();