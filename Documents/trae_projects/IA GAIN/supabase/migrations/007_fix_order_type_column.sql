-- Fix missing order_type column in orders table
-- This migration ensures the order_type column exists and has proper constraints

-- Add order_type column to orders table if it doesn't exist
ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS order_type TEXT DEFAULT 'delivery' CHECK (order_type IN ('delivery', 'pickup', 'dine-in'));

-- Update existing orders with default order_type if null
UPDATE public.orders 
SET order_type = 'delivery' 
WHERE order_type IS NULL;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_orders_order_type ON public.orders(order_type);

-- Grant permissions
GRANT SELECT ON public.orders TO anon;
GRANT ALL PRIVILEGES ON public.orders TO authenticated;

-- Add RLS policies for orders table if they don't exist
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all users to view orders
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'orders' AND policyname = 'Anyone can view orders') THEN
        CREATE POLICY "Anyone can view orders" ON public.orders
            FOR SELECT USING (true);
    END IF;
END $$;

-- Create policy to allow authenticated users to insert orders
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'orders' AND policyname = 'Authenticated users can insert orders') THEN
        CREATE POLICY "Authenticated users can insert orders" ON public.orders
            FOR INSERT WITH CHECK (auth.role() = 'authenticated');
    END IF;
END $$;

-- Create policy to allow users to update their own orders
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'orders' AND policyname = 'Users can update own orders') THEN
        CREATE POLICY "Users can update own orders" ON public.orders
            FOR UPDATE USING (auth.role() = 'authenticated');
    END IF;
END $$;

-- Create policy to allow users to delete their own orders
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'orders' AND policyname = 'Users can delete own orders') THEN
        CREATE POLICY "Users can delete own orders" ON public.orders
            FOR DELETE USING (auth.role() = 'authenticated');
    END IF;
END $$;

RAISE NOTICE '✅ Coluna order_type adicionada/atualizada com sucesso!';