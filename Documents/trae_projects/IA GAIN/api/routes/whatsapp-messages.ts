import { Router } from 'express';
import { supabase } from '../server.js';

const router = Router();

// List all WhatsApp messages
router.get('/', async (req, res) => {
  try {
    const { data, error } = await supabase
      .from('whatsapp_messages')
      .select('*')
      .order('sent_at', { ascending: false });

    if (error) {
      console.error('Error fetching WhatsApp messages:', error);
      return res.status(500).json({ error: 'Failed to fetch WhatsApp messages' });
    }

    // Transform data to match frontend interface
    const transformedMessages = data.map(message => ({
      id: message.id,
      customerName: message.customer_name,
      phone: message.phone,
      message: message.message,
      status: message.status,
      sentAt: message.sent_at
    }));

    res.json(transformedMessages);
  } catch (error) {
    console.error('Error in whatsapp-messages route:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create a new WhatsApp message
router.post('/', async (req, res) => {
  try {
    const { customerName, phone, message } = req.body;

    if (!customerName || !phone || !message) {
      return res.status(400).json({ error: 'Customer name, phone, and message are required' });
    }

    const messageData = {
      customer_name: customerName,
      phone,
      message,
      status: 'sent',
      sent_at: new Date().toISOString()
    };

    const { data, error } = await supabase
      .from('whatsapp_messages')
      .insert([messageData])
      .select()
      .single();

    if (error) {
      console.error('Error creating WhatsApp message:', error);
      return res.status(500).json({ error: 'Failed to create WhatsApp message' });
    }

    // Transform data to match frontend interface
    const transformedMessage = {
      id: data.id,
      customerName: data.customer_name,
      phone: data.phone,
      message: data.message,
      status: data.status,
      sentAt: data.sent_at
    };

    res.status(201).json(transformedMessage);
  } catch (error) {
    console.error('Error in whatsapp-messages route:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update a WhatsApp message status
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    if (!status) {
      return res.status(400).json({ error: 'Status is required' });
    }

    const { data, error } = await supabase
      .from('whatsapp_messages')
      .update({ status })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating WhatsApp message:', error);
      return res.status(500).json({ error: 'Failed to update WhatsApp message' });
    }

    if (!data) {
      return res.status(404).json({ error: 'WhatsApp message not found' });
    }

    // Transform data to match frontend interface
    const transformedMessage = {
      id: data.id,
      customerName: data.customer_name,
      phone: data.phone,
      message: data.message,
      status: data.status,
      sentAt: data.sent_at
    };

    res.json(transformedMessage);
  } catch (error) {
    console.error('Error in whatsapp-messages route:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete a WhatsApp message
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const { error } = await supabase
      .from('whatsapp_messages')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting WhatsApp message:', error);
      return res.status(500).json({ error: 'Failed to delete WhatsApp message' });
    }

    res.status(204).send();
  } catch (error) {
    console.error('Error in whatsapp-messages route:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;