-- Fix RLS policies for calendar_events table
-- Allow anonymous users to insert test data

-- Drop existing policies
DROP POLICY IF EXISTS "Anyone can view calendar events" ON public.calendar_events;
DROP POLICY IF EXISTS "Authenticated users can create events" ON public.calendar_events;
DROP POLICY IF EXISTS "Users can update their events" ON public.calendar_events;
DROP POLICY IF EXISTS "Users can delete their events" ON public.calendar_events;

-- Create more permissive policies for testing
-- Allow anyone to view events
CREATE POLICY "Anyone can view calendar events" ON public.calendar_events
    FOR SELECT USING (deleted_at IS NULL);

-- Allow anyone to create events (for testing)
CREATE POLICY "Anyone can create events" ON public.calendar_events
    FOR INSERT WITH CHECK (true);

-- Allow anyone to update events (for testing)
CREATE POLICY "Anyone can update events" ON public.calendar_events
    FOR UPDATE USING (true);

-- Allow anyone to delete events (for testing)
CREATE POLICY "Anyone can delete events" ON public.calendar_events
    FOR DELETE USING (true);

-- Grant all permissions to anon role
GRANT ALL PRIVILEGES ON public.calendar_events TO anon;
GRANT ALL PRIVILEGES ON public.upcoming_events TO anon;