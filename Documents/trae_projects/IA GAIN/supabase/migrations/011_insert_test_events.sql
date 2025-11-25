-- Fix the trigger for setting created_by automatically
DROP TRIGGER IF EXISTS trigger_set_default_created_by ON public.calendar_events;

-- Create a simpler approach - just insert directly with a default UUID
INSERT INTO public.calendar_events (
    title,
    description,
    event_type,
    start_date,
    end_date,
    location,
    address,
    status,
    created_by
) VALUES 
(
    'Feira de Alimentos Orgânicos - Centro',
    'Feira semanal com produtos frescos e orgânicos da Purpose Food',
    'feira',
    NOW() + INTERVAL '2 days',
    NOW() + INTERVAL '2 days 8 hours',
    'Praça Central - Centro da Cidade',
    'Praça Central, 123 - Centro',
    'scheduled',
    '00000000-0000-0000-0000-000000000001'::uuid
),
(
    'Entrega de Marmitas - Empresa TechCorp',
    'Entrega semanal de marmitas saudáveis para funcionários',
    'entrega',
    NOW() + INTERVAL '1 day',
    NOW() + INTERVAL '1 day 2 hours',
    'TechCorp - Setor de Tecnologia',
    'Rua da Tecnologia, 456 - Setor Industrial',
    'confirmed',
    '00000000-0000-0000-0000-000000000001'::uuid
),
(
    'Reunião de Planejamento - Evento Corporativo',
    'Reunião para planejar evento corporativo de final de ano',
    'reuniao',
    NOW() + INTERVAL '3 days',
    NOW() + INTERVAL '3 days 1.5 hours',
    'Escritório Purpose Food',
    'Rua da Alimentação Saudável, 789',
    'scheduled',
    '00000000-0000-0000-0000-000000000001'::uuid
),
(
    'Evento Corporativo - Festa de Final de Ano',
    'Catering para festa corporativa de final de ano',
    'evento',
    NOW() + INTERVAL '7 days',
    NOW() + INTERVAL '7 days 6 hours',
    'Centro de Convenções',
    'Avenida das Convenções, 1000 - Centro',
    'scheduled',
    '00000000-0000-0000-0000-000000000001'::uuid
);