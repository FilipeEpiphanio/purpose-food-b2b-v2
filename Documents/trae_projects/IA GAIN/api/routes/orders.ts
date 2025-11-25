import express from 'express';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase with static config for production
const supabaseUrl = 'https://xqsocdvvvbgdgrezoqlf.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhxc29jZHZ2dmJnZGdyZXpvcWxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzYwNjAsImV4cCI6MjA3ODY1MjA2MH0.ZY-Flx5BoBI3vnSS_PfuxaWHpQEOeLSL8By8QVtGtEw';

const supabase = createClient(supabaseUrl, supabaseKey);

const router = express.Router();

/**
 * Create a new order with delivery scheduling
 * This endpoint saves orders to the database and creates calendar events for deliveries
 */
router.post('/', async (req, res) => {
  try {
    const {
      customer_name,
      customer_phone,
      delivery_address,
      status = 'pending',
      payment_method = 'cash',
      payment_status = 'pending',
      notes,
      needs_invoice = false,
      order_type = 'pickup'
    } = req.body;

    // Validate required fields - ajustado para campos que o frontend realmente envia
    if (!customer_name || !customer_phone || !delivery_address) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: customer_name, customer_phone, delivery_address'
      });
    }

    // Create order in database - ajustado para campos do frontend
    const orderData = {
      customer_name: customer_name,
      delivery_address: delivery_address,
      order_number: `PED-${String(Date.now()).slice(-6)}`,
      total_amount: 0, // Valor padrão, será atualizado quando adicionar itens
      status: status,
      payment_status: payment_status,
      payment_method: payment_method,
      order_type: order_type,
      notes: notes || `Cliente: ${customer_name} | Tel: ${customer_phone} | Endereço: ${delivery_address}`,
      needs_invoice: needs_invoice,
      delivery_date: new Date().toISOString(), // Data atual como data de entrega
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const { data: order, error: orderError } = await supabase
      .from('orders')
      .insert([orderData])
      .select()
      .single();

    if (orderError) {
      console.error('Error creating order:', orderError);
      return res.status(500).json({
        success: false,
        error: 'Failed to create order',
        details: orderError.message
      });
    }

    // Create calendar event for delivery
    const calendarEventData = {
      title: `Entrega - Pedido #${order.order_number.slice(-6)}`,
      description: `Cliente: ${customer_name} - ${notes || 'Entrega de pedido'}`,
      event_type: 'entrega',
      start_date: new Date().toISOString(),
      end_date: new Date(new Date().getTime() + 30 * 60 * 1000).toISOString(), // 30 min duration
      location: delivery_address,
      address: delivery_address,
      event_category: 'delivery',
      status: 'scheduled',
      sync_status: 'synced',
      created_by: '00000000-0000-0000-0000-000000000001',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const { data: calendarEvent, error: calendarError } = await supabase
      .from('calendar_events')
      .insert([calendarEventData])
      .select()
      .single();

    if (calendarError) {
      console.error('Error creating calendar event:', calendarError);
      // Continue even if calendar event fails - order is still created
    } else {
      console.log('✅ Calendar event created for delivery:', calendarEvent?.id);
    }

    console.log('✅ Order created successfully:', order.id);

    res.json({
      success: true,
      order,
      message: 'Order created successfully'
    });

  } catch (error) {
    console.error('Error creating order:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create order',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * Get orders with delivery scheduling
 */
router.get('/', async (req, res) => {
  try {
    const { start_date, end_date, status, order_type } = req.query;

    let query = supabase
      .from('orders')
      .select('*')
      .order('created_at', { ascending: false });

    // Filter by date range
    if (start_date) {
      query = query.gte('scheduled_date', start_date);
    }
    if (end_date) {
      query = query.lte('scheduled_date', end_date);
    }

    // Filter by status
    if (status) {
      query = query.eq('status', status);
    }

    // Filter by order type
    if (order_type) {
      query = query.eq('order_type', order_type);
    }

    const { data: orders, error } = await query;

    if (error) {
      return res.status(500).json({
        success: false,
        error: 'Failed to fetch orders',
        details: error.message
      });
    }

    res.json({
      success: true,
      orders: orders || [],
      count: orders?.length || 0
    });

  } catch (error) {
    console.error('Error fetching orders:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch orders',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * Get single order
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const { data: order, error } = await supabase
      .from('orders')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      return res.status(404).json({
        success: false,
        error: 'Order not found',
        details: error.message
      });
    }

    res.json({
      success: true,
      order
    });

  } catch (error) {
    console.error('Error fetching order:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch order',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * Update order
 */
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;

    const { data: order, error } = await supabase
      .from('orders')
      .update({
        ...updateData,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      return res.status(500).json({
        success: false,
        error: 'Failed to update order',
        details: error.message
      });
    }

    if (!order) {
      return res.status(404).json({
        success: false,
        error: 'Order not found'
      });
    }

    res.json({
      success: true,
      order,
      message: 'Order updated successfully'
    });

  } catch (error) {
    console.error('Error updating order:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update order',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * Delete order
 */
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const { error } = await supabase
      .from('orders')
      .delete()
      .eq('id', id);

    if (error) {
      return res.status(500).json({
        success: false,
        error: 'Failed to delete order',
        details: error.message
      });
    }

    res.json({
      success: true,
      message: 'Order deleted successfully'
    });

  } catch (error) {
    console.error('Error deleting order:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to delete order',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;