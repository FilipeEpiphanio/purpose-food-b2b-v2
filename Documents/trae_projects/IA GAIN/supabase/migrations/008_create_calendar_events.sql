-- Create calendar events table for Purpose Food scheduling
-- This table stores events, feiras, and compromissos with Google Calendar sync

CREATE TABLE public.calendar_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    event_type TEXT NOT NULL CHECK (event_type IN ('feira', 'evento', 'compromisso', 'entrega', 'reuniao')),
    
    -- Date and time fields
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    all_day BOOLEAN DEFAULT false,
    
    -- Location information
    location TEXT,
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Google Calendar sync fields
    google_event_id TEXT,
    google_calendar_id TEXT DEFAULT 'primary',
    sync_status TEXT DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'error', 'deleted')),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_error TEXT,
    
    -- Event details specific to Purpose Food
    event_category TEXT CHECK (event_category IN ('food_fair', 'corporate_event', 'private_event', 'delivery', 'meeting', 'other')),
    expected_attendees INTEGER DEFAULT 0,
    products_to_bring TEXT[], -- Array of product names
    special_requirements TEXT,
    
    -- Financial tracking
    estimated_revenue DECIMAL(10, 2),
    actual_revenue DECIMAL(10, 2),
    expenses DECIMAL(10, 2) DEFAULT 0,
    
    -- Status and workflow
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled')),
    
    -- User assignment
    assigned_to UUID REFERENCES auth.users(id),
    created_by UUID NOT NULL REFERENCES auth.users(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_calendar_events_start_date ON public.calendar_events(start_date);
CREATE INDEX idx_calendar_events_event_type ON public.calendar_events(event_type);
CREATE INDEX idx_calendar_events_status ON public.calendar_events(status);
CREATE INDEX idx_calendar_events_google_event_id ON public.calendar_events(google_event_id);
CREATE INDEX idx_calendar_events_assigned_to ON public.calendar_events(assigned_to);
CREATE INDEX idx_calendar_events_created_by ON public.calendar_events(created_by);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_calendar_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER trigger_update_calendar_events_updated_at
    BEFORE UPDATE ON public.calendar_events
    FOR EACH ROW
    EXECUTE FUNCTION update_calendar_events_updated_at();

-- Create view for upcoming events
CREATE VIEW public.upcoming_events AS
SELECT 
    id,
    title,
    description,
    event_type,
    start_date,
    end_date,
    location,
    address,
    status,
    event_category,
    expected_attendees,
    estimated_revenue,
    google_event_id,
    sync_status
FROM public.calendar_events
WHERE deleted_at IS NULL
    AND start_date >= NOW() - INTERVAL '1 day'
    AND status != 'cancelled'
ORDER BY start_date ASC;

-- Enable RLS
ALTER TABLE public.calendar_events ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view all events
CREATE POLICY "Anyone can view calendar events" ON public.calendar_events
    FOR SELECT USING (deleted_at IS NULL);

-- Authenticated users can create events
CREATE POLICY "Authenticated users can create events" ON public.calendar_events
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Users can update events they created or are assigned to
CREATE POLICY "Users can update their events" ON public.calendar_events
    FOR UPDATE USING (
        auth.uid() = created_by OR 
        auth.uid() = assigned_to OR
        auth.role() = 'authenticated'
    );

-- Users can delete events they created
CREATE POLICY "Users can delete their events" ON public.calendar_events
    FOR DELETE USING (auth.uid() = created_by);

-- Grant permissions
GRANT SELECT ON public.calendar_events TO anon;
GRANT ALL PRIVILEGES ON public.calendar_events TO authenticated;
GRANT SELECT ON public.upcoming_events TO anon;
GRANT SELECT ON public.upcoming_events TO authenticated;

-- Create function to sync with Google Calendar
CREATE OR REPLACE FUNCTION sync_event_with_google(event_id UUID)
RETURNS TEXT AS $$
DECLARE
    event_record public.calendar_events%ROWTYPE;
    sync_result TEXT;
BEGIN
    SELECT * INTO event_record FROM public.calendar_events WHERE id = event_id;
    
    IF NOT FOUND THEN
        RETURN 'Event not found';
    END IF;
    
    -- Update sync status
    UPDATE public.calendar_events 
    SET sync_status = 'pending', last_sync_at = NOW()
    WHERE id = event_id;
    
    sync_result := 'Sync initiated for event: ' || event_record.title;
    RETURN sync_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;