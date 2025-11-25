/**
 * Vercel deploy entry handler, for serverless deployment, please don't modify this file
 */
import type { VercelRequest, VercelResponse } from '@vercel/node';
import express from 'express';
import cors from 'cors';
import { createClient } from '@supabase/supabase-js';
import calendarRoutes from './routes/calendar.js';
import authRoutes from './routes/auth.js';
import productsRoutes from './routes/products.js';
import ordersRoutes from './routes/orders.js';
import financialRoutes from './routes/financial.js';
import customersRoutes from './routes/customers.js';
import invoicesRoutes from './routes/invoices.js';
import socialPostsRoutes from './routes/social-posts.js';
import whatsappMessagesRoutes from './routes/whatsapp-messages.js';
import dashboardRoutes from './routes/dashboard.js';
import stripeRoutes from './routes/stripe.js';

// Initialize Supabase with static config for production
const supabaseUrl = 'https://xqsocdvvvbgdgrezoqlf.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhxc29jZHZ2dmJnZGdyZXpvcWxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzYwNjAsImV4cCI6MjA3ODY1MjA2MH0.ZY-Flx5BoBI3vnSS_PfuxaWHpQEOeLSL8By8QVtGtEw';

export const supabase = createClient(supabaseUrl, supabaseKey);

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/calendar', calendarRoutes);
app.use('/api/products', productsRoutes);
app.use('/api/orders', ordersRoutes);
app.use('/api/financial', financialRoutes);
app.use('/api/customers', customersRoutes);
app.use('/api/invoices', invoicesRoutes);
app.use('/api/social-posts', socialPostsRoutes);
app.use('/api/whatsapp-messages', whatsappMessagesRoutes);
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/stripe', stripeRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Error handler
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

export default function handler(req: VercelRequest, res: VercelResponse) {
  return app(req, res);
}