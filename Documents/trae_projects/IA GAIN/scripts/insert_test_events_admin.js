import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

// Use service role key for admin access
const supabase = createClient(
  process.env.VITE_SUPABASE_URL,
  process.env.VITE_SUPABASE_SERVICE_ROLE_KEY || process.env.VITE_SUPABASE_ANON_KEY
);

async function insertTestEvents() {
  try {
    // Get the first user from the auth.users table to use as created_by
    const { data: users, error: userError } = await supabase
      .from('users')
      .select('id')
      .limit(1);
    
    if (userError || !users || users.length === 0) {
      console.log('No users found. Using a default UUID for testing.');
      // Use a default UUID for testing
      const defaultUserId = '00000000-0000-0000-0000-000000000001';
      
      const testEvents = [
        {
          title: 'Feira de Alimentos Orgânicos - Centro',
          description: 'Feira semanal com produtos frescos e orgânicos da Purpose Food',
          event_type: 'feira',
          start_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 8 * 60 * 60 * 1000).toISOString(),
          location: 'Praça Central - Centro da Cidade',
          address: 'Praça Central, 123 - Centro',
          event_category: 'food_fair',
          expected_attendees: 150,
          products_to_bring: ['Pães Artesanais', 'Bolos Funcionais', 'Sucos Naturais', 'Saladas'],
          estimated_revenue: 2500.00,
          status: 'scheduled',
          created_by: defaultUserId
        },
        {
          title: 'Entrega de Marmitas - Empresa TechCorp',
          description: 'Entrega semanal de marmitas saudáveis para funcionários',
          event_type: 'entrega',
          start_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
          location: 'TechCorp - Setor de Tecnologia',
          address: 'Rua da Tecnologia, 456 - Setor Industrial',
          event_category: 'delivery',
          expected_attendees: 50,
          products_to_bring: ['Marmitas Vegetarianas', 'Marmitas Veganas', 'Sucos', 'Sobremesas'],
          estimated_revenue: 800.00,
          status: 'confirmed',
          created_by: defaultUserId
        },
        {
          title: 'Reunião de Planejamento - Evento Corporativo',
          description: 'Reunião para planejar evento corporativo de final de ano',
          event_type: 'reuniao',
          start_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000 + 1.5 * 60 * 60 * 1000).toISOString(),
          location: 'Escritório Purpose Food',
          address: 'Rua da Alimentação Saudável, 789',
          event_category: 'meeting',
          expected_attendees: 8,
          special_requirements: 'Trazer amostras de cardápio e orçamentos',
          status: 'scheduled',
          created_by: defaultUserId
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
    } else {
      const userId = users[0].id;
      console.log('Using user ID:', userId);
      
      const testEvents = [
        {
          title: 'Feira de Alimentos Orgânicos - Centro',
          description: 'Feira semanal com produtos frescos e orgânicos da Purpose Food',
          event_type: 'feira',
          start_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 8 * 60 * 60 * 1000).toISOString(),
          location: 'Praça Central - Centro da Cidade',
          address: 'Praça Central, 123 - Centro',
          event_category: 'food_fair',
          expected_attendees: 150,
          products_to_bring: ['Pães Artesanais', 'Bolos Funcionais', 'Sucos Naturais', 'Saladas'],
          estimated_revenue: 2500.00,
          status: 'scheduled',
          created_by: userId
        },
        {
          title: 'Entrega de Marmitas - Empresa TechCorp',
          description: 'Entrega semanal de marmitas saudáveis para funcionários',
          event_type: 'entrega',
          start_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
          location: 'TechCorp - Setor de Tecnologia',
          address: 'Rua da Tecnologia, 456 - Setor Industrial',
          event_category: 'delivery',
          expected_attendees: 50,
          products_to_bring: ['Marmitas Vegetarianas', 'Marmitas Veganas', 'Sucos', 'Sobremesas'],
          estimated_revenue: 800.00,
          status: 'confirmed',
          created_by: userId
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
    }
    
    console.log('✅ Test events insertion completed!');
    
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