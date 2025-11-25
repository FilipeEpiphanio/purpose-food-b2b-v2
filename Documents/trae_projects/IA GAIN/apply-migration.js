import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function applyMigration() {
  try {
    console.log('Applying order_type column migration...');
    
    // Read the migration SQL
    const migrationSQL = `
      -- Add order_type column to orders table if it doesn't exist
      ALTER TABLE public.orders 
      ADD COLUMN IF NOT EXISTS order_type TEXT DEFAULT 'delivery' CHECK (order_type IN ('delivery', 'pickup', 'dine-in'));
      
      -- Update existing orders with default order_type if null
      UPDATE public.orders 
      SET order_type = 'delivery' 
      WHERE order_type IS NULL;
      
      -- Create index for better performance
      CREATE INDEX IF NOT EXISTS idx_orders_order_type ON public.orders(order_type);
      
      -- Grant permissions
      GRANT SELECT ON public.orders TO anon;
      GRANT ALL PRIVILEGES ON public.orders TO authenticated;
    `;
    
    // Execute the migration SQL
    const { error } = await supabase.rpc('exec_sql', {
      query: migrationSQL
    });
    
    if (error) {
      console.log('❌ Migration failed:', error.message);
      return false;
    } else {
      console.log('✅ Migration applied successfully!');
      return true;
    }
  } catch (err) {
    console.log('❌ Migration error:', err.message);
    return false;
  }
}

applyMigration().then(success => {
  process.exit(success ? 0 : 1);
});