import { supabase } from '../lib/supabase';
import { Order } from '../stores/customerStore';

export interface AdminOrder {
  id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  customer_phone?: string;
  items: Array<{
    product_id: string;
    product_name: string;
    quantity: number;
    unit_price: number;
    total_price: number;
  }>;
  subtotal: number;
  delivery_fee: number;
  total: number;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered' | 'cancelled';
  payment_status: 'pending' | 'paid' | 'failed';
  delivery_option: 'pickup' | 'delivery';
  delivery_address?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Converte um pedido do cliente (B2C) para um pedido do administrador (B2B)
 */
export async function convertCustomerOrderToAdminOrder(
  customerOrder: Order,
  customerData: {
    id: string;
    name: string;
    email: string;
    phone?: string;
  }
): Promise<AdminOrder> {
  // Buscar informações dos produtos no banco de dados
  const productIds = customerOrder.items.map(item => item.id);
  
  const { data: products, error } = await supabase
    .from('products')
    .select('id, name, price')
    .in('id', productIds);

  if (error) {
    throw new Error('Erro ao buscar informações dos produtos');
  }

  // Criar mapeamento de produtos
  const productMap = new Map();
  products?.forEach(product => {
    productMap.set(product.id, product);
  });

  // Converter items
  const items = customerOrder.items.map(item => {
    const product = productMap.get(item.id);
    return {
      product_id: item.id,
      product_name: product?.name || item.name,
      quantity: item.quantity,
      unit_price: item.price,
      total_price: item.price * item.quantity
    };
  });

  const subtotal = items.reduce((sum, item) => sum + item.total_price, 0);
  const deliveryFee = customerOrder.deliveryOption === 'delivery' ? 10 : 0; // Taxa de entrega se for delivery

  return {
    id: customerOrder.id,
    customer_id: customerData.id,
    customer_name: customerData.name,
    customer_email: customerData.email,
    customer_phone: customerData.phone,
    items,
    subtotal,
    delivery_fee: deliveryFee,
    total: subtotal + deliveryFee,
    status: customerOrder.status as any,
    payment_status: 'pending',
    delivery_option: customerOrder.deliveryOption || 'pickup',
    delivery_address: customerOrder.deliveryAddress || undefined,
    notes: customerOrder.notes,
    created_at: customerOrder.createdAt,
    updated_at: new Date().toISOString()
  };
}

/**
 * Sincroniza um pedido do cliente com o banco de dados do administrador
 */
export async function syncCustomerOrderToAdmin(customerOrder: Order, customerData: any) {
  try {
    const adminOrder = await convertCustomerOrderToAdminOrder(customerOrder, customerData);
    
    // Inserir pedido no banco de dados do administrador
    const { data, error } = await supabase
      .from('orders')
      .insert([{
        id: adminOrder.id,
        customer_id: adminOrder.customer_id,
        customer_name: adminOrder.customer_name,
        customer_email: adminOrder.customer_email,
        customer_phone: adminOrder.customer_phone,
        items: adminOrder.items,
        subtotal: adminOrder.subtotal,
        delivery_fee: adminOrder.delivery_fee,
        total: adminOrder.total,
        status: adminOrder.status,
        payment_status: adminOrder.payment_status,
        delivery_option: adminOrder.delivery_option,
        delivery_address: adminOrder.delivery_address,
        notes: adminOrder.notes,
        created_at: adminOrder.created_at,
        updated_at: adminOrder.updated_at
      }]);

    if (error) {
      console.error('Erro ao sincronizar pedido:', error);
      throw error;
    }

    return data;
  } catch (error) {
    console.error('Erro na sincronização:', error);
    throw error;
  }
}

/**
 * Atualiza o status de um pedido no sistema administrativo
 */
export async function updateAdminOrderStatus(
  orderId: string, 
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered' | 'cancelled'
) {
  const { data, error } = await supabase
    .from('orders')
    .update({ 
      status,
      updated_at: new Date().toISOString()
    })
    .eq('id', orderId);

  if (error) {
    console.error('Erro ao atualizar status do pedido:', error);
    throw error;
  }

  return data;
}

/**
 * Busca todos os pedidos de clientes para o painel administrativo
 */
export async function getCustomerOrdersForAdmin() {
  const { data, error } = await supabase
    .from('orders')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Erro ao buscar pedidos de clientes:', error);
    throw error;
  }

  return data;
}

/**
 * Busca pedidos por status para o dashboard administrativo
 */
export async function getOrdersByStatus(status: string) {
  const { data, error } = await supabase
    .from('orders')
    .select('*')
    .eq('status', status)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Erro ao buscar pedidos por status:', error);
    throw error;
  }

  return data;
}

/**
 * Calcula estatísticas dos pedidos de clientes
 */
export async function getCustomerOrderStats() {
  const { data, error } = await supabase
    .from('orders')
    .select('total, status, payment_status, created_at');

  if (error) {
    console.error('Erro ao buscar estatísticas de pedidos:', error);
    throw error;
  }

  const stats = {
    totalOrders: data?.length || 0,
    totalRevenue: data?.reduce((sum, order) => sum + (order.total || 0), 0) || 0,
    pendingOrders: data?.filter(order => order.status === 'pending').length || 0,
    confirmedOrders: data?.filter(order => order.status === 'confirmed').length || 0,
    deliveredOrders: data?.filter(order => order.status === 'delivered').length || 0,
    paidOrders: data?.filter(order => order.payment_status === 'paid').length || 0,
    monthlyRevenue: 0,
    revenueVariation: 0
  };

  // Calcular receita do mês atual
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  
  const monthlyOrders = data?.filter(order => {
    const orderDate = new Date(order.created_at);
    return orderDate.getMonth() === currentMonth && orderDate.getFullYear() === currentYear;
  }) || [];

  stats.monthlyRevenue = monthlyOrders.reduce((sum, order) => sum + (order.total || 0), 0);

  // Calcular variação em relação ao mês anterior
  const previousMonth = currentMonth === 0 ? 11 : currentMonth - 1;
  const previousYear = currentMonth === 0 ? currentYear - 1 : currentYear;
  
  const previousMonthOrders = data?.filter(order => {
    const orderDate = new Date(order.created_at);
    return orderDate.getMonth() === previousMonth && orderDate.getFullYear() === previousYear;
  }) || [];

  const previousMonthRevenue = previousMonthOrders.reduce((sum, order) => sum + (order.total || 0), 0);
  
  if (previousMonthRevenue > 0) {
    stats.revenueVariation = ((stats.monthlyRevenue - previousMonthRevenue) / previousMonthRevenue) * 100;
  }

  return stats;
}