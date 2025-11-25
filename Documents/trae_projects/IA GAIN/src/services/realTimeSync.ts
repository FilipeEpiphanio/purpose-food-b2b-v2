/**
 * Serviço de sincronização em tempo real entre interface do cliente e gerencial
 */

interface Notification {
  id: string;
  customer_id?: string;
  type: 'order' | 'invoice' | 'system' | 'product';
  title: string;
  message: string;
  read: boolean;
  created_at: string;
  reference_id?: string;
  reference_type?: string;
}

interface ProductChange {
  productId: string;
  changes: string[];
  product?: any;
  timestamp: string;
}

export class RealTimeSyncService {
  private subscriptions: Map<string, Set<Function>> = new Map();
  private listeners: Map<string, Set<Function>> = new Map();
  private customerNotifications: Map<string, Notification[]> = new Map();
  private managementNotifications: Notification[] = [];
  private realtimeSubscription: any = null;

  constructor() {
    this.initializeSubscriptions();
    this.startRealTimeSync();
  }

  private initializeSubscriptions() {
    console.log('Serviço de sincronização inicializado com integração real');
  }

  private async startRealTimeSync() {
    try {
      // Subscribe to notifications table changes
      this.realtimeSubscription = (window as any).supabaseClient
        ?.channel('notifications-channel')
        .on('postgres_changes', 
          { event: '*', schema: 'public', table: 'notifications' },
          async (payload: any) => {
            await this.handleNotificationChange(payload);
          }
        )
        .subscribe();

      // Subscribe to products table changes
      (window as any).supabaseClient
        ?.channel('products-channel')
        .on('postgres_changes', 
          { event: '*', schema: 'public', table: 'products' },
          async (payload: any) => {
            await this.handleProductChange(payload);
          }
        )
        .subscribe();

      console.log('Canais de sincronização em tempo real conectados');
    } catch (error) {
      console.error('Erro ao conectar canais de sincronização:', error);
      // Fallback to periodic polling if realtime fails
      this.startPollingFallback();
    }
  }

  private async handleNotificationChange(payload: any) {
    const notification = payload.new as Notification;
    
    if (notification.customer_id) {
      // Customer notification
      if (!this.customerNotifications.has(notification.customer_id)) {
        this.customerNotifications.set(notification.customer_id, []);
      }
      
      const notifications = this.customerNotifications.get(notification.customer_id)!;
      notifications.push(notification);
      
      console.log(`Notificação em tempo real para cliente ${notification.customer_id}:`, notification.message);
    } else {
      // Management notification
      this.managementNotifications.push(notification);
      console.log('Notificação de gestão em tempo real:', notification.message);
    }
  }

  private async handleProductChange(payload: any) {
    const productId = payload.old?.id || payload.new?.id;
    if (!productId) return;

    const changeData: ProductChange = {
      productId,
      changes: this.detectChanges(payload.old, payload.new),
      product: payload.new,
      timestamp: new Date().toISOString()
    };

    await this.notifyProductChange(productId, changeData);
  }

  private detectChanges(oldData: any, newData: any): string[] {
    const changes: string[] = [];
    if (!oldData || !newData) return changes;

    Object.keys(newData).forEach(key => {
      if (oldData[key] !== newData[key]) {
        changes.push(key);
      }
    });

    return changes;
  }

  private startPollingFallback() {
    // Poll for changes every 30 seconds if realtime fails
    setInterval(async () => {
      await this.pollForChanges();
    }, 30000);
  }

  private async pollForChanges() {
    try {
      // Fetch recent notifications
      const { data: notifications, error } = await (window as any).supabaseClient
        ?.from('notifications')
        .select('*')
        .gt('created_at', new Date(Date.now() - 30000).toISOString()) // Last 30 seconds
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Erro ao buscar notificações:', error);
        return;
      }

      notifications?.forEach((notification: Notification) => {
        this.handleNotificationChange({ new: notification });
      });

      // Fetch recent product changes
      const { data: products, error: productsError } = await (window as any).supabaseClient
        ?.from('products')
        .select('*')
        .gt('updated_at', new Date(Date.now() - 30000).toISOString()) // Last 30 seconds
        .order('updated_at', { ascending: false });

      if (productsError) {
        console.error('Erro ao buscar mudanças de produtos:', productsError);
        return;
      }

      // For polling, we'll treat each product as a change
      products?.forEach((product: any) => {
        this.handleProductChange({ new: product, old: null });
      });

    } catch (error) {
      console.error('Erro na verificação periódica:', error);
    }
  }

  /**
   * Inscreve um callback para mudanças em produtos específicos
   */
  subscribeToProductChanges(productId: string, callback: Function) {
    if (!this.subscriptions.has(productId)) {
      this.subscriptions.set(productId, new Set());
    }
    this.subscriptions.get(productId)!.add(callback);
  }

  /**
   * Método genérico para escutar mudanças em produtos
   * Retorna uma função de unsubscribe
   */
  onProductChange(callback: Function): () => void {
    try {
      const listenerId = `general_${Date.now()}_${Math.random()}`;
      
      this.subscriptions.set(listenerId, new Set([callback]));
      
      console.log('Listener de mudanças de produto registrado:', listenerId);
      
      return () => {
        this.subscriptions.delete(listenerId);
        console.log('Listener de mudanças de produto removido:', listenerId);
      };
    } catch (error) {
      console.error('Erro ao registrar listener de mudanças:', error);
      return () => {};
    }
  }

  /**
   * Notifica sobre mudanças em produtos
   */
  async notifyProductChange(productId: string, changeData: ProductChange) {
    // Notificar listeners específicos do produto
    const callbacks = this.subscriptions.get(productId);
    if (callbacks) {
      callbacks.forEach(callback => {
        callback(changeData);
      });
    }

    // Notificar listeners genéricos (onProductChange)
    this.subscriptions.forEach((callbacks, key) => {
      if (key.startsWith('general_')) {
        callbacks.forEach(callback => {
          callback(changeData);
        });
      }
    });
  }

  /**
   * Obtém mudanças em produtos para sincronização
   */
  async getProductChanges(productId: string): Promise<any> {
    try {
      const { data: product, error } = await (window as any).supabaseClient
        ?.from('products')
        .select('*')
        .eq('id', productId)
        .single();

      if (error) {
        console.error('Erro ao buscar produto:', error);
        return {
          productId,
          changes: [],
          lastUpdate: new Date().toISOString(),
          error: error.message
        };
      }

      return {
        productId,
        changes: product ? ['data_fetched'] : ['not_found'],
        product,
        lastUpdate: product?.updated_at || new Date().toISOString(),
        error: null
      };
    } catch (error) {
      console.error('Erro ao obter mudanças de produto:', error);
      return {
        productId,
        changes: [],
        lastUpdate: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }

  /**
   * Obtém produto para visualização do cliente
   */
  async getCustomerProduct(productId: string): Promise<any> {
    try {
      const { data: product, error } = await (window as any).supabaseClient
        ?.from('products')
        .select('*')
        .eq('id', productId)
        .single();

      if (error) {
        console.error('Erro ao buscar produto do cliente:', error);
        return {
          id: productId,
          name: 'Produto não encontrado',
          price: 0,
          stock: 0,
          preparation_time: 0,
          is_active: false,
          image_url: '',
          ingredients: [],
          error: error.message
        };
      }

      return {
        id: product.id,
        name: product.name,
        price: parseFloat(product.price) || 0,
        stock: product.stock_current || 0,
        preparation_time: product.preparation_time || 0,
        is_active: product.is_active || false,
        image_url: product.image_url || '',
        ingredients: product.ingredients || [],
        error: null
      };
    } catch (error) {
      console.error('Erro ao obter produto do cliente:', error);
      return {
        id: productId,
        name: 'Erro ao carregar produto',
        price: 0,
        stock: 0,
        preparation_time: 0,
        is_active: false,
        image_url: '',
        ingredients: [],
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }

  /**
   * Notifica cliente sobre eventos importantes
   */
  async notifyCustomer(customerId: string, notification: any) {
    try {
      const { error } = await (window as any).supabaseClient
        ?.from('notifications')
        .insert([{
          customer_id: customerId,
          type: notification.type || 'system',
          title: notification.title,
          message: notification.message,
          reference_id: notification.referenceId,
          reference_type: notification.referenceType,
          read: false
        }]);

      if (error) {
        console.error('Erro ao criar notificação:', error);
        // Fallback to local storage
        if (!this.customerNotifications.has(customerId)) {
          this.customerNotifications.set(customerId, []);
        }
        
        const notifications = this.customerNotifications.get(customerId)!;
        notifications.push({
          id: `local_${Date.now()}`,
          customer_id: customerId,
          type: notification.type || 'system',
          title: notification.title,
          message: notification.message,
          reference_id: notification.referenceId,
          reference_type: notification.referenceType,
          read: false,
          created_at: new Date().toISOString()
        });
      }

      console.log(`Notificação enviada para cliente ${customerId}:`, notification.message);
    } catch (error) {
      console.error('Erro ao notificar cliente:', error);
    }
  }

  /**
   * Obtém notificações do cliente
   */
  async getCustomerNotifications(customerId: string): Promise<Notification[]> {
    try {
      const { data: notifications, error } = await (window as any).supabaseClient
        ?.from('notifications')
        .select('*')
        .eq('customer_id', customerId)
        .order('created_at', { ascending: false })
        .limit(50);

      if (error) {
        console.error('Erro ao buscar notificações do cliente:', error);
        return this.customerNotifications.get(customerId) || [];
      }

      return notifications || this.customerNotifications.get(customerId) || [];
    } catch (error) {
      console.error('Erro ao obter notificações do cliente:', error);
      return this.customerNotifications.get(customerId) || [];
    }
  }

  /**
   * Notifica gestão sobre eventos importantes
   */
  async notifyManagement(notification: any) {
    try {
      const { error } = await (window as any).supabaseClient
        ?.from('notifications')
        .insert([{
          type: notification.type || 'system',
          title: notification.title,
          message: notification.message,
          reference_id: notification.referenceId,
          reference_type: notification.referenceType,
          read: false
        }]);

      if (error) {
        console.error('Erro ao criar notificação de gestão:', error);
        // Fallback to local storage
        this.managementNotifications.push({
          id: `local_${Date.now()}`,
          type: notification.type || 'system',
          title: notification.title,
          message: notification.message,
          reference_id: notification.referenceId,
          reference_type: notification.referenceType,
          read: false,
          created_at: new Date().toISOString()
        });
      }

      console.log('Notificação de gestão:', notification.message);
    } catch (error) {
      console.error('Erro ao notificar gestão:', error);
    }
  }

  /**
   * Obtém notificações de gestão
   */
  async getManagementNotifications(): Promise<Notification[]> {
    try {
      const { data: notifications, error } = await (window as any).supabaseClient
        ?.from('notifications')
        .select('*')
        .is('customer_id', null)
        .order('created_at', { ascending: false })
        .limit(50);

      if (error) {
        console.error('Erro ao buscar notificações de gestão:', error);
        return this.managementNotifications;
      }

      return notifications || this.managementNotifications;
    } catch (error) {
      console.error('Erro ao obter notificações de gestão:', error);
      return this.managementNotifications;
    }
  }

  /**
   * Simula sincronização de produto
   */
  async simulateProductSync(productData: any): Promise<{ syncTime: number }> {
    const startTime = Date.now();
    
    try {
      // Try to update the product in the database
      const { error } = await (window as any).supabaseClient
        ?.from('products')
        .update({
          name: productData.name,
          price: productData.price,
          stock_current: productData.stock,
          preparation_time: productData.preparation_time,
          is_active: productData.is_active,
          image_url: productData.image_url,
          ingredients: productData.ingredients,
          updated_at: new Date().toISOString()
        })
        .eq('id', productData.id);

      if (error) {
        console.error('Erro ao sincronizar produto:', error);
      }
    } catch (error) {
      console.error('Erro na sincronização:', error);
    }
    
    const syncTime = Date.now() - startTime;
    
    console.log(`Produto ${productData.name} sincronizado em ${syncTime}ms`);
    
    return { syncTime };
  }

  /**
   * Limpa recursos
   */
  destroy() {
    this.subscriptions.clear();
    this.listeners.clear();
    this.customerNotifications.clear();
    this.managementNotifications = [];
    
    if (this.realtimeSubscription) {
      this.realtimeSubscription.unsubscribe();
    }
    
    console.log('Serviço de sincronização finalizado');
  }
}

export const realTimeSyncService = new RealTimeSyncService();