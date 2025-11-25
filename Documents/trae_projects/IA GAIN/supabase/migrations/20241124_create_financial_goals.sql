-- Create financial_goals table
CREATE TABLE IF NOT EXISTS financial_goals (
    id UUID DEFAULT extensions.uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    target_amount NUMERIC NOT NULL,
    current_amount NUMERIC DEFAULT 0,
    deadline DATE NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Grant permissions
GRANT SELECT ON financial_goals TO anon;
GRANT SELECT ON financial_goals TO authenticated;
GRANT INSERT ON financial_goals TO authenticated;
GRANT UPDATE ON financial_goals TO authenticated;
GRANT DELETE ON financial_goals TO authenticated;

-- Enable RLS
ALTER TABLE financial_goals ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Allow authenticated users to read financial goals" ON financial_goals
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert financial goals" ON financial_goals
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update financial goals" ON financial_goals
    FOR UPDATE
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to delete financial goals" ON financial_goals
    FOR DELETE
    TO authenticated
    USING (true);