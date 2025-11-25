-- Database Schema Fixes for Dashboard
-- Run these commands in your Supabase SQL Editor

-- 1. Create financial_records table
CREATE TABLE IF NOT EXISTS public.financial_records (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    record_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    amount DECIMAL(10,2) NOT NULL,
    transaction_date DATE NOT NULL,
    payment_method VARCHAR(50),
    reference_id UUID,
    reference_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Add order_date column to orders table
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS order_date DATE DEFAULT CURRENT_DATE;

-- 3. Add status column to customers table
ALTER TABLE public.customers 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' 
CHECK (status IN ('active', 'inactive', 'blocked'));

-- 4. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_financial_records_date ON public.financial_records(transaction_date);
CREATE INDEX IF NOT EXISTS idx_financial_records_type ON public.financial_records(record_type);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);

-- 5. Grant permissions
GRANT SELECT ON public.financial_records TO anon;
GRANT ALL PRIVILEGES ON public.financial_records TO authenticated;

-- 6. Update existing data with proper defaults
UPDATE public.orders 
SET order_date = created_at::date 
WHERE order_date IS NULL;

UPDATE public.customers 
SET status = 'active' 
WHERE status IS NULL;

-- 7. Insert sample financial data for testing
INSERT INTO public.financial_records (
    record_type, 
    category, 
    description, 
    amount, 
    transaction_date, 
    payment_method
) VALUES 
    ('revenue', 'Sales Revenue', 'Monthly Sales', 15000.00, CURRENT_DATE - INTERVAL '30 days', 'multiple'),
    ('revenue', 'Sales Revenue', 'Monthly Sales', 18000.00, CURRENT_DATE - INTERVAL '60 days', 'multiple'),
    ('expense', 'Operating Costs', 'Raw Materials', 5000.00, CURRENT_DATE - INTERVAL '15 days', 'bank_transfer'),
    ('expense', 'Operating Costs', 'Utilities', 800.00, CURRENT_DATE - INTERVAL '10 days', 'bank_transfer'),
    ('revenue', 'Sales Revenue', 'Monthly Sales', 22000.00, CURRENT_DATE, 'multiple');

-- 8. Create view for dashboard financial summary
CREATE OR REPLACE VIEW public.dashboard_financial_summary AS
SELECT 
    DATE_TRUNC('month', transaction_date) as month,
    SUM(CASE WHEN record_type = 'revenue' THEN amount ELSE 0 END) as total_revenue,
    SUM(CASE WHEN record_type = 'expense' THEN amount ELSE 0 END) as total_expenses,
    SUM(CASE WHEN record_type = 'revenue' THEN amount ELSE -amount END) as net_profit
FROM public.financial_records
WHERE transaction_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY month DESC;

-- 9. Check if fixes were applied successfully
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'financial_records';
SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'orders' AND column_name = 'order_date';
SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'customers' AND column_name = 'status';