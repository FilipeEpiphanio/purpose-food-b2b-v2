import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL || '',
  process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

async function checkAndCreateCalendarTable() {
  try {
    // Check if table exists
    const { data: tableExists, error: checkError } = await supabase
      .from('calendar_events')
      .select('id')
      .limit(1);

    if (checkError && checkError.code === 'PGRST116') {
      console.log('📅 Criando tabela calendar_events...');
      
      // Create table SQL
      const createTableSQL = `
        CREATE TABLE IF NOT EXISTS calendar_events (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          title VARCHAR(255) NOT NULL,
          type VARCHAR(50) NOT NULL CHECK (type IN ('feira', 'evento', 'compromisso', 'entrega', 'reuniao')),
          description TEXT,
          start_date TIMESTAMP WITH TIME ZONE NOT NULL,
          end_date TIMESTAMP WITH TIME ZONE NOT NULL,
          location VARCHAR(255),
          notes TEXT,
          budget DECIMAL(10,2),
          attendees TEXT,
          user_id UUID NOT NULL,
          google_event_id VARCHAR(255),
          google_calendar_id VARCHAR(255),
          sync_status VARCHAR(50) DEFAULT 'not_synced' CHECK (sync_status IN ('synced', 'pending', 'failed', 'not_synced')),
          last_sync_at TIMESTAMP WITH TIME ZONE,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          created_by VARCHAR(255)
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_calendar_events_user_id ON calendar_events(user_id);
        CREATE INDEX IF NOT EXISTS idx_calendar_events_start_date ON calendar_events(start_date);
        CREATE INDEX IF NOT EXISTS idx_calendar_events_google_event_id ON calendar_events(google_event_id);
        CREATE INDEX IF NOT EXISTS idx_calendar_events_sync_status ON calendar_events(sync_status);

        -- Enable RLS
        ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;

        -- Create RLS policies
        CREATE POLICY "Users can view their own events" ON calendar_events
          FOR SELECT USING (auth.uid() = user_id);

        CREATE POLICY "Users can insert their own events" ON calendar_events
          FOR INSERT WITH CHECK (auth.uid() = user_id);

        CREATE POLICY "Users can update their own events" ON calendar_events
          FOR UPDATE USING (auth.uid() = user_id);

        CREATE POLICY "Users can delete their own events" ON calendar_events
          FOR DELETE USING (auth.uid() = user_id);

        -- Grant permissions
        GRANT SELECT ON calendar_events TO anon, authenticated;
        GRANT INSERT ON calendar_events TO anon, authenticated;
        GRANT UPDATE ON calendar_events TO anon, authenticated;
        GRANT DELETE ON calendar_events TO anon, authenticated;
      `;

      const { error: createError } = await supabase.rpc('exec_sql', { sql: createTableSQL });
      
      if (createError) {
        console.error('❌ Erro ao criar tabela:', createError);
        return;
      }
      
      console.log('✅ Tabela calendar_events criada com sucesso!');
    } else {
      console.log('✅ Tabela calendar_events já existe');
    }

    // Insert test events
    console.log('📅 Inserindo eventos de teste...');
    
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
        sync_status: 'not_synced'
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
        sync_status: 'not_synced'
      }
    ];

    for (const event of testEvents) {
      const { error: insertError } = await supabase
        .from('calendar_events')
        .insert([event]);
      
      if (insertError) {
        console.error('❌ Erro ao inserir evento:', insertError);
      } else {
        console.log('✅ Evento inserido:', event.title);
      }
    }

    console.log('🎉 Script concluído com sucesso!');

  } catch (error) {
    console.error('❌ Erro no script:', error);
  }
}

checkAndCreateCalendarTable();