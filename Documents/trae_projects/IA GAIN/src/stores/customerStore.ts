import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
}

interface Customer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  cpf?: string;
}

export interface Order {
  id: string;
  items: CartItem[];
  total: number;
  status: 'pending' | 'confirmed' | 'in_production' | 'ready' | 'delivered' | 'cancelled';
  deliveryOption: 'delivery' | 'pickup';
  deliveryAddress?: string;
  deliveryTime?: string; // Horário agendado para entrega
  estimatedTime?: string;
  notes?: string;
  createdAt: string;
}

interface CustomerStore {
  customer: Customer | null;
  cartItems: CartItem[];
  orders: Order[];
  isAuthenticated: boolean;
  
  // Actions
  setCustomer: (customer: Customer | null) => void;
  signIn: (email: string, password: string) => Promise<boolean>;
  signUp: (customerData: Partial<Customer> & { password: string }) => Promise<boolean>;
  signOut: () => void;
  addToCart: (item: CartItem) => void;
  removeFromCart: (itemId: string) => void;
  updateCartItemQuantity: (itemId: string, quantity: number) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
  getCartTotal: () => number;
  getCartItemCount: () => number;
  createOrder: (orderData: Partial<Order>) => Promise<string>;
  updateOrderStatus: (orderId: string, status: Order['status']) => void;
  fetchOrders: () => Promise<void>;
  fetchCustomerData: () => Promise<void>;
}

// Helper function to get Supabase client
const getSupabaseClient = () => {
  return (window as any).supabaseClient;
};

export const useCustomerStore = create<CustomerStore>()(
  persist(
    (set, get) => ({
      customer: null,
      cartItems: [],
      orders: [],
      isAuthenticated: false,

      setCustomer: (customer) => set({ customer, isAuthenticated: !!customer }),

      signIn: async (email, password) => {
        try {
          const supabase = getSupabaseClient();
          if (!supabase) {
            console.error('Supabase client não disponível');
            return false;
          }

          const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password,
          });

          if (error) {
            console.error('Erro ao fazer login:', error);
            return false;
          }

          if (data.user) {
            // Fetch customer data
            const { data: customerData, error: customerError } = await supabase
              .from('customers')
              .select('*')
              .eq('id', data.user.id)
              .single();

            if (customerError) {
              console.error('Erro ao buscar dados do cliente:', customerError);
              return false;
            }

            const customer: Customer = {
              id: customerData.id,
              name: customerData.name,
              email: customerData.email,
              phone: customerData.phone,
              address: customerData.address,
              cpf: customerData.cpf_cnpj
            };

            set({ customer, isAuthenticated: true });
            
            // Fetch customer orders
            await get().fetchOrders();
            
            return true;
          }
          
          return false;
        } catch (error) {
          console.error('Erro ao fazer login:', error);
          return false;
        }
      },

      signUp: async (customerData) => {
        try {
          const supabase = getSupabaseClient();
          if (!supabase) {
            console.error('Supabase client não disponível');
            return false;
          }

          const { data, error } = await supabase.auth.signUp({
            email: customerData.email!,
            password: customerData.password!,
          });

          if (error) {
            console.error('Erro ao criar conta:', error);
            return false;
          }

          if (data.user) {
            // Create customer record
            const { error: customerError } = await supabase
              .from('customers')
              .insert([{
                id: data.user.id,
                name: customerData.name,
                email: customerData.email,
                phone: customerData.phone,
                address: customerData.address,
                cpf_cnpj: customerData.cpf
              }]);

            if (customerError) {
              console.error('Erro ao criar registro de cliente:', customerError);
              return false;
            }

            const customer: Customer = {
              id: data.user.id,
              name: customerData.name || '',
              email: customerData.email || '',
              phone: customerData.phone,
              address: customerData.address,
              cpf: customerData.cpf
            };

            set({ customer, isAuthenticated: true });
            return true;
          }
          
          return false;
        } catch (error) {
          console.error('Erro ao cadastrar:', error);
          return false;
        }
      },

      signOut: async () => {
        try {
          const supabase = getSupabaseClient();
          if (supabase) {
            await supabase.auth.signOut();
          }
        } catch (error) {
          console.error('Erro ao fazer logout:', error);
        }
        set({ customer: null, isAuthenticated: false, cartItems: [] });
      },

      addToCart: (item) => {
        const { cartItems } = get();
        const existingItem = cartItems.find(cartItem => cartItem.id === item.id);
        
        if (existingItem) {
          set({
            cartItems: cartItems.map(cartItem =>
              cartItem.id === item.id
                ? { ...cartItem, quantity: cartItem.quantity + item.quantity }
                : cartItem
            )
          });
        } else {
          set({ cartItems: [...cartItems, item] });
        }
      },

      removeFromCart: (itemId) => {
        const { cartItems } = get();
        set({ cartItems: cartItems.filter(item => item.id !== itemId) });
      },

      updateCartItemQuantity: (itemId, quantity) => {
        const { cartItems } = get();
        if (quantity <= 0) {
          get().removeFromCart(itemId);
        } else {
          set({
            cartItems: cartItems.map(item =>
              item.id === itemId ? { ...item, quantity } : item
            )
          });
        }
      },

      updateQuantity: (itemId, quantity) => {
        get().updateCartItemQuantity(itemId, quantity);
      },

      clearCart: () => set({ cartItems: [] }),

      getCartTotal: () => {
        const { cartItems } = get();
        return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
      },

      getCartItemCount: () => {
        const { cartItems } = get();
        return cartItems.reduce((count, item) => count + item.quantity, 0);
      },

      createOrder: async (orderData) => {
        const { cartItems, customer, getCartTotal } = get();
        
        if (!customer || cartItems.length === 0) {
          throw new Error('Cliente não autenticado ou carrinho vazio');
        }

        try {
          const supabase = getSupabaseClient();
          if (!supabase) {
            throw new Error('Supabase client não disponível');
          }

          const orderId = 'PED-' + Date.now().toString().slice(-6);
          const total = getCartTotal();
          
          // Create order in database
          const { error: orderError } = await supabase
            .from('orders')
            .insert([{
              id: orderId,
              customer_id: customer.id,
              total_amount: total,
              status: 'pending',
              delivery_option: orderData.deliveryOption || 'pickup',
              delivery_address: orderData.deliveryAddress,
              delivery_time: orderData.deliveryTime,
              estimated_time: orderData.estimatedTime || '30-45 minutos',
              notes: orderData.notes,
              order_date: new Date().toISOString().split('T')[0]
            }]);

          if (orderError) {
            throw new Error('Erro ao criar pedido: ' + orderError.message);
          }

          // Create order items
          const orderItems = cartItems.map(item => ({
            order_id: orderId,
            product_id: item.id,
            quantity: item.quantity,
            unit_price: item.price,
            total_price: item.price * item.quantity
          }));

          const { error: itemsError } = await supabase
            .from('order_items')
            .insert(orderItems);

          if (itemsError) {
            throw new Error('Erro ao criar itens do pedido: ' + itemsError.message);
          }

          // Create notification for order
          await supabase
            .from('notifications')
            .insert([{
              customer_id: customer.id,
              type: 'order',
              title: 'Novo Pedido',
              message: `Seu pedido #${orderId} foi criado com sucesso!`,
              reference_id: orderId,
              reference_type: 'order',
              read: false
            }]);

          const newOrder: Order = {
            id: orderId,
            items: [...cartItems],
            total: total,
            status: 'pending',
            deliveryOption: orderData.deliveryOption || 'pickup',
            deliveryAddress: orderData.deliveryAddress,
            deliveryTime: orderData.deliveryTime,
            estimatedTime: orderData.estimatedTime || '30-45 minutos',
            notes: orderData.notes,
            createdAt: new Date().toISOString()
          };

          set({
            orders: [newOrder, ...get().orders],
            cartItems: [] // Limpar carrinho após criar pedido
          });

          return orderId;
        } catch (error) {
          console.error('Erro ao criar pedido:', error);
          throw error;
        }
      },

      updateOrderStatus: async (orderId, status) => {
        try {
          const supabase = getSupabaseClient();
          if (!supabase) {
            console.error('Supabase client não disponível');
            return;
          }

          const { error } = await supabase
            .from('orders')
            .update({ status })
            .eq('id', orderId);

          if (error) {
            console.error('Erro ao atualizar status do pedido:', error);
            return;
          }

          const { orders } = get();
          set({
            orders: orders.map(order =>
              order.id === orderId ? { ...order, status } : order
            )
          });
        } catch (error) {
          console.error('Erro ao atualizar status do pedido:', error);
        }
      },

      fetchOrders: async () => {
        try {
          const { customer } = get();
          if (!customer) return;

          const supabase = getSupabaseClient();
          if (!supabase) {
            console.error('Supabase client não disponível');
            return;
          }

          const { data: ordersData, error } = await supabase
            .from('orders')
            .select(`
              *,
              order_items(
                product_id,
                quantity,
                unit_price,
                total_price
              )
            `)
            .eq('customer_id', customer.id)
            .order('created_at', { ascending: false });

          if (error) {
            console.error('Erro ao buscar pedidos:', error);
            return;
          }

          const orders: Order[] = ordersData?.map((order: any) => ({
            id: order.id,
            items: order.order_items?.map((item: any) => ({
              id: item.product_id,
              name: 'Produto', // Would need to fetch product names separately
              price: parseFloat(item.unit_price) || 0,
              quantity: item.quantity,
              image: undefined
            })) || [],
            total: parseFloat(order.total_amount) || 0,
            status: order.status,
            deliveryOption: order.delivery_option,
            deliveryAddress: order.delivery_address,
            deliveryTime: order.delivery_time,
            estimatedTime: order.estimated_time,
            notes: order.notes,
            createdAt: order.created_at
          })) || [];

          set({ orders });
        } catch (error) {
          console.error('Erro ao buscar pedidos:', error);
        }
      },

      fetchCustomerData: async () => {
        try {
          const supabase = getSupabaseClient();
          if (!supabase) {
            console.error('Supabase client não disponível');
            return;
          }

          const { data: { user } } = await supabase.auth.getUser();
          
          if (user) {
            const { data: customerData, error } = await supabase
              .from('customers')
              .select('*')
              .eq('id', user.id)
              .single();

            if (error) {
              console.error('Erro ao buscar dados do cliente:', error);
              return;
            }

            const customer: Customer = {
              id: customerData.id,
              name: customerData.name,
              email: customerData.email,
              phone: customerData.phone,
              address: customerData.address,
              cpf: customerData.cpf_cnpj
            };

            set({ customer, isAuthenticated: true });
            await get().fetchOrders();
          }
        } catch (error) {
          console.error('Erro ao buscar dados do cliente:', error);
        }
      }
    }),
    {
      name: 'customer-store',
      partialize: (state) => ({
        customer: state.customer,
        isAuthenticated: state.isAuthenticated,
        orders: state.orders
        // Não persistir o carrinho para não manter itens antigos
      })
    }
  )
);

// Initialize customer data on app start
useCustomerStore.getState().fetchCustomerData();