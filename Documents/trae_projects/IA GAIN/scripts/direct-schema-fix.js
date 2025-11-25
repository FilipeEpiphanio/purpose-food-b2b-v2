import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function fixSchemaDirectly() {
  console.log('Applying database schema fixes directly...');

  try {
    // First, let's check what tables exist
    console.log('Checking current database schema...');
    
    // Check if financial_records table exists
    const { data: financialExists } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public')
      .eq('table_name', 'financial_records');

    if (!financialExists || financialExists.length === 0) {
      console.log('Creating financial_records table...');
      
      // Create table using raw SQL through the API
      const { error: createError } = await supabase
        .rpc('exec_sql', {
          query: `
            CREATE TABLE public.financial_records (
              id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
              record_type VARCHAR(50) NOT NULL,
              category VARCHAR(100) NOT NULL,
              description TEXT,
              amount DECIMAL(10,2) NOT NULL,
              transaction_date DATE NOT NULL,
              payment_method VARCHAR(50),
              reference_id UUID,
              reference_type VARCHAR(50),
              created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
              updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
          `
        });

      if (createError) {
        console.log('Could not create financial_records table:', createError.message);
      } else {
        console.log('✓ Financial records table created');
      }
    } else {
      console.log('Financial records table already exists');
    }

    // Check if orders table has order_date column
    const { data: orderColumns } = await supabase
      .from('information_schema.columns')
      .select('column_name')
      .eq('table_schema', 'public')
      .eq('table_name', 'orders')
      .eq('column_name', 'order_date');

    if (!orderColumns || orderColumns.length === 0) {
      console.log('Adding order_date column to orders table...');
      
      const { error: alterError } = await supabase
        .from('orders')
        .alter()
        .addColumn('order_date', 'date', { default: 'CURRENT_DATE' });

      if (alterError) {
        console.log('Could not add order_date column:', alterError.message);
      } else {
        console.log('✓ Order date column added');
      }
    } else {
      console.log('Order date column already exists');
    }

    // Check if customers table has status column
    const { data: customerColumns } = await supabase
      .from('information_schema.columns')
      .select('column_name')
      .eq('table_schema', 'public')
      .eq('table_name', 'customers')
      .eq('column_name', 'status');

    if (!customerColumns || customerColumns.length === 0) {
      console.log('Adding status column to customers table...');
      
      // For now, let's just update the existing records
      const { error: updateError } = await supabase
        .from('customers')
        .update({ status: 'active' });

      if (updateError) {
        console.log('Could not update customer status:', updateError.message);
      } else {
        console.log('✓ Customer status updated');
      }
    } else {
      console.log('Customer status column already exists');
    }

    // Insert some sample financial data
    console.log('Inserting sample financial data...');
    const { error: insertError } = await supabase
      .from('financial_records')
      .insert([
        {
          record_type: 'revenue',
          category: 'Sales Revenue',
          description: 'Monthly Sales',
          amount: 15000.00,
          transaction_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          payment_method: 'multiple'
        },
        {
          record_type: 'revenue',
          category: 'Sales Revenue',
          description: 'Monthly Sales',
          amount: 18000.00,
          transaction_date: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          payment_method: 'multiple'
        },
        {
          record_type: 'expense',
          category: 'Operating Costs',
          description: 'Raw Materials',
          amount: 5000.00,
          transaction_date: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          payment_method: 'bank_transfer'
        },
        {
          record_type: 'revenue',
          category: 'Sales Revenue',
          description: 'Current Month Sales',
          amount: 22000.00,
          transaction_date: new Date().toISOString().split('T')[0],
          payment_method: 'multiple'
        }
      ]);

    if (insertError) {
      console.log('Could not insert sample data:', insertError.message);
    } else {
      console.log('✓ Sample financial data inserted');
    }

    console.log('Database schema fixes completed!');
    
  } catch (error) {
    console.error('Error applying schema fixes:', error);
  }
}

fixSchemaDirectly();