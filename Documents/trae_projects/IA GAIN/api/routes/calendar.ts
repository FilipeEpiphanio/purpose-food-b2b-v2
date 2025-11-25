import express from 'express';
import { supabase } from '../server';
import GoogleCalendarAuth from '../services/googleCalendarAuth';
import GoogleCalendarService, { CalendarEvent } from '../services/googleCalendarService';

const router = express.Router();

/**
 * Google Calendar Authentication Routes
 */

// Start Google OAuth flow
router.get('/auth', (req, res) => {
  try {
    const auth = new GoogleCalendarAuth();
    const authUrl = auth.generateAuthUrl();
    
    res.json({ 
      success: true, 
      authUrl,
      message: 'Redirect to this URL to authenticate with Google Calendar'
    });
  } catch (error) {
    console.error('Error generating auth URL:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to generate authentication URL',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Google OAuth callback
router.get('/auth/callback', async (req, res) => {
  try {
    const { code } = req.query;
    
    if (!code || typeof code !== 'string') {
      return res.status(400).json({ 
        success: false, 
        error: 'Authorization code is required' 
      });
    }

    const auth = new GoogleCalendarAuth();
    const tokens = await auth.exchangeCodeForTokens(code);

    // Store tokens in database (you should associate with user)
    // For now, we'll store them in a temporary table or return them
    const { error } = await supabase
      .from('google_calendar_tokens')
      .upsert({
        id: 'default', // You should use user ID here
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        expiry_date: tokens.expiry_date,
        scope: tokens.scope,
        token_type: tokens.token_type,
        updated_at: new Date().toISOString()
      });

    if (error) {
      console.error('Error storing tokens:', error);
      return res.status(500).json({ 
        success: false, 
        error: 'Failed to store authentication tokens' 
      });
    }

    res.json({ 
      success: true, 
      message: 'Google Calendar authentication successful',
      tokens: {
        access_token: tokens.access_token,
        scope: tokens.scope,
        token_type: tokens.token_type
      }
    });
  } catch (error) {
    console.error('Error in OAuth callback:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Authentication failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * Calendar Events Routes
 */

// Get all calendar events - unifies calendar events and delivery orders
router.get('/events', async (req, res) => {
  try {
    // Get calendar events
    const { data: calendarEvents, error: calendarError } = await supabase
      .from('calendar_events')
      .select('*')
      .order('start_date', { ascending: true });

    if (calendarError) {
      return res.status(500).json({ 
        success: false, 
        error: 'Failed to fetch calendar events',
        details: calendarError.message 
      });
    }

    // Get delivery orders with scheduled dates for the current month
    const startOfMonth = new Date();
    startOfMonth.setDate(1);
    startOfMonth.setHours(0, 0, 0, 0);
    
    const endOfMonth = new Date(startOfMonth);
    endOfMonth.setMonth(endOfMonth.getMonth() + 1);

    const { data: deliveryOrders, error: ordersError } = await supabase
      .from('orders')
      .select('id, customer_name, delivery_address, scheduled_date, delivery_date, order_type, status, total_amount, created_at, updated_at')
      .eq('order_type', 'delivery')
      .not('scheduled_date', 'is', null)
      .gte('scheduled_date', startOfMonth.toISOString())
      .lt('scheduled_date', endOfMonth.toISOString())
      .order('scheduled_date', { ascending: true });

    if (ordersError) {
      console.error('Error fetching delivery orders:', ordersError);
      // Continue with calendar events only if orders fail
    }

    // Convert delivery orders to calendar event format
    const deliveryEvents = (deliveryOrders || []).map(order => ({
      id: `order_${order.id}`,
      title: `Entrega - Pedido #${order.id.slice(-6)}`,
      description: `Cliente: ${order.customer_name}`,
      event_type: 'entrega',
      start_date: order.scheduled_date,
      end_date: order.delivery_date || new Date(new Date(order.scheduled_date).getTime() + 30 * 60 * 1000).toISOString(), // Default 30 min duration
      location: order.delivery_address,
      address: order.delivery_address,
      status: order.status === 'delivered' ? 'completed' : 'scheduled',
      google_event_id: null,
      google_calendar_id: 'primary',
      sync_status: 'synced',
      created_by: '00000000-0000-0000-0000-000000000001',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }));

    // Combine all events
    const allEvents = [
      ...(calendarEvents || []),
      ...deliveryEvents
    ].sort((a, b) => new Date(a.start_date).getTime() - new Date(b.start_date).getTime());

    res.json({ 
      success: true, 
      events: allEvents,
      count: allEvents.length,
      sources: {
        calendar: calendarEvents?.length || 0,
        deliveries: deliveryOrders?.length || 0
      }
    });
  } catch (error) {
    console.error('Error fetching calendar events:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch calendar events',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get upcoming events - unifies calendar events and delivery orders
router.get('/events/upcoming', async (req, res) => {
  try {
    // Get calendar events
    const { data: calendarEvents, error: calendarError } = await supabase
      .from('calendar_events')
      .select('*')
      .gte('start_date', new Date().toISOString())
      .order('start_date', { ascending: true });

    if (calendarError) {
      return res.status(500).json({ 
        success: false, 
        error: 'Failed to fetch calendar events',
        details: calendarError.message 
      });
    }

    // Get delivery orders with scheduled dates
    const { data: deliveryOrders, error: ordersError } = await supabase
      .from('orders')
      .select('id, customer_name, delivery_address, scheduled_date, delivery_date, order_type, status, total_amount')
      .eq('order_type', 'delivery')
      .not('scheduled_date', 'is', null)
      .gte('scheduled_date', new Date().toISOString())
      .order('scheduled_date', { ascending: true });

    if (ordersError) {
      console.error('Error fetching delivery orders:', ordersError);
      // Continue with calendar events only if orders fail
    }

    // Convert delivery orders to calendar event format
    const deliveryEvents = (deliveryOrders || []).map(order => ({
      id: `order_${order.id}`,
      title: `Entrega - Pedido #${order.id.slice(-6)}`,
      description: `Cliente: ${order.customer_name}`,
      event_type: 'entrega',
      start_date: order.scheduled_date,
      end_date: order.delivery_date || new Date(new Date(order.scheduled_date).getTime() + 30 * 60 * 1000).toISOString(), // Default 30 min duration
      location: order.delivery_address,
      address: order.delivery_address,
      status: order.status === 'delivered' ? 'completed' : 'scheduled',
      google_event_id: null,
      google_calendar_id: 'primary',
      sync_status: 'synced',
      created_by: '00000000-0000-0000-0000-000000000001',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }));

    // Combine and sort all events
    const allEvents = [
      ...(calendarEvents || []),
      ...deliveryEvents
    ].sort((a, b) => new Date(a.start_date).getTime() - new Date(b.start_date).getTime());

    // Limit to 5 upcoming events
    const upcomingEvents = allEvents.slice(0, 5);

    res.json({ 
      success: true, 
      events: upcomingEvents,
      count: upcomingEvents.length,
      sources: {
        calendar: calendarEvents?.length || 0,
        deliveries: deliveryOrders?.length || 0
      }
    });
  } catch (error) {
    console.error('Error fetching upcoming events:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch upcoming events',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get single event
router.get('/events/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const { data: event, error } = await supabase
      .from('calendar_events')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      return res.status(404).json({ 
        success: false, 
        error: 'Event not found',
        details: error.message 
      });
    }

    res.json({ 
      success: true, 
      event 
    });
  } catch (error) {
    console.error('Error fetching event:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch event',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Create new calendar event
router.post('/events', async (req, res) => {
  try {
    const eventData: CalendarEvent = req.body;
    
    // Validate required fields
    if (!eventData.title || !eventData.start_date || !eventData.event_type) {
      return res.status(400).json({ 
        success: false, 
        error: 'Title, start_date, and event_type are required' 
      });
    }

    // Get user ID from request (you should implement proper authentication)
    const userId = req.headers['user-id'] || 'default-user-id';

    const eventDataWithUser = {
      ...eventData,
      created_by: userId,
      assigned_to: eventData.assigned_to || userId
    };

    const { data: event, error } = await supabase
      .from('calendar_events')
      .insert([eventDataWithUser])
      .select()
      .single();

    if (error) {
      return res.status(500).json({ 
        success: false, 
        error: 'Failed to create calendar event',
        details: error.message 
      });
    }

    // Try to sync with Google Calendar if authenticated
    try {
      const { data: tokens } = await supabase
        .from('google_calendar_tokens')
        .select('*')
        .single();

      if (tokens) {
        const auth = new GoogleCalendarAuth();
        const authClient = await auth.getAuthenticatedClient(tokens);
        const calendarService = new GoogleCalendarService(authClient);
        
        const googleEventId = await calendarService.createGoogleEvent(event);
        
        // Update event with Google event ID
        await supabase
          .from('calendar_events')
          .update({
            google_event_id: googleEventId,
            sync_status: 'synced',
            last_sync_at: new Date().toISOString()
          })
          .eq('id', event.id);
      }
    } catch (syncError) {
      console.error('Error syncing with Google Calendar:', syncError);
      // Don't fail the request if sync fails
    }

    res.json({ 
      success: true, 
      event,
      message: 'Calendar event created successfully'
    });
  } catch (error) {
    console.error('Error creating calendar event:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to create calendar event',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Update calendar event
router.put('/events/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;

    const { data: event, error } = await supabase
      .from('calendar_events')
      .update({
        ...updateData,
        updated_at: new Date().toISOString(),
        sync_status: 'pending' // Mark for re-sync
      })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      return res.status(500).json({ 
        success: false, 
        error: 'Failed to update calendar event',
        details: error.message 
      });
    }

    // Try to sync with Google Calendar if event has Google event ID
    if (event.google_event_id) {
      try {
        const { data: tokens } = await supabase
          .from('google_calendar_tokens')
          .select('*')
          .single();

        if (tokens) {
          const auth = new GoogleCalendarAuth();
          const authClient = await auth.getAuthenticatedClient(tokens);
          const calendarService = new GoogleCalendarService(authClient);
          
          await calendarService.updateGoogleEvent(event.google_event_id, event);
          
          // Update sync status
          await supabase
            .from('calendar_events')
            .update({
              sync_status: 'synced',
              last_sync_at: new Date().toISOString()
            })
            .eq('id', id);
        }
      } catch (syncError) {
        console.error('Error syncing with Google Calendar:', syncError);
      }
    }

    res.json({ 
      success: true, 
      event,
      message: 'Calendar event updated successfully'
    });
  } catch (error) {
    console.error('Error updating calendar event:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to update calendar event',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Delete calendar event
router.delete('/events/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Get event first to check if it has Google event ID
    const { data: event } = await supabase
      .from('calendar_events')
      .select('google_event_id, google_calendar_id')
      .eq('id', id)
      .single();

    // Try to delete from Google Calendar if synced
    if (event?.google_event_id) {
      try {
        const { data: tokens } = await supabase
          .from('google_calendar_tokens')
          .select('*')
          .single();

        if (tokens) {
          const auth = new GoogleCalendarAuth();
          const authClient = await auth.getAuthenticatedClient(tokens);
          const calendarService = new GoogleCalendarService(authClient);
          
          await calendarService.deleteGoogleEvent(
            event.google_event_id,
            event.google_calendar_id || 'primary'
          );
        }
      } catch (syncError) {
        console.error('Error deleting from Google Calendar:', syncError);
      }
    }

    // Delete from local database
    const { error } = await supabase
      .from('calendar_events')
      .delete()
      .eq('id', id);

    if (error) {
      return res.status(500).json({ 
        success: false, 
        error: 'Failed to delete calendar event',
        details: error.message 
      });
    }

    res.json({ 
      success: true, 
      message: 'Calendar event deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting calendar event:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to delete calendar event',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * Calendar Sync Routes
 */

// Sync events from Google Calendar
router.post('/sync/from-google', async (req, res) => {
  try {
    const { calendarId = 'primary' } = req.body;

    const { data: tokens } = await supabase
      .from('google_calendar_tokens')
      .select('*')
      .single();

    if (!tokens) {
      return res.status(401).json({ 
        success: false, 
        error: 'Google Calendar not authenticated' 
      });
    }

    const auth = new GoogleCalendarAuth();
    const authClient = await auth.getAuthenticatedClient(tokens);
    const calendarService = new GoogleCalendarService(authClient);
    
    const syncedCount = await calendarService.syncFromGoogleCalendar(calendarId);

    res.json({ 
      success: true, 
      syncedCount,
      message: `Successfully synced ${syncedCount} events from Google Calendar`
    });
  } catch (error) {
    console.error('Error syncing from Google Calendar:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to sync from Google Calendar',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Sync events to Google Calendar
router.post('/sync/to-google', async (req, res) => {
  try {
    const { data: tokens } = await supabase
      .from('google_calendar_tokens')
      .select('*')
      .single();

    if (!tokens) {
      return res.status(401).json({ 
        success: false, 
        error: 'Google Calendar not authenticated' 
      });
    }

    const auth = new GoogleCalendarAuth();
    const authClient = await auth.getAuthenticatedClient(tokens);
    const calendarService = new GoogleCalendarService(authClient);
    
    const syncedCount = await calendarService.syncToGoogleCalendar();

    res.json({ 
      success: true, 
      syncedCount,
      message: `Successfully synced ${syncedCount} events to Google Calendar`
    });
  } catch (error) {
    console.error('Error syncing to Google Calendar:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to sync to Google Calendar',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get available calendars
router.get('/calendars', async (req, res) => {
  try {
    const { data: tokens } = await supabase
      .from('google_calendar_tokens')
      .select('*')
      .single();

    if (!tokens) {
      return res.status(401).json({ 
        success: false, 
        error: 'Google Calendar not authenticated' 
      });
    }

    const auth = new GoogleCalendarAuth();
    const authClient = await auth.getAuthenticatedClient(tokens);
    const calendarService = new GoogleCalendarService(authClient);
    
    const calendars = await calendarService.getCalendars();

    res.json({ 
      success: true, 
      calendars,
      count: calendars.length
    });
  } catch (error) {
    console.error('Error getting calendars:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to get calendars',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
