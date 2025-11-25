import { google, calendar_v3 } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import { supabase } from '../server';

export interface CalendarEvent {
  id?: string;
  title: string;
  description?: string;
  start_date: string; // ISO string
  end_date?: string; // ISO string
  all_day?: boolean;
  location?: string;
  address?: string;
  event_type: 'feira' | 'evento' | 'compromisso' | 'entrega' | 'reuniao';
  event_category?: 'food_fair' | 'corporate_event' | 'private_event' | 'delivery' | 'meeting' | 'other';
  expected_attendees?: number;
  products_to_bring?: string[];
  special_requirements?: string;
  estimated_revenue?: number;
  google_event_id?: string;
  google_calendar_id?: string;
  assigned_to?: string;
  created_by: string;
}

export interface GoogleCalendarEvent {
  id?: string;
  summary: string;
  description?: string;
  start: {
    dateTime?: string;
    date?: string;
    timeZone?: string;
  };
  end: {
    dateTime?: string;
    date?: string;
    timeZone?: string;
  };
  location?: string;
  attendees?: Array<{
    email: string;
    displayName?: string;
  }>;
  reminders?: {
    useDefault?: boolean;
    overrides?: Array<{
      method: 'email' | 'popup';
      minutes: number;
    }>;
  };
  colorId?: string;
  extendedProperties?: {
    private?: {
      [key: string]: string;
    };
    shared?: {
      [key: string]: string;
    };
  };
}

export class GoogleCalendarService {
  private calendar: calendar_v3.Calendar;

  constructor(authClient: OAuth2Client) {
    this.calendar = google.calendar({ version: 'v3', auth: authClient });
  }

  /**
   * Convert local event to Google Calendar event format
   */
  private localEventToGoogleEvent(event: CalendarEvent): GoogleCalendarEvent {
    const googleEvent: GoogleCalendarEvent = {
      summary: event.title,
      description: event.description,
      location: event.location || event.address,
      start: {},
      end: {},
      extendedProperties: {
        private: {
          event_type: event.event_type,
          event_category: event.event_category || 'other',
          expected_attendees: event.expected_attendees?.toString() || '0',
          products_to_bring: event.products_to_bring?.join(',') || '',
          special_requirements: event.special_requirements || '',
          estimated_revenue: event.estimated_revenue?.toString() || '0',
          local_event_id: event.id || ''
        }
      }
    };

    // Handle all-day events
    if (event.all_day) {
      const startDate = new Date(event.start_date);
      googleEvent.start.date = startDate.toISOString().split('T')[0];
      
      if (event.end_date) {
        const endDate = new Date(event.end_date);
        googleEvent.end.date = endDate.toISOString().split('T')[0];
      } else {
        // If no end date for all-day event, make it a single day event
        googleEvent.end.date = googleEvent.start.date;
      }
    } else {
      // Handle timed events
      googleEvent.start.dateTime = event.start_date;
      googleEvent.end.dateTime = event.end_date || event.start_date;
      googleEvent.start.timeZone = 'America/Sao_Paulo';
      googleEvent.end.timeZone = 'America/Sao_Paulo';
    }

    // Set reminders
    googleEvent.reminders = {
      useDefault: false,
      overrides: [
        { method: 'email', minutes: 60 }, // 1 hour before
        { method: 'popup', minutes: 30 }   // 30 minutes before
      ]
    };

    // Set color based on event type
    const colorMap: Record<string, string> = {
      'feira': '5',      // Yellow (for food fairs)
      'evento': '6',     // Orange (for events)
      'compromisso': '7', // Cyan (for appointments)
      'entrega': '8',    // Gray (for deliveries)
      'reuniao': '9'     // Blue (for meetings)
    };
    googleEvent.colorId = colorMap[event.event_type] || '1';

    return googleEvent;
  }

  /**
   * Convert Google Calendar event to local event format
   */
  private googleEventToLocalEvent(googleEvent: GoogleCalendarEvent): Partial<CalendarEvent> {
    const localEvent: Partial<CalendarEvent> = {
      title: googleEvent.summary || '',
      description: googleEvent.description,
      location: googleEvent.location,
      google_event_id: googleEvent.id,
      start_date: googleEvent.start?.dateTime || googleEvent.start?.date || '',
      end_date: googleEvent.end?.dateTime || googleEvent.end?.date || ''
    };

    // Extract extended properties
    if (googleEvent.extendedProperties?.private) {
      const props = googleEvent.extendedProperties.private;
      localEvent.event_type = props.event_type as CalendarEvent['event_type'];
      localEvent.event_category = props.event_category as CalendarEvent['event_category'];
      localEvent.expected_attendees = props.expected_attendees ? parseInt(props.expected_attendees) : undefined;
      localEvent.products_to_bring = props.products_to_bring ? props.products_to_bring.split(',') : undefined;
      localEvent.special_requirements = props.special_requirements;
      localEvent.estimated_revenue = props.estimated_revenue ? parseFloat(props.estimated_revenue) : undefined;
    }

    return localEvent;
  }

  /**
   * Create a new event in Google Calendar
   */
  async createGoogleEvent(event: CalendarEvent): Promise<string> {
    try {
      const googleEvent = this.localEventToGoogleEvent(event);
      
      const response = await this.calendar.events.insert({
        calendarId: event.google_calendar_id || 'primary',
        requestBody: googleEvent
      });

      return response.data.id!;
    } catch (error) {
      console.error('Error creating Google Calendar event:', error);
      throw new Error('Failed to create Google Calendar event');
    }
  }

  /**
   * Update an existing Google Calendar event
   */
  async updateGoogleEvent(googleEventId: string, event: CalendarEvent): Promise<void> {
    try {
      const googleEvent = this.localEventToGoogleEvent(event);
      
      await this.calendar.events.update({
        calendarId: event.google_calendar_id || 'primary',
        eventId: googleEventId,
        requestBody: googleEvent
      });
    } catch (error) {
      console.error('Error updating Google Calendar event:', error);
      throw new Error('Failed to update Google Calendar event');
    }
  }

  /**
   * Delete a Google Calendar event
   */
  async deleteGoogleEvent(googleEventId: string, calendarId: string = 'primary'): Promise<void> {
    try {
      await this.calendar.events.delete({
        calendarId: calendarId,
        eventId: googleEventId
      });
    } catch (error) {
      console.error('Error deleting Google Calendar event:', error);
      throw new Error('Failed to delete Google Calendar event');
    }
  }

  /**
   * Get events from Google Calendar
   */
  async getGoogleEvents(options: {
    calendarId?: string;
    timeMin?: string;
    timeMax?: string;
    maxResults?: number;
    singleEvents?: boolean;
    orderBy?: 'startTime' | 'updated';
  } = {}): Promise<calendar_v3.Schema$Event[]> {
    try {
      const response = await this.calendar.events.list({
        calendarId: options.calendarId || 'primary',
        timeMin: options.timeMin || new Date().toISOString(),
        timeMax: options.timeMax,
        maxResults: options.maxResults || 250,
        singleEvents: options.singleEvents !== false,
        orderBy: options.orderBy || 'startTime'
      });

      return response.data.items || [];
    } catch (error) {
      console.error('Error getting Google Calendar events:', error);
      throw new Error('Failed to get Google Calendar events');
    }
  }

  /**
   * Sync events from Google Calendar to local database
   */
  async syncFromGoogleCalendar(calendarId: string = 'primary'): Promise<number> {
    try {
      const googleEvents = await this.getGoogleEvents({ calendarId });
      let syncedCount = 0;

      for (const googleEvent of googleEvents) {
        if (!googleEvent.id) continue;

        // Check if event already exists in local database
        const { data: existingEvent } = await supabase
          .from('calendar_events')
          .select('id')
          .eq('google_event_id', googleEvent.id)
          .single();

        if (googleEvent.id && googleEvent.summary && googleEvent.start?.dateTime && googleEvent.end?.dateTime) {
          const localEventData = this.googleEventToLocalEvent(googleEvent as GoogleCalendarEvent);
        
          if (existingEvent) {
            // Update existing event
            const { error: updateError } = await supabase
              .from('calendar_events')
              .update({
                ...localEventData,
                sync_status: 'synced',
                last_sync_at: new Date().toISOString()
              })
              .eq('id', existingEvent.id);

            if (!updateError) syncedCount++;
          } else {
            // Create new event
            const { error: insertError } = await supabase
              .from('calendar_events')
              .insert([{
                ...localEventData,
                google_event_id: googleEvent.id,
                google_calendar_id: calendarId,
                sync_status: 'synced',
                last_sync_at: new Date().toISOString(),
                created_by: 'google-sync' // This should be replaced with actual user ID
              }]);

            if (!insertError) syncedCount++;
          }
        }
      }

      return syncedCount;
    } catch (error) {
      console.error('Error syncing from Google Calendar:', error);
      throw new Error('Failed to sync from Google Calendar');
    }
  }

  /**
   * Sync events from local database to Google Calendar
   */
  async syncToGoogleCalendar(): Promise<number> {
    try {
      // Get events that need to be synced
      const { data: events, error } = await supabase
        .from('calendar_events')
        .select('*')
        .or('sync_status.eq.pending,sync_status.eq.error')
        .limit(50);

      if (error) {
        throw new Error(`Failed to get events to sync: ${error.message}`);
      }

      let syncedCount = 0;

      for (const event of events || []) {
        try {
          if (event.google_event_id) {
            // Update existing Google Calendar event
            await this.updateGoogleEvent(event.google_event_id, event);
          } else {
            // Create new Google Calendar event
            const googleEventId = await this.createGoogleEvent(event);
            
            // Update local event with Google event ID
            const { error: updateError } = await supabase
              .from('calendar_events')
              .update({
                google_event_id: googleEventId,
                sync_status: 'synced',
                last_sync_at: new Date().toISOString(),
                sync_error: null
              })
              .eq('id', event.id);

            if (!updateError) syncedCount++;
          }
        } catch (error) {
          console.error(`Error syncing event ${event.id}:`, error);
          
          // Update sync error in database
          await supabase
            .from('calendar_events')
            .update({
              sync_status: 'error',
              sync_error: error instanceof Error ? error.message : 'Unknown error',
              last_sync_at: new Date().toISOString()
            })
            .eq('id', event.id);
        }
      }

      return syncedCount;
    } catch (error) {
      console.error('Error syncing to Google Calendar:', error);
      throw new Error('Failed to sync to Google Calendar');
    }
  }

  /**
   * Get available calendars
   */
  async getCalendars(): Promise<calendar_v3.Schema$CalendarListEntry[]> {
    try {
      const response = await this.calendar.calendarList.list();
      return response.data.items || [];
    } catch (error) {
      console.error('Error getting calendars:', error);
      throw new Error('Failed to get calendars');
    }
  }
}

export default GoogleCalendarService;