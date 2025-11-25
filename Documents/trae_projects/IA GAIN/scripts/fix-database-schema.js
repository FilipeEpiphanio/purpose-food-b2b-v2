const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function fixDatabaseSchema() {
  try {
    console.log('Starting database schema fixes...');

    // Create financial_records table
    const createFinancialRecords = `
      CREATE TABLE IF NOT EXISTS public.financial_records (
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
    `;
    
    const { error: financialError } = await supabase.rpc('exec_sql', {
      query: createFinancialRecords
    });
    
    if (financialError) {
      console.log('Financial records table may already exist or error creating it:', financialError.message);
    } else {
      console.log('✓ Financial records table created');
    }

    // Add order_date column to orders table
    const addOrderDate = `
      ALTER TABLE public.orders 
      ADD COLUMN IF NOT EXISTS order_date DATE DEFAULT CURRENT_DATE;
    `;
    
    const { error: orderDateError } = await supabase.rpc('exec_sql', {
      query: addOrderDate
    });
    
    if (orderDateError) {
      console.log('Order date column may already exist or error adding it:', orderDateError.message);
    } else {
      console.log('✓ Order date column added to orders table');
    }

    // Add status column to customers table
    const addCustomerStatus = `
      ALTER TABLE public.customers 
      ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' 
      CHECK (status IN ('active', 'inactive', 'blocked'));
    `;
    
    const { error: customerStatusError } = await supabase.rpc('exec_sql', {
      query: addCustomerStatus
    });
    
    if (customerStatusError) {
      console.log('Customer status column may already exist or error adding it:', customerStatusError.message);
    } else {
      console.log('✓ Status column added to customers table');
    }

    // Create indexes
    const createIndexes = `
      CREATE INDEX IF NOT EXISTS idx_financial_records_date ON public.financial_records(transaction_date);
      CREATE INDEX IF NOT EXISTS idx_financial_records_type ON public.financial_records(record_type);
      CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);
      CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);
    `;
    
    const { error: indexesError } = await supabase.rpc('exec_sql', {
      query: createIndexes
    });
    
    if (indexesError) {
      console.log('Error creating indexes:', indexesError.message);
    } else {
      console.log('✓ Indexes created');
    }

    // Grant permissions
    const grantPermissions = `
      GRANT SELECT ON public.financial_records TO anon;
      GRANT ALL PRIVILEGES ON public.financial_records TO authenticated;
    `;
    
    const { error: permissionsError } = await supabase.rpc('exec_sql', {
      query: grantPermissions
    });
    
    if (permissionsError) {
      console.log('Error granting permissions:', permissionsError.message);
    } else {
      console.log('✓ Permissions granted');
    }

    // Update existing data
    const updateData = `
      UPDATE public.orders 
      SET order_date = created_at::date 
      WHERE order_date IS NULL;
      
      UPDATE public.customers 
      SET status = 'active' 
      WHERE status IS NULL;
    `;
    
    const { error: updateError } = await supabase.rpc('exec_sql', {
      query: updateData
    });
    
    if (updateError) {
      console.log('Error updating existing data:', updateError.message);
    } else {
      console.log('✓ Existing data updated');
    }

    // Insert sample financial data
    const insertSampleData = `
      INSERT INTO public.financial_records (
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
        ('revenue', 'Sales Revenue', 'Monthly Sales', 22000.00, CURRENT_DATE, 'multiple');
    `;
    
    const { error: insertError } = await supabase.rpc('exec_sql', {
      query: insertSampleData
    });
    
    if (insertError) {
      console.log('Error inserting sample data:', insertError.message);
    } else {
      console.log('✓ Sample financial data inserted');
    }

    console.log('Database schema fixes completed successfully!');
    
  } catch (error) {
    console.error('Error fixing database schema:', error);
  }
}

fixDatabaseSchema();