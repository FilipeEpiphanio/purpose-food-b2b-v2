import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabase = createClient(
  process.env.VITE_SUPABASE_URL,
  process.env.VITE_SUPABASE_ANON_KEY
);

async function insertTestEventsSimple() {
  try {
    console.log('📝 Inserting test events with minimal data...');
    
    // Create events with minimal required fields (created_by will be set automatically)
    const testEvents = [
      {
        title: 'Feira de Alimentos Orgânicos - Centro',
        description: 'Feira semanal com produtos frescos e orgânicos da Purpose Food',
        event_type: 'feira',
        start_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
        end_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 8 * 60 * 60 * 1000).toISOString(),
        location: 'Praça Central - Centro da Cidade',
        address: 'Praça Central, 123 - Centro',
        status: 'scheduled'
      },
      {
        title: 'Entrega de Marmitas - Empresa TechCorp',
        description: 'Entrega semanal de marmitas saudáveis para funcionários',
        event_type: 'entrega',
        start_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(),
        end_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
        location: 'TechCorp - Setor de Tecnologia',
        address: 'Rua da Tecnologia, 456 - Setor Industrial',
        status: 'confirmed'
      },
      {
        title: 'Reunião de Planejamento - Evento Corporativo',
        description: 'Reunião para planejar evento corporativo de final de ano',
        event_type: 'reuniao',
        start_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
        end_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000 + 1.5 * 60 * 60 * 1000).toISOString(),
        location: 'Escritório Purpose Food',
        address: 'Rua da Alimentação Saudável, 789',
        status: 'scheduled'
      }
    ];

    let insertedCount = 0;
    
    for (const event of testEvents) {
      const { data, error } = await supabase
        .from('calendar_events')
        .insert(event)
        .select();
      
      if (error) {
        console.error('❌ Error inserting event:', event.title, error.message);
      } else {
        console.log('✅ Event inserted:', event.title);
        insertedCount++;
      }
    }
    
    console.log(`\n📊 Summary: ${insertedCount}/${testEvents.length} events inserted successfully`);
    
    // Verify the events were inserted
    const { data: events, error: fetchError } = await supabase
      .from('calendar_events')
      .select('*')
      .order('start_date', { ascending: true });
    
    if (!fetchError) {
      console.log(`\n📅 Total events in database: ${events.length}`);
      events.forEach(event => {
        console.log(`- ${event.title} (${event.event_type}) - ${new Date(event.start_date).toLocaleString()}`);
      });
    } else {
      console.error('Error fetching events:', fetchError.message);
    }
    
  } catch (error) {
    console.error('Error:', error);
  }
}

insertTestEventsSimple();