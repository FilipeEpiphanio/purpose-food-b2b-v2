-- Fix calendar_events table to allow testing
-- Make created_by field nullable for testing purposes

ALTER TABLE public.calendar_events 
ALTER COLUMN created_by DROP NOT NULL;

-- Also make assigned_to nullable for flexibility
ALTER TABLE public.calendar_events 
ALTER COLUMN assigned_to DROP NOT NULL;

-- Create a function to set created_by automatically if not provided
CREATE OR REPLACE FUNCTION set_default_created_by()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.created_by IS NULL THEN
        NEW.created_by = '00000000-0000-0000-0000-000000000001'::uuid;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically set created_by
DROP TRIGGER IF EXISTS trigger_set_default_created_by ON public.calendar_events;
CREATE TRIGGER trigger_set_default_created_by
    BEFORE INSERT ON public.calendar_events
    FOR EACH ROW
    EXECUTE FUNCTION set_default_created_by();

