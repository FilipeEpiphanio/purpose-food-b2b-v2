// Test script to verify database connection and populate test data
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

// Use environment variables from .env file
dotenv.config();

const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseAnonKey = process.env.VITE_SUPABASE_ANON_KEY;

console.log('🔄 Testing database connection...');
console.log('URL:', supabaseUrl);
console.log('Key:', supabaseAnonKey?.substring(0, 10) + '...');

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testConnection() {
  try {
    // Test basic connection
    console.log('📊 Testing connection...');
    const { data, error } = await supabase.from('products').select('*').limit(1);
    
    if (error) {
      console.error('❌ Connection error:', error.message);
      
      // Try to create the products table if it doesn't exist
      console.log('🔄 Attempting to create products table...');
      
      // Simple test data
      const testProducts = [
        {
          name: 'Pão de Queijo Artesanal',
          description: 'Pão de queijo tradicional mineiro',
          category: 'Salgados',
          price: 25.00,
          cost: 15.00,
          stock: 150,
          min_stock: 20,
          unit: 'kg',
          status: 'active'
        }
      ];
      
      // Try to insert test data
      const { data: insertData, error: insertError } = await supabase
        .from('products')
        .insert(testProducts);
        
      if (insertError) {
        console.error('❌ Insert error:', insertError.message);
        console.log('💡 Tip: You may need to run the SQL migration first');
      } else {
        console.log('✅ Test data inserted successfully!');
      }
      
    } else {
      console.log('✅ Database connection successful!');
      console.log('📊 Found products:', data?.length || 0);
      
      // Check if we have data
      const { data: allData, error: allError } = await supabase.from('products').select('*');
      
      if (allError) {
        console.error('❌ Error fetching all data:', allError.message);
      } else {
        console.log('📊 Total products in database:', allData?.length || 0);
        
        if (allData?.length === 0) {
          console.log('💡 No data found. Run the dashboard_test.sql script to populate data.');
        }
      }
    }
    
  } catch (error) {
    console.error('❌ Unexpected error:', error.message);
  }
}

testConnection();