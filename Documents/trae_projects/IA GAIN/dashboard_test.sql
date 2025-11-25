-- SCRIPT DE TESTE PARA POPULAR DADOS DO DASHBOARD
-- Execute este script no SQL Editor do Supabase

-- Limpar dados existentes (opcional)
TRUNCATE TABLE orders CASCADE;
TRUNCATE TABLE products CASCADE;
TRUNCATE TABLE customers CASCADE;
TRUNCATE TABLE financial_records CASCADE;

-- Inserir produtos de exemplo
INSERT INTO products (name, description, category, price, cost, stock, min_stock, unit, status, created_at, updated_at) VALUES
('Pão de Queijo Artesanal', 'Pão de queijo tradicional mineiro', 'Salgados', 25.00, 15.00, 150, 20, 'kg', 'active', NOW(), NOW()),
('Coxinha de Frango', 'Coxinha cremosa com frango desfiado', 'Salgados', 8.00, 4.50, 200, 30, 'un', 'active', NOW(), NOW()),
('Bolo de Cenoura', 'Bolo fofo com cobertura de chocolate', 'Doces', 45.00, 25.00, 80, 15, 'kg', 'active', NOW(), NOW()),
('Quiche de Legumes', 'Quiche leve com legumes frescos', 'Salgados', 35.00, 20.00, 60, 10, 'un', 'active', NOW(), NOW()),
('Brigadeiro Gourmet', 'Brigadeiro com chocolate belga', 'Doces', 3.50, 1.80, 300, 50, 'un', 'active', NOW(), NOW()),
('Empada de Palmito', 'Empada cremosa com palmito', 'Salgados', 6.00, 3.20, 120, 25, 'un', 'active', NOW(), NOW()),
('Torta de Limão', 'Torta azedinha com merengue', 'Doces', 55.00, 30.00, 40, 8, 'un', 'active', NOW(), NOW()),
('Croissant de Manteiga', 'Croissant folhado com manteiga', 'Salgados', 12.00, 6.50, 90, 15, 'un', 'active', NOW(), NOW());

-- Inserir clientes de exemplo
INSERT INTO customers (name, email, phone, document, type, address, city, state, zip_code, status, created_at, updated_at) VALUES
('Maria Silva', 'maria.silva@email.com', '(11) 98765-4321', '123.456.789-01', 'individual', 'Rua das Flores, 123', 'São Paulo', 'SP', '01234-567', 'active', NOW(), NOW()),
('João Santos', 'joao.santos@email.com', '(11) 99876-5432', '987.654.321-09', 'individual', 'Av. Paulista, 1000', 'São Paulo', 'SP', '01310-100', 'active', NOW(), NOW()),
('Empresa ABC Ltda', 'contato@empresaabc.com.br', '(11) 3234-5678', '12.345.678/0001-90', 'company', 'Rua do Comércio, 500', 'São Paulo', 'SP', '04567-890', 'active', NOW(), NOW()),
('Carla Oliveira', 'carla.oliveira@email.com', '(11) 91234-5678', '456.789.123-02', 'individual', 'Alameda Santos, 200', 'São Paulo', 'SP', '01419-100', 'active', NOW(), NOW()),
('Padaria Central', 'pedidos@padariacentral.com.br', '(11) 3098-7654', '98.765.432/0001-10', 'company', 'Rua da Padaria, 75', 'São Paulo', 'SP', '02345-678', 'active', NOW(), NOW()),
('Rafael Costa', 'rafael.costa@email.com', '(11) 98712-3456', '789.012.345-03', 'individual', 'Travessa do Sol, 33', 'São Paulo', 'SP', '03456-789', 'active', NOW(), NOW()),
('Confeitaria Doce Sabor', 'vendas@docesabor.com.br', '(11) 3344-5566', '11.223.344/0001-55', 'company', 'Av. das Nações, 1500', 'São Paulo', 'SP', '05678-901', 'active', NOW(), NOW()),
('Patricia Mendes', 'patricia.mendes@email.com', '(11) 99887-6655', '234.567.890-04', 'individual', 'Rua das Palmeiras, 88', 'São Paulo', 'SP', '06789-012', 'active', NOW(), NOW());

-- Inserir pedidos de exemplo
INSERT INTO orders (order_number, customer_id, total_amount, status, order_date, delivery_date, payment_method, payment_status, notes, created_at, updated_at) VALUES
('PED-2024-001', 1, 156.50, 'delivered', NOW() - INTERVAL '5 days', NOW() - INTERVAL '3 days', 'credit_card', 'paid', 'Pedido para festa de aniversário', NOW(), NOW()),
('PED-2024-002', 2, 89.00, 'delivered', NOW() - INTERVAL '4 days', NOW() - INTERVAL '2 days', 'pix', 'paid', 'Entrega rápida solicitada', NOW(), NOW()),
('PED-2024-003', 3, 234.75, 'in_preparation', NOW() - INTERVAL '3 days', NOW() + INTERVAL '1 day', 'bank_slip', 'pending', 'Pedido corporativo mensal', NOW(), NOW()),
('PED-2024-004', 4, 67.25, 'delivered', NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 day', 'pix', 'paid', 'Pedido de sábado', NOW(), NOW()),
('PED-2024-005', 5, 445.80, 'confirmed', NOW() - INTERVAL '1 day', NOW() + INTERVAL '2 days', 'credit_card', 'paid', 'Pedido da padaria para semana', NOW(), NOW()),
('PED-2024-006', 6, 123.40, 'pending', NOW(), NOW() + INTERVAL '3 days', 'pix', 'pending', 'Aguardando confirmação de pagamento', NOW(), NOW()),
('PED-2024-007', 7, 567.90, 'in_preparation', NOW() - INTERVAL '1 day', NOW() + INTERVAL '1 day', 'bank_slip', 'paid', 'Encomenda grande para evento', NOW(), NOW()),
('PED-2024-008', 8, 78.50, 'confirmed', NOW(), NOW() + INTERVAL '2 days', 'pix', 'paid', 'Pedido simples para final de semana', NOW(), NOW()),
('PED-2024-009', 1, 198.75, 'pending', NOW(), NOW() + INTERVAL '4 days', 'credit_card', 'pending', 'Segundo pedido do mês', NOW(), NOW()),
('PED-2024-010', 3, 334.60, 'confirmed', NOW(), NOW() + INTERVAL '5 days', 'bank_slip', 'paid', 'Pedido mensal adicional', NOW(), NOW());

-- Inserir itens dos pedidos
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price, created_at) VALUES
(1, 1, 2, 25.00, 50.00, NOW()), -- Pão de queijo
(1, 2, 5, 8.00, 40.00, NOW()), -- Coxinha
(1, 3, 1.5, 45.00, 67.50, NOW()), -- Bolo de cenoura
(2, 2, 8, 8.00, 64.00, NOW()), -- Coxinha
(2, 6, 4, 6.00, 24.00, NOW()), -- Empada
(3, 1, 5, 25.00, 125.00, NOW()), -- Pão de queijo
(3, 4, 2, 35.00, 70.00, NOW()), -- Quiche
(3, 8, 3, 12.00, 36.00, NOW()), -- Croissant
(4, 5, 10, 3.50, 35.00, NOW()), -- Brigadeiro
(4, 7, 0.5, 55.00, 27.50, NOW()), -- Torta de limão
(4, 2, 1, 8.00, 8.00, NOW()), -- Coxinha
(5, 1, 8, 25.00, 200.00, NOW()), -- Pão de queijo
(5, 2, 15, 8.00, 120.00, NOW()), -- Coxinha
(5, 6, 10, 6.00, 60.00, NOW()), -- Empada
(5, 8, 5, 12.00, 60.00, NOW()), -- Croissant
(5, 3, 1, 45.00, 45.00, NOW()), -- Bolo
(6, 2, 8, 8.00, 64.00, NOW()), -- Coxinha
(6, 5, 15, 3.50, 52.50, NOW()), -- Brigadeiro
(6, 6, 1, 6.00, 6.00, NOW()), -- Empada
(7, 3, 3, 45.00, 135.00, NOW()), -- Bolo
(7, 7, 2, 55.00, 110.00, NOW()), -- Torta
(7, 1, 5, 25.00, 125.00, NOW()), -- Pão de queijo
(7, 4, 3, 35.00, 105.00, NOW()), -- Quiche
(8, 2, 5, 8.00, 40.00, NOW()), -- Coxinha
(8, 5, 10, 3.50, 35.00, NOW()), -- Brigadeiro
(8, 8, 0.5, 12.00, 6.00, NOW()), -- Croissant
(9, 1, 3, 25.00, 75.00, NOW()), -- Pão de queijo
(9, 2, 8, 8.00, 64.00, NOW()), -- Coxinha
(9, 3, 1, 45.00, 45.00, NOW()), -- Bolo
(9, 7, 0.5, 55.00, 27.50, NOW()), -- Torta
(10, 1, 6, 25.00, 150.00, NOW()), -- Pão de queijo
(10, 4, 3, 35.00, 105.00, NOW()), -- Quiche
(10, 8, 4, 12.00, 48.00, NOW()), -- Croissant
(10, 6, 5, 6.00, 30.00, NOW()); -- Empada

-- Inserir registros financeiros
INSERT INTO financial_records (type, category, description, amount, date, payment_method, reference_type, reference_id, created_at, updated_at) VALUES
('revenue', 'sales', 'Venda de produtos - Pedido PED-2024-001', 156.50, NOW() - INTERVAL '5 days', 'credit_card', 'order', 1, NOW(), NOW()),
('revenue', 'sales', 'Venda de produtos - Pedido PED-2024-002', 89.00, NOW() - INTERVAL '4 days', 'pix', 'order', 2, NOW(), NOW()),
('revenue', 'sales', 'Venda de produtos - Pedido PED-2024-004', 67.25, NOW() - INTERVAL '2 days', 'pix', 'order', 4, NOW(), NOW()),
('revenue', 'sales', 'Venda de produtos - Pedido PED-2024-005', 445.80, NOW() - INTERVAL '1 day', 'credit_card', 'order', 5, NOW(), NOW()),
('revenue', 'sales', 'Venda de produtos - Pedido PED-2024-007', 567.90, NOW() - INTERVAL '1 day', 'bank_slip', 'order', 7, NOW(), NOW()),
('revenue', 'sales', 'Venda de produtos - Pedido PED-2024-008', 78.50, NOW(), 'pix', 'order', 8, NOW(), NOW()),
('revenue', 'sales', 'Venda de produtos - Pedido PED-2024-010', 334.60, NOW(), 'bank_slip', 'order', 10, NOW(), NOW()),

-- Custos de produção
('expense', 'ingredients', 'Compra de farinha e queijo', 450.00, NOW() - INTERVAL '7 days', 'bank_slip', 'other', NULL, NOW(), NOW()),
('expense', 'ingredients', 'Compra de frango e legumes', 320.00, NOW() - INTERVAL '6 days', 'bank_slip', 'other', NULL, NOW(), NOW()),
('expense', 'ingredients', 'Compra de chocolate e açúcar', 280.00, NOW() - INTERVAL '5 days', 'credit_card', 'other', NULL, NOW(), NOW()),
('expense', 'utilities', 'Conta de energia elétrica', 180.00, NOW() - INTERVAL '3 days', 'bank_slip', 'other', NULL, NOW(), NOW()),
('expense', 'utilities', 'Conta de água', 85.00, NOW() - INTERVAL '2 days', 'bank_slip', 'other', NULL, NOW(), NOW()),
('expense', 'salaries', 'Salário funcionários produção', 1200.00, NOW() - INTERVAL '1 day', 'bank_transfer', 'other', NULL, NOW(), NOW()),
('expense', 'rent', 'Aluguel do estabelecimento', 800.00, NOW(), 'bank_slip', 'other', NULL, NOW(), NOW());

-- Verificar dados inseridos
SELECT 
  'Resumo dos Dados Inseridos:' as info,
  (SELECT COUNT(*) FROM products) as total_products,
  (SELECT COUNT(*) FROM customers) as total_customers,
  (SELECT COUNT(*) FROM orders) as total_orders,
  (SELECT COUNT(*) FROM order_items) as total_order_items,
  (SELECT COUNT(*) FROM financial_records WHERE type = 'revenue') as total_revenues,
  (SELECT COUNT(*) FROM financial_records WHERE type = 'expense') as total_expenses;

-- Consultas úteis para testar o dashboard
SELECT 
  COUNT(*) as total_orders,
  SUM(total_amount) as total_revenue,
  AVG(total_amount) as avg_order_value
FROM orders 
WHERE status IN ('delivered', 'confirmed', 'in_preparation');

SELECT 
  status,
  COUNT(*) as count,
  SUM(total_amount) as total_amount
FROM orders 
GROUP BY status;

SELECT 
  category,
  COUNT(*) as count,
  SUM(amount) as total_amount
FROM financial_records 
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY category, type
ORDER BY type, total_amount DESC;