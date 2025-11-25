import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabase = createClient(
  process.env.VITE_SUPABASE_URL,
  process.env.VITE_SUPABASE_ANON_KEY
);

async function insertTestEvents() {
  try {
    // Get the current user (you'll need to be logged in)
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      console.log('Please log in first to insert test events');
      return;
    }

    const testEvents = [
      {
        title: 'Feira de Alimentos Orgânicos - Centro',
        description: 'Feira semanal com produtos frescos e orgânicos da Purpose Food',
        event_type: 'feira',
        start_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days from now
        end_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 8 * 60 * 60 * 1000).toISOString(), // 8 hours later
        location: 'Praça Central - Centro da Cidade',
        address: 'Praça Central, 123 - Centro',
        event_category: 'food_fair',
        expected_attendees: 150,
        products_to_bring: ['Pães Artesanais', 'Bolos Funcionais', 'Sucos Naturais', 'Saladas'],
        estimated_revenue: 2500.00,
        status: 'scheduled',
        created_by: user.id
      },
      {
        title: 'Entrega de Marmitas - Empresa TechCorp',
        description: 'Entrega semanal de marmitas saudáveis para funcionários',
        event_type: 'entrega',
        start_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
        end_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(), // 2 hours later
        location: 'TechCorp - Setor de Tecnologia',
        address: 'Rua da Tecnologia, 456 - Setor Industrial',
        event_category: 'delivery',
        expected_attendees: 50,
        products_to_bring: ['Marmitas Vegetarianas', 'Marmitas Veganas', 'Sucos', 'Sobremesas'],
        estimated_revenue: 800.00,
        status: 'confirmed',
        created_by: user.id
      },
      {
        title: 'Reunião de Planejamento - Evento Corporativo',
        description: 'Reunião para planejar evento corporativo de final de ano',
        event_type: 'reuniao',
        start_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days from now
        end_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000 + 1.5 * 60 * 60 * 1000).toISOString(), // 1.5 hours later
        location: 'Escritório Purpose Food',
        address: 'Rua da Alimentação Saudável, 789',
        event_category: 'meeting',
        expected_attendees: 8,
        special_requirements: 'Trazer amostras de cardápio e orçamentos',
        status: 'scheduled',
        created_by: user.id
      },
      {
        title: 'Evento Corporativo - Festa de Final de Ano',
        description: 'Catering para festa corporativa de final de ano',
        event_type: 'evento',
        start_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 1 week from now
        end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000 + 6 * 60 * 60 * 1000).toISOString(), // 6 hours later
        location: 'Centro de Convenções',
        address: 'Avenida das Convenções, 1000 - Centro',
        event_category: 'corporate_event',
        expected_attendees: 200,
        products_to_bring: ['Catering Completo', 'Bebidas', 'Sobremesas', 'Decoração'],
        estimated_revenue: 8000.00,
        special_requirements: 'Montagem 2h antes do evento',
        status: 'scheduled',
        created_by: user.id
      }
    ];

    console.log('Inserting test events...');
    
    for (const event of testEvents) {
      const { data, error } = await supabase
        .from('calendar_events')
        .insert(event)
        .select();
      
      if (error) {
        console.error('Error inserting event:', event.title, error);
      } else {
        console.log('✅ Event inserted:', event.title);
      }
    }
    
    console.log('✅ All test events inserted successfully!');
    
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
    }
    
  } catch (error) {
    console.error('Error:', error);
  }
}

insertTestEvents();