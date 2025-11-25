import express from 'express';
import { stripe, supabase } from '../server';

const router = express.Router();

// Create payment intent
router.post('/create-payment-intent', async (req, res) => {
  try {
    const { items, customerId, paymentMethodId } = req.body;

    // Calculate total amount
    const totalAmount = items.reduce((sum: number, item: any) => {
      return sum + (item.price * item.quantity * 100); // Convert to cents
    }, 0);

    // Create payment intent
    const paymentIntent = await stripe.paymentIntents.create({
      amount: totalAmount,
      currency: 'brl',
      payment_method: paymentMethodId,
      customer: customerId,
      confirm: true,
      return_url: `${process.env.FRONTEND_URL}/payment-success`,
      metadata: {
        customerId,
        items: JSON.stringify(items),
      },
    });

    // Save order to database
    const { data: order, error } = await supabase
      .from('orders')
      .insert({
        customer_id: customerId,
        total_amount: totalAmount / 100, // Convert back to reais
        payment_intent_id: paymentIntent.id,
        status: paymentIntent.status === 'succeeded' ? 'paid' : 'pending',
        items: items,
        payment_method: 'stripe',
      })
      .select()
      .single();

    if (error) {
      throw error;
    }

    res.json({
      success: true,
      paymentIntent: paymentIntent,
      order: order,
    });
  } catch (error) {
    console.error('Error creating payment intent:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create payment intent',
    });
  }
});

// Get payment methods for customer
router.get('/payment-methods/:customerId', async (req, res) => {
  try {
    const { customerId } = req.params;

    const paymentMethods = await stripe.paymentMethods.list({
      customer: customerId,
      type: 'card',
    });

    res.json({
      success: true,
      paymentMethods: paymentMethods.data,
    });
  } catch (error) {
    console.error('Error fetching payment methods:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch payment methods',
    });
  }
});

// Create customer
router.post('/create-customer', async (req, res) => {
  try {
    const { email, name, phone, cpf, address } = req.body;

    // Create Stripe customer
    const customer = await stripe.customers.create({
      email,
      name,
      phone,
      metadata: {
        cpf,
        address: JSON.stringify(address),
      },
    });

    // Save to database
    const { data: savedCustomer, error } = await supabase
      .from('customers')
      .insert({
        stripe_customer_id: customer.id,
        email,
        name,
        phone,
        cpf,
        address,
      })
      .select()
      .single();

    if (error) {
      throw error;
    }

    res.json({
      success: true,
      customer: savedCustomer,
      stripeCustomer: customer,
    });
  } catch (error) {
    console.error('Error creating customer:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create customer',
    });
  }
});

// Process PIX payment
router.post('/process-pix', async (req, res) => {
  try {
    const { items, customerId } = req.body;
    const totalAmount = items.reduce((sum: number, item: any) => {
      return sum + (item.price * item.quantity * 100);
    }, 0);

    // Create PIX payment intent
    const paymentIntent = await stripe.paymentIntents.create({
      amount: totalAmount,
      currency: 'brl',
      payment_method_types: ['pix'],
      customer: customerId,
      metadata: {
        customerId,
        items: JSON.stringify(items),
      },
    });

    res.json({
      success: true,
      paymentIntent: paymentIntent,
      pixQrCode: paymentIntent.next_action?.pix_display_qr_code?.data?.toString(),
    });
  } catch (error) {
    console.error('Error processing PIX payment:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process PIX payment',
    });
  }
});

// Get sales statistics
router.get('/stats', async (req, res) => {
  try {
    const { startDate, endDate } = req.query;

    const { data: sales, error } = await supabase
      .from('orders')
      .select('*')
      .gte('created_at', startDate)
      .lte('created_at', endDate)
      .eq('status', 'paid');

    if (error) {
      throw error;
    }

    const totalSales = sales.reduce((sum, order) => sum + order.total_amount, 0);
    const totalOrders = sales.length;
    const averageOrderValue = totalOrders > 0 ? totalSales / totalOrders : 0;

    res.json({
      success: true,
      stats: {
        totalSales,
        totalOrders,
        averageOrderValue,
      },
    });
  } catch (error) {
    console.error('Error fetching sales stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch sales statistics',
    });
  }
});

// Get daily sales report
router.get('/daily-report', async (req, res) => {
  try {
    const { date } = req.query;
    const targetDate = date || new Date().toISOString().split('T')[0];

    const { data: sales, error } = await supabase
      .from('orders')
      .select('*')
      .eq('created_at::date', targetDate)
      .eq('status', 'paid');

    if (error) {
      throw error;
    }

    const hourlySales = Array.from({ length: 24 }, (_, hour) => {
      const hourSales = sales.filter(sale => {
        const saleHour = new Date(sale.created_at).getHours();
        return saleHour === hour;
      });

      return {
        hour: hour.toString().padStart(2, '0') + ':00',
        sales: hourSales.length,
        revenue: hourSales.reduce((sum, sale) => sum + sale.total_amount, 0),
      };
    });

    res.json({
      success: true,
      date: targetDate,
      hourlySales,
      totalSales: sales.length,
      totalRevenue: sales.reduce((sum, sale) => sum + sale.total_amount, 0),
    });
  } catch (error) {
    console.error('Error fetching daily report:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch daily report',
    });
  }
});

export default router;