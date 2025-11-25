import { supabase } from '../lib/supabase';

interface NotificationData {
  customer_id: string;
  title: string;
  message: string;
  type: 'availability' | 'order_status' | 'promotion' | 'production';
  data?: Record<string, any>;
}

interface AvailabilityNotificationData {
  delivery_type: 'immediate' | 'production';
  preparation_time?: number;
  stock_current: number;
}

class NotificationService {
  async createNotification(notification: NotificationData): Promise<void> {
    try {
      const { error } = await supabase
        .from('customer_notifications')
        .insert([{
          ...notification,
          created_at: new Date().toISOString(),
          read: false
        }]);

      if (error) throw error;
    } catch (error) {
      console.error('Erro ao criar notificação:', error);
    }
  }

  async createAvailabilityNotification(
    customerId: string,
    productName: string,
    data: AvailabilityNotificationData
  ): Promise<void> {
    let title = 'Disponibilidade do Produto';
    let message = '';

    if (data.delivery_type === 'immediate') {
      message = `${productName} está disponível para entrega imediata!`;
    } else {
      message = `${productName} está em produção. Tempo estimado: ${data.preparation_time}h`;
    }

    await this.createNotification({
      customer_id: customerId,
      title,
      message,
      type: 'availability',
      data: {
        product_name: productName,
        delivery_type: data.delivery_type,
        preparation_time: data.preparation_time,
        stock_current: data.stock_current
      }
    });
  }

  async createOrderStatusNotification(
    customerId: string,
    orderId: string,
    status: string,
    estimatedDelivery?: string
  ): Promise<void> {
    const statusMessages = {
      'pending': 'Seu pedido foi recebido e está sendo processado',
      'confirmed': 'Seu pedido foi confirmado e está em preparação',
      'in_production': 'Seu pedido está em produção',
      'ready': 'Seu pedido está pronto para retirada',
      'delivered': 'Seu pedido foi entregue com sucesso!',
      'cancelled': 'Seu pedido foi cancelado'
    };

    const title = `Status do Pedido #${orderId.slice(-6)}`;
    const message = statusMessages[status as keyof typeof statusMessages] || 'Status atualizado';

    await this.createNotification({
      customer_id: customerId,
      title,
      message,
      type: 'order_status',
      data: {
        order_id: orderId,
        status,
        estimated_delivery: estimatedDelivery
      }
    });
  }

  async createProductionNotification(
    customerId: string,
    productName: string,
    preparationTime: number
  ): Promise<void> {
    await this.createNotification({
      customer_id: customerId,
      title: 'Tempo de Produção',
      message: `${productName} está em produção. Tempo estimado: ${preparationTime}h`,
      type: 'production',
      data: {
        product_name: productName,
        preparation_time: preparationTime
      }
    });
  }

  async getCustomerNotifications(customerId: string, limit: number = 50): Promise<any[]> {
    try {
      const { data, error } = await supabase
        .from('customer_notifications')
        .select('*')
        .eq('customer_id', customerId)
        .order('created_at', { ascending: false })
        .limit(limit);

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Erro ao buscar notificações:', error);
      return [];
    }
  }

  async markAsRead(notificationId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('customer_notifications')
        .update({ read: true })
        .eq('id', notificationId);

      if (error) throw error;
    } catch (error) {
      console.error('Erro ao marcar notificação como lida:', error);
    }
  }

  async markAllAsRead(customerId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('customer_notifications')
        .update({ read: true })
        .eq('customer_id', customerId)
        .eq('read', false);

      if (error) throw error;
    } catch (error) {
      console.error('Erro ao marcar todas as notificações como lidas:', error);
    }
  }

  async getUnreadCount(customerId: string): Promise<number> {
    try {
      const { count, error } = await supabase
        .from('customer_notifications')
        .select('*', { count: 'exact', head: true })
        .eq('customer_id', customerId)
        .eq('read', false);

      if (error) throw error;
      return count || 0;
    } catch (error) {
      console.error('Erro ao contar notificações não lidas:', error);
      return 0;
    }
  }

  // Configurar listener para notificações em tempo real
  onNotificationChange(customerId: string, callback: (notification: any) => void) {
    return supabase
      .channel(`notifications-${customerId}`)
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'customer_notifications',
        filter: `customer_id=eq.${customerId}`
      }, (payload) => {
        callback(payload.new);
      })
      .subscribe();
  }
}

export const notificationService = new NotificationService();