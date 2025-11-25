-- Fix Dashboard Schema Issues
-- This migration creates missing tables and columns needed for dashboard functionality

-- Create financial_records table
CREATE TABLE IF NOT EXISTS public.financial_records (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    record_type VARCHAR(50) NOT NULL, -- 'revenue', 'expense', 'investment'
    category VARCHAR(100) NOT NULL,
    description TEXT,
    amount DECIMAL(10,2) NOT NULL,
    transaction_date DATE NOT NULL,
    payment_method VARCHAR(50),
    reference_id UUID, -- Reference to orders, invoices, etc.
    reference_type VARCHAR(50), -- 'order', 'invoice', 'manual'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add order_date column to orders table
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS order_date DATE DEFAULT CURRENT_DATE;

-- Add status column to customers table
ALTER TABLE public.customers 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' 
CHECK (status IN ('active', 'inactive', 'blocked'));

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_financial_records_date ON public.financial_records(transaction_date);
CREATE INDEX IF NOT EXISTS idx_financial_records_type ON public.financial_records(record_type);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_customers_status ON public.customers(status);

-- Grant permissions to financial_records table
GRANT SELECT ON public.financial_records TO anon;
GRANT ALL PRIVILEGES ON public.financial_records TO authenticated;

-- Update existing orders with order_date if null
UPDATE public.orders 
SET order_date = created_at::date 
WHERE order_date IS NULL;

-- Update existing customers with status if null
UPDATE public.customers 
SET status = 'active' 
WHERE status IS NULL;

-- Create function to automatically update financial records
CREATE OR REPLACE FUNCTION update_financial_record()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Insert revenue record for new orders
        IF NEW.status = 'completed' THEN
            INSERT INTO public.financial_records (
                record_type, 
                category, 
                description, 
                amount, 
                transaction_date, 
                reference_id, 
                reference_type
            ) VALUES (
                'revenue',
                'Sales Revenue',
                CONCAT('Order #', NEW.order_number),
                NEW.total_amount,
                NEW.order_date,
                NEW.id,
                'order'
            );
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Update financial record when order status changes
        IF OLD.status != NEW.status AND NEW.status = 'completed' THEN
            INSERT INTO public.financial_records (
                record_type, 
                category, 
                description, 
                amount, 
                transaction_date, 
                reference_id, 
                reference_type
            ) VALUES (
                'revenue',
                'Sales Revenue',
                CONCAT('Order #', NEW.order_number),
                NEW.total_amount,
                NEW.order_date,
                NEW.id,
                'order'
            );
        END IF;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic financial record updates
DROP TRIGGER IF EXISTS update_financial_record_trigger ON public.orders;
CREATE TRIGGER update_financial_record_trigger
    AFTER INSERT OR UPDATE OF status ON public.orders
    FOR EACH ROW
    EXECUTE FUNCTION update_financial_record();

-- Insert sample financial data for testing
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

-- Create view for dashboard financial summary
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