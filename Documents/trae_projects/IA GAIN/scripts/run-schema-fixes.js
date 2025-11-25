import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function fixDatabaseSchema() {
  console.log('Starting database schema fixes...');

  try {
    // Create financial_records table
    console.log('Creating financial_records table...');
    const { error: financialError } = await supabase.rpc('exec_sql', {
      query: `CREATE TABLE IF NOT EXISTS public.financial_records (
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
      );`
    });
    
    if (financialError) {
      console.log('Financial records table error (may already exist):', financialError.message);
    } else {
      console.log('✓ Financial records table created');
    }

    // Add order_date column to orders table
    console.log('Adding order_date column to orders table...');
    const { error: orderDateError } = await supabase.rpc('exec_sql', {
      query: `ALTER TABLE public.orders 
      ADD COLUMN IF NOT EXISTS order_date DATE DEFAULT CURRENT_DATE;`
    });
    
    if (orderDateError) {
      console.log('Order date column error (may already exist):', orderDateError.message);
    } else {
      console.log('✓ Order date column added to orders table');
    }

    // Add status column to customers table
    console.log('Adding status column to customers table...');
    const { error: customerStatusError } = await supabase.rpc('exec_sql', {
      query: `ALTER TABLE public.customers 
      ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' 
      CHECK (status IN ('active', 'inactive', 'blocked'));`
    });
    
    if (customerStatusError) {
      console.log('Customer status column error (may already exist):', customerStatusError.message);
    } else {
      console.log('✓ Status column added to customers table');
    }

    // Create indexes
    console.log('Creating indexes...');
    const { error: indexesError } = await supabase.rpc('exec_sql', {
      query: `CREATE INDEX IF NOT EXISTS idx_financial_records_date ON public.financial_records(transaction_date);
      CREATE INDEX IF NOT EXISTS idx_financial_records_type ON public.financial_records(record_type);
      CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);
      CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);`
    });
    
    if (indexesError) {
      console.log('Indexes error:', indexesError.message);
    } else {
      console.log('✓ Indexes created');
    }

    // Grant permissions
    console.log('Granting permissions...');
    const { error: permissionsError } = await supabase.rpc('exec_sql', {
      query: `GRANT SELECT ON public.financial_records TO anon;
      GRANT ALL PRIVILEGES ON public.financial_records TO authenticated;`
    });
    
    if (permissionsError) {
      console.log('Permissions error:', permissionsError.message);
    } else {
      console.log('✓ Permissions granted');
    }

    // Update existing data
    console.log('Updating existing data...');
    const { error: updateError } = await supabase.rpc('exec_sql', {
      query: `UPDATE public.orders 
      SET order_date = created_at::date 
      WHERE order_date IS NULL;
      
      UPDATE public.customers 
      SET status = 'active' 
      WHERE status IS NULL;`
    });
    
    if (updateError) {
      console.log('Update error:', updateError.message);
    } else {
      console.log('✓ Existing data updated');
    }

    // Insert sample financial data
    console.log('Inserting sample financial data...');
    const { error: insertError } = await supabase.rpc('exec_sql', {
      query: `INSERT INTO public.financial_records (
        record_type, 
        category, 
        description, 
        amount, 
        transaction_date, 
        payment_method
      ) VALUES 
        ('revenue', 'Sales Revenue', 'Monthly Sales', 15000.00, CURRENT_DATE - INTERVAL '30 days', 'multiple'),
        ('revenue', 'Sales Revenue', 'Monthly Sales', 18000.00, CURRENT_DATE - INTERVAL '60 days', 'multiple'),
        ('expense', 'Operating Costs', 'Raw Materials', 5000.00, CURRENT_DATE - INTERVAL '15 days', 'bank_transfer'),
        ('expense', 'Operating Costs', 'Utilities', 800.00, CURRENT_DATE - INTERVAL '10 days', 'bank_transfer'),
        ('revenue', 'Sales Revenue', 'Monthly Sales', 22000.00, CURRENT_DATE, 'multiple');`
    });
    
    if (insertError) {
      console.log('Sample data error:', insertError.message);
    } else {
      console.log('✓ Sample financial data inserted');
    }

    console.log('Database schema fixes completed successfully!');
    
  } catch (error) {
    console.error('Error fixing database schema:', error);
  }
}

fixDatabaseSchema();