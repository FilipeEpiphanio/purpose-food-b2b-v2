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

async function checkAndFixOrderType() {
  try {
    console.log('🔍 Verificando estrutura da tabela orders...');

    // Primeiro, vamos verificar se a coluna order_type existe
    const { data: ordersData, error: ordersError } = await supabase
      .from('orders')
      .select('*')
      .limit(1);

    if (ordersError) {
      console.error('❌ Erro ao acessar tabela orders:', ordersError);
      return;
    }

    // Verificar se order_type existe nos dados retornados
    const hasOrderType = ordersData && ordersData.length > 0 && 'order_type' in ordersData[0];
    
    if (hasOrderType) {
      console.log('✅ Coluna order_type já existe na tabela orders');
      
      // Verificar se há valores nulos
      const { data: nullData, error: nullError } = await supabase
        .from('orders')
        .select('id, order_type')
        .is('order_type', null);

      if (nullError) {
        console.error('❌ Erro ao verificar valores nulos:', nullError);
      } else if (nullData && nullData.length > 0) {
        console.log(`📊 Encontrados ${nullData.length} pedidos com order_type nulo. Atualizando...`);
        
        // Atualizar valores nulos
        const { error: updateError } = await supabase
          .from('orders')
          .update({ order_type: 'delivery' })
          .is('order_type', null);

        if (updateError) {
          console.error('❌ Erro ao atualizar valores nulos:', updateError);
        } else {
          console.log('✅ Valores nulos de order_type atualizados com sucesso');
        }
      } else {
        console.log('✅ Nenhum valor nulo encontrado em order_type');
      }
    } else {
      console.log('⚠️ Coluna order_type não encontrada. A coluna será criada automaticamente pela aplicação.');
      console.log('💡 A aplicação React está configurada para lidar com isso.');
    }

    console.log('🎉 Verificação concluída!');
    console.log('💡 Se ainda houver erros, reinicie o servidor backend e atualize o dashboard.');

  } catch (error) {
    console.error('❌ Erro durante a verificação:', error);
  }
}

// Executar verificação
checkAndFixOrderType();