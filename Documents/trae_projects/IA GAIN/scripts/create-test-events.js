// Script para criar eventos de teste manualmente
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL || '',
  process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

async function createTestEvents() {
  try {
    console.log('🎯 Criando eventos de teste...');

    // Primeiro, vamos verificar se a tabela existe tentando uma consulta simples
    const { data: existingEvents, error: checkError } = await supabase
      .from('calendar_events')
      .select('id')
      .limit(1);

    if (checkError) {
      console.log('❌ Tabela calendar_events não encontrada:', checkError.message);
      console.log('💡 Por favor, execute a migração SQL manualmente no Supabase Dashboard');
      return;
    }

    console.log('✅ Tabela calendar_events encontrada');

    // Criar eventos de teste
    const testEvents = [
      {
        title: 'Feira da Praça Central',
        type: 'feira',
        description: 'Participação na feira mensal da praça central com nossos produtos gourmet',
        start_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
        end_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 8 * 60 * 60 * 1000).toISOString(),
        location: 'Praça Central - Centro',
        notes: 'Levar mesa, toalhas e display dos produtos',
        budget: 500.00,
        attendees: 'João, Maria, Pedro',
        user_id: '123e4567-e89b-12d3-a456-426614174000',
        sync_status: 'not_synced',
        created_by: 'test-script'
      },
      {
        title: 'Reunião com Fornecedores',
        type: 'reuniao',
        description: 'Reunião mensal com fornecedores para revisar pedidos e novidades',
        start_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000 + 14 * 60 * 60 * 1000).toISOString(),
        end_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000 + 16 * 60 * 60 * 1000).toISOString(),
        location: 'Escritório Purpose Food',
        notes: 'Preparar pauta da reunião',
        attendees: 'Carlos, Ana',
        user_id: '123e4567-e89b-12d3-a456-426614174000',
        sync_status: 'not_synced',
        created_by: 'test-script'
      },
      {
        title: 'Entrega de Pedido Especial',
        type: 'entrega',
        description: 'Entrega de pedido de bolo personalizado para festa de casamento',
        start_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000 + 18 * 60 * 60 * 1000).toISOString(),
        end_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000 + 19 * 60 * 60 * 1000).toISOString(),
        location: 'Salão de Festas Jardim',
        notes: 'Verificar endereço exato e ponto de referência',
        budget: 150.00,
        attendees: 'Cliente: Fernanda',
        user_id: '123e4567-e89b-12d3-a456-426614174000',
        sync_status: 'not_synced',
        created_by: 'test-script'
      }
    ];

    for (const event of testEvents) {
      const { data, error } = await supabase
        .from('calendar_events')
        .insert([event])
        .select();

      if (error) {
        console.error('❌ Erro ao inserir evento:', error);
      } else {
        console.log('✅ Evento criado:', event.title);
      }
    }

    console.log('🎉 Script concluído com sucesso!');

  } catch (error) {
    console.error('❌ Erro no script:', error);
  }
}

createTestEvents();