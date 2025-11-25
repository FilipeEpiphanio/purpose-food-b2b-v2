-- Script de teste para inserir eventos de exemplo no calendário
INSERT INTO calendar_events (
  id,
  title,
  type,
  description,
  start_date,
  end_date,
  location,
  notes,
  budget,
  attendees,
  user_id,
  sync_status,
  created_at,
  updated_at
) VALUES 
(
  gen_random_uuid(),
  'Feira da Praça Central',
  'feira',
  'Participação na feira mensal da praça central com nossos produtos gourmet',
  NOW() + INTERVAL '2 days',
  NOW() + INTERVAL '2 days 8 hours',
  'Praça Central - Centro',
  'Levar mesa, toalhas e display dos produtos',
  500.00,
  'João, Maria, Pedro',
  '123e4567-e89b-12d3-a456-426614174000',
  'not_synced',
  NOW(),
  NOW()
),
(
  gen_random_uuid(),
  'Reunião com Fornecedores',
  'reuniao',
  'Reunião mensal com fornecedores para revisar pedidos e novidades',
  NOW() + INTERVAL '1 day 14:00',
  NOW() + INTERVAL '1 day 16:00',
  'Escritório Purpose Food',
  'Preparar pauta da reunião',
  NULL,
  'Carlos, Ana',
  '123e4567-e89b-12d3-a456-426614174000',
  'not_synced',
  NOW(),
  NOW()
),
(
  gen_random_uuid(),
  'Entrega de Pedido Especial',
  'entrega',
  'Entrega de pedido de bolo personalizado para festa de casamento',
  NOW() + INTERVAL '3 days 18:00',
  NOW() + INTERVAL '3 days 19:00',
  'Salão de Festas Jardim',
  'Verificar endereço exato e ponto de referência',
  150.00,
  'Cliente: Fernanda',
  '123e4567-e89b-12d3-a456-426614174000',
  'not_synced',
  NOW(),
  NOW()
);

-- Verificar os eventos inseridos
SELECT 
  title,
  type,
  start_date,
  end_date,
  location,
  sync_status
FROM calendar_events 
WHERE user_id = '123e4567-e89b-12d3-a456-426614174000'
ORDER BY start_date;