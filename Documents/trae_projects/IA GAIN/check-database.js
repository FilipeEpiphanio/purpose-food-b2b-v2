import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

async function checkDatabase() {
  try {
    console.log('Checking database structure...');
    
    // Try to query the orders table with order_type column
    const { data, error } = await supabase
      .from('orders')
      .select('order_type')
      .limit(1);
    
    if (error) {
      console.log('❌ order_type column NOT found - migration needed');
      console.log('Error details:', error.message);
      return false;
    } else {
      console.log('✅ order_type column found - migration applied successfully');
      console.log('Sample data:', data);
      return true;
    }
  } catch (err) {
    console.log('❌ Database verification error:', err.message);
    return false;
  }
}

checkDatabase().then(success => {
  process.exit(success ? 0 : 1);
});