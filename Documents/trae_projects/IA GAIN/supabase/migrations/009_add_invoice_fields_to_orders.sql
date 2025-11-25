-- Adicionar campos de controle de nota fiscal na tabela orders
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS needs_invoice BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS invoice_issued BOOLEAN DEFAULT FALSE;

-- Adicionar comentários para documentação
COMMENT ON COLUMN orders.needs_invoice IS 'Indica se o pedido precisa de nota fiscal';
COMMENT ON COLUMN orders.invoice_issued IS 'Indica se a nota fiscal já foi emitida para este pedido';

-- Criar índice para melhorar performance em consultas
CREATE INDEX IF NOT EXISTS idx_orders_needs_invoice ON orders(needs_invoice);
CREATE INDEX IF NOT EXISTS idx_orders_invoice_issued ON orders(invoice_issued);

-- Atualizar pedidos existentes que podem precisar de nota fiscal
-- (baseado em valor ou tipo de cliente - ajustar conforme necessário)
UPDATE orders 
SET needs_invoice = TRUE 
WHERE total_amount > 100.00 
  AND needs_invoice IS NULL;