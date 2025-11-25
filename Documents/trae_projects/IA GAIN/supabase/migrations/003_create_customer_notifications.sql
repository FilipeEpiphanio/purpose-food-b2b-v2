-- Criar tabela de notificações do cliente
CREATE TABLE IF NOT EXISTS customer_notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  type VARCHAR(50) NOT NULL CHECK (type IN ('availability', 'order_status', 'promotion', 'production')),
  data JSONB,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  CONSTRAINT fk_customer_notifications_customer 
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_customer_notifications_customer_id ON customer_notifications(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_notifications_created_at ON customer_notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_customer_notifications_read ON customer_notifications(customer_id, read);
CREATE INDEX IF NOT EXISTS idx_customer_notifications_type ON customer_notifications(type);

-- Criar política de segurança para RLS
ALTER TABLE customer_notifications ENABLE ROW LEVEL SECURITY;

-- Permitir que clientes vejam apenas suas próprias notificações
CREATE POLICY "Customers can view own notifications" ON customer_notifications
  FOR SELECT USING (auth.uid() = customer_id);

-- Permitir que clientes atualizem apenas suas próprias notificações
CREATE POLICY "Customers can update own notifications" ON customer_notifications
  FOR UPDATE USING (auth.uid() = customer_id);

-- Permitir inserção de notificações pelo sistema (service role)
CREATE POLICY "System can insert notifications" ON customer_notifications
  FOR INSERT WITH CHECK (true);

-- Conceder permissões aos papéis apropriados
GRANT SELECT ON customer_notifications TO anon, authenticated;
GRANT INSERT ON customer_notifications TO anon, authenticated;
GRANT UPDATE ON customer_notifications TO authenticated;