import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';
import Stripe from 'stripe';

// Import routes
import authRoutes from './routes/auth';
import productsRoutes from './routes/products';
import ordersRoutes from './routes/orders';
import customersRoutes from './routes/customers';
import financialRoutes from './routes/financial';
import salesRoutes from './routes/sales';
import socialMediaRoutes from './routes/socialMedia';
import invoiceRoutes from './routes/invoices';
import stripeRoutes from './routes/stripe';
import fixSchemaRoutes from './routes/fix-schema';
import calendarRoutes from './routes/calendar';
import dashboardRoutes from './routes/dashboard';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Initialize Supabase
export const supabase = createClient(
  process.env.SUPABASE_URL || '',
  process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

// Initialize Stripe
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
  apiVersion: '2023-10-16',
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/products', productsRoutes);
app.use('/api/orders', ordersRoutes);
app.use('/api/customers', customersRoutes);
app.use('/api/financial', financialRoutes);
app.use('/api/sales', salesRoutes);
app.use('/api/social-media', socialMediaRoutes);
app.use('/api/invoices', invoiceRoutes);
app.use('/api/stripe', stripeRoutes);
app.use('/api/fix-schema', fixSchemaRoutes);
app.use('/api/calendar', calendarRoutes);
app.use('/api/dashboard', dashboardRoutes);

// Payment webhook endpoint (for Stripe)
app.post('/api/webhooks/stripe', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!sig || !webhookSecret) {
    return res.status(400).send('Missing signature or webhook secret');
  }

  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, webhookSecret);
  } catch (err) {
    console.log(`Webhook signature verification failed.`, err);
    return res.status(400).send(`Webhook Error: ${err}`);
  }

  // Handle the event
  switch (event.type) {
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      console.log('PaymentIntent was successful!');
      // Update order status in database
      break;
    case 'payment_intent.payment_failed':
      const failedPayment = event.data.object;
      console.log('PaymentIntent failed!');
      // Update order status in database
      break;
    default:
      console.log(`Unhandled event type ${event.type}`);
  }

  res.json({ received: true });
});

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// Migration endpoint to fix order_type column
app.post('/api/migrate/order-type', async (req, res) => {
  try {
    console.log('Applying order_type column migration...');
    
    // First, let's check if the column exists
    const { data: checkData, error: checkError } = await supabase
      .from('orders')
      .select('order_type')
      .limit(1);
    
    if (!checkError) {
      console.log('✅ order_type column already exists');
      return res.json({ success: true, message: 'order_type column already exists' });
    }
    
    // If we get here, the column doesn't exist, so let's add it
    console.log('order_type column not found, attempting to add it...');
    
    // Try to add the column by updating a non-existent record
    // This should trigger the column creation
    const { error: updateError } = await supabase
      .from('orders')
      .update({ order_type: 'delivery' })
      .eq('id', '00000000-0000-0000-0000-000000000000');
    
    if (updateError && updateError.message.includes('column')) {
      // Column still doesn't exist, let's try a different approach
      console.log('Direct update failed, trying alternative method...');
      
      // Insert a new record with the order_type field
      const { error: insertError } = await supabase
        .from('orders')
        .insert([{
          customer_id: '00000000-0000-0000-0000-000000000000',
          total_amount: 0,
          status: 'pending',
          order_type: 'delivery'
        }]);
      
      if (insertError) {
        console.log('Migration failed:', insertError.message);
        return res.status(500).json({ 
          success: false, 
          error: 'Failed to add order_type column',
          details: insertError.message 
        });
      }
      
      // Delete the test record
      await supabase
        .from('orders')
        .delete()
        .eq('id', '00000000-0000-0000-0000-000000000000');
    }
    
    // Verify the column was added
    const { data: verifyData, error: verifyError } = await supabase
      .from('orders')
      .select('order_type')
      .limit(1);
    
    if (verifyError) {
      console.log('Migration verification failed:', verifyError.message);
      return res.status(500).json({ 
        success: false, 
        error: 'Migration appeared to succeed but column not found',
        details: verifyError.message 
      });
    }
    
    console.log('✅ Migration completed successfully!');
    res.json({ success: true, message: 'order_type column added successfully' });
    
  } catch (error) {
    console.error('Migration error:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Migration failed',
      details: error.message 
    });
  }
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📱 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:5173'}`);
  console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
});

export default app;