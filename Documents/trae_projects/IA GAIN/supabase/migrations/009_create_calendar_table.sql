-- Criar tabela calendar_events manualmente
CREATE TABLE IF NOT EXISTS calendar_events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL CHECK (type IN ('feira', 'evento', 'compromisso', 'entrega', 'reuniao')),
  description TEXT,
  start_date TIMESTAMP WITH TIME ZONE NOT NULL,
  end_date TIMESTAMP WITH TIME ZONE NOT NULL,
  location VARCHAR(255),
  notes TEXT,
  budget DECIMAL(10,2),
  attendees TEXT,
  user_id UUID NOT NULL,
  google_event_id VARCHAR(255),
  google_calendar_id VARCHAR(255),
  sync_status VARCHAR(50) DEFAULT 'not_synced' CHECK (sync_status IN ('synced', 'pending', 'failed', 'not_synced')),
  last_sync_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by VARCHAR(255)
);

-- Criar indexes
CREATE INDEX IF NOT EXISTS idx_calendar_events_user_id ON calendar_events(user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_start_date ON calendar_events(start_date);
CREATE INDEX IF NOT EXISTS idx_calendar_events_google_event_id ON calendar_events(google_event_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_sync_status ON calendar_events(sync_status);

-- Habilitar RLS
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;

-- Criar políticas RLS
CREATE POLICY "Users can view their own events" ON calendar_events
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own events" ON calendar_events
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own events" ON calendar_events
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own events" ON calendar_events
  FOR DELETE USING (auth.uid() = user_id);

-- Conceder permissões
GRANT SELECT ON calendar_events TO anon, authenticated;
GRANT INSERT ON calendar_events TO anon, authenticated;
GRANT UPDATE ON calendar_events TO anon, authenticated;
GRANT DELETE ON calendar_events TO anon, authenticated;

-- Inserir eventos de teste
INSERT INTO calendar_events (title, type, description, start_date, end_date, location, notes, budget, attendees, user_id, sync_status) VALUES 
('Feira da Praça Central', 'feira', 'Participação na feira mensal da praça central com nossos produtos gourmet', 
 NOW() + INTERVAL '2 days', NOW() + INTERVAL '2 days 8 hours', 'Praça Central - Centro', 
 'Levar mesa, toalhas e display dos produtos', 500.00, 'João, Maria, Pedro', 
 '123e4567-e89b-12d3-a456-426614174000', 'not_synced'),
('Reunião com Fornecedores', 'reuniao', 'Reunião mensal com fornecedores para revisar pedidos e novidades', 
 NOW() + INTERVAL '1 day 14:00', NOW() + INTERVAL '1 day 16:00', 'Escritório Purpose Food', 
 'Preparar pauta da reunião', NULL, 'Carlos, Ana', 
 '123e4567-e89b-12d3-a456-426614174000', 'not_synced'),
('Entrega de Pedido Especial', 'entrega', 'Entrega de pedido de bolo personalizado para festa de casamento', 
 NOW() + INTERVAL '3 days 18:00', NOW() + INTERVAL '3 days 19:00', 'Salão de Festas Jardim', 
 'Verificar endereço exato e ponto de referência', 150.00, 'Cliente: Fernanda', 
 '123e4567-e89b-12d3-a456-426614174000', 'not_synced');

-- Verificar os eventos criados
SELECT title, type, start_date, location, sync_status 
FROM calendar_events 
WHERE user_id = '123e4567-e89b-12d3-a456-426614174000'
ORDER BY start_date;