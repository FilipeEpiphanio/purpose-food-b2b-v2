-- Create google_calendar_tokens table for storing Google Calendar authentication tokens
CREATE TABLE IF NOT EXISTS public.google_calendar_tokens (
    id TEXT PRIMARY KEY DEFAULT 'default',
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expiry_date BIGINT,
    scope TEXT,
    token_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Enable RLS
ALTER TABLE public.google_calendar_tokens ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow public read access" ON public.google_calendar_tokens
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access" ON public.google_calendar_tokens
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update access" ON public.google_calendar_tokens
    FOR UPDATE USING (true);

CREATE POLICY "Allow public delete access" ON public.google_calendar_tokens
    FOR DELETE USING (true);

-- Grant permissions
GRANT ALL ON public.google_calendar_tokens TO anon;
GRANT ALL ON public.google_calendar_tokens TO authenticated;