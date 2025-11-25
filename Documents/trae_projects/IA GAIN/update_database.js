// Script para atualizar o banco de dados com novos campos
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseAnonKey = process.env.VITE_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function updateDatabase() {
  try {
    console.log('🔄 Atualizando banco de dados com novos campos...');

    // SQL para adicionar os novos campos
    const sql = `
      -- Adicionar novos campos à tabela de produtos
      ALTER TABLE products 
      ADD COLUMN IF NOT EXISTS image_url TEXT,
      ADD COLUMN IF NOT EXISTS ingredients TEXT[],
      ADD COLUMN IF NOT EXISTS preparation_time NUMERIC(4,1),
      ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

      -- Atualizar produtos existentes
      UPDATE products SET is_active = true WHERE is_active IS NULL;
      
      -- Criar índice para ingredientes
      CREATE INDEX IF NOT EXISTS idx_products_ingredients ON products USING GIN (ingredients);
    `;

    // Como não podemos executar SQL diretamente, vamos fazer as alterações uma por uma
    
    // 1. Adicionar image_url
    const { error: error1 } = await supabase.rpc('exec_sql', { 
      sql: 'ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT;' 
    });
    if (error1) console.log('Imagem URL já existe ou erro:', error1.message);
    else console.log('✅ Campo image_url adicionado');

    // 2. Adicionar ingredients
    const { error: error2 } = await supabase.rpc('exec_sql', { 
      sql: 'ALTER TABLE products ADD COLUMN IF NOT EXISTS ingredients TEXT[];' 
    });
    if (error2) console.log('Ingredientes já existe ou erro:', error2.message);
    else console.log('✅ Campo ingredients adicionado');

    // 3. Adicionar preparation_time
    const { error: error3 } = await supabase.rpc('exec_sql', { 
      sql: 'ALTER TABLE products ADD COLUMN IF NOT EXISTS preparation_time NUMERIC(4,1);' 
    });
    if (error3) console.log('Tempo preparo já existe ou erro:', error3.message);
    else console.log('✅ Campo preparation_time adicionado');

    // 4. Adicionar is_active
    const { error: error4 } = await supabase.rpc('exec_sql', { 
      sql: 'ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;' 
    });
    if (error4) console.log('Ativo já existe ou erro:', error4.message);
    else console.log('✅ Campo is_active adicionado');

    // 5. Atualizar valores
    const { error: error5 } = await supabase.rpc('exec_sql', { 
      sql: 'UPDATE products SET is_active = true WHERE is_active IS NULL;' 
    });
    if (error5) console.log('Erro ao atualizar valores:', error5.message);
    else console.log('✅ Valores atualizados');

    console.log('🎉 Banco de dados atualizado com sucesso!');

  } catch (error) {
    console.error('❌ Erro ao atualizar banco de dados:', error);
  }
}

// Vamos tentar uma abordagem diferente - criar uma função simples
async function simpleUpdate() {
  try {
    console.log('🔄 Tentando atualizar com método simples...');
    
    // Vamos buscar um produto existente para ver a estrutura atual
    const { data: existingProduct, error: fetchError } = await supabase
      .from('products')
      .select('*')
      .limit(1);

    if (fetchError) {
      console.log('Erro ao buscar produto:', fetchError.message);
      return;
    }

    console.log('📊 Produto existente:', existingProduct?.[0]);
    
    // Se já temos os campos novos, não precisamos atualizar
    if (existingProduct?.[0] && 'image_url' in existingProduct[0]) {
      console.log('✅ Campos já existem no banco de dados!');
      return;
    }
    
    console.log('⚠️ Os campos novos ainda não existem. Você precisa executar o SQL manualmente no Supabase.');
    console.log('📋 Copie e cole este SQL no SQL Editor do Supabase:');
    console.log('');
    console.log('ALTER TABLE products ');
    console.log('ADD COLUMN IF NOT EXISTS image_url TEXT,');
    console.log('ADD COLUMN IF NOT EXISTS ingredients TEXT[],');
    console.log('ADD COLUMN IF NOT EXISTS preparation_time NUMERIC(4,1),');
    console.log('ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;');
    console.log('');
    console.log('UPDATE products SET is_active = true WHERE is_active IS NULL;');
    
  } catch (error) {
    console.error('❌ Erro:', error);
  }
}

simpleUpdate();