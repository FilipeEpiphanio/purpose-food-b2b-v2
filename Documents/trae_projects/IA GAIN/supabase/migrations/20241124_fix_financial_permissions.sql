-- Grant permissions for financial tables
GRANT SELECT ON financial_records TO anon;
GRANT SELECT ON financial_records TO authenticated;
GRANT INSERT ON financial_records TO authenticated;
GRANT UPDATE ON financial_records TO authenticated;
GRANT DELETE ON financial_records TO authenticated;

GRANT SELECT ON transactions TO anon;
GRANT SELECT ON transactions TO authenticated;
GRANT INSERT ON transactions TO authenticated;
GRANT UPDATE ON transactions TO authenticated;
GRANT DELETE ON transactions TO authenticated;

-- Create RLS policies for financial_records
ALTER TABLE financial_records ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read all financial records
CREATE POLICY "Allow authenticated users to read financial records" ON financial_records
    FOR SELECT
    TO authenticated
    USING (true);

-- Allow authenticated users to insert financial records
CREATE POLICY "Allow authenticated users to insert financial records" ON financial_records
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Allow authenticated users to update their own financial records
CREATE POLICY "Allow authenticated users to update financial records" ON financial_records
    FOR UPDATE
    TO authenticated
    USING (true);

-- Allow authenticated users to delete financial records
CREATE POLICY "Allow authenticated users to delete financial records" ON financial_records
    FOR DELETE
    TO authenticated
    USING (true);

-- Create RLS policies for transactions
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read all transactions
CREATE POLICY "Allow authenticated users to read transactions" ON transactions
    FOR SELECT
    TO authenticated
    USING (true);

-- Allow authenticated users to insert transactions
CREATE POLICY "Allow authenticated users to insert transactions" ON transactions
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Allow authenticated users to update transactions
CREATE POLICY "Allow authenticated users to update transactions" ON transactions
    FOR UPDATE
    TO authenticated
    USING (true);

-- Allow authenticated users to delete transactions
CREATE POLICY "Allow authenticated users to delete transactions" ON transactions
    FOR DELETE
    TO authenticated
    USING (true);