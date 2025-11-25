import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Customer {
  id: string
  name: string
  email: string
  phone: string
  address: string
  created_at: string
}

export interface CartItem {
  id: string
  productId: string
  name: string
  price: number
  quantity: number
  image?: string
  preparationTime?: number
}

export interface CustomerOrder {
  id: string
  customerId: string
  items: CartItem[]
  total: number
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered'
  paymentStatus: 'pending' | 'paid' | 'failed'
  deliveryType: 'delivery' | 'pickup'
  deliveryAddress?: string
  estimatedDeliveryTime?: string
  created_at: string
}

interface CustomerStore {
  customer: Customer | null
  cartItems: CartItem[]
  orders: CustomerOrder[]
  isAuthenticated: boolean
  
  // Actions
  setCustomer: (customer: Customer | null) => void
  signIn: (email: string, password: string) => Promise<boolean>
  signOut: () => void
  addToCart: (item: Omit<CartItem, 'id'>) => void
  removeFromCart: (productId: string) => void
  updateCartQuantity: (productId: string, quantity: number) => void
  clearCart: () => void
  placeOrder: (deliveryType: 'delivery' | 'pickup', deliveryAddress?: string) => Promise<boolean>
  updateOrderStatus: (orderId: string, status: CustomerOrder['status']) => void
  getCartTotal: () => number
  getCartItemCount: () => number
  fetchOrders: () => Promise<void>
  fetchCustomerData: () => Promise<void>
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
              created_at: customerData.created_at
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

      signOut: async () => {
        try {
          const supabase = getSupabaseClient();
          if (supabase) {
            await supabase.auth.signOut();
          }
        } catch (error) {
          console.error('Erro ao fazer logout:', error);
        }
        set({ customer: null, cartItems: [], orders: [], isAuthenticated: false });
      },

      addToCart: (item) => {
        const existingItem = get().cartItems.find(cartItem => cartItem.productId === item.productId)
        
        if (existingItem) {
          set({
            cartItems: get().cartItems.map(cartItem =>
              cartItem.productId === item.productId
                ? { ...cartItem, quantity: cartItem.quantity + item.quantity }
                : cartItem
            )
          })
        } else {
          set({
            cartItems: [...get().cartItems, { ...item, id: Date.now().toString() }]
          })
        }
      },

      removeFromCart: (productId) => {
        set({
          cartItems: get().cartItems.filter(item => item.productId !== productId)
        })
      },

      updateCartQuantity: (productId, quantity) => {
        if (quantity <= 0) {
          get().removeFromCart(productId)
          return
        }
        
        set({
          cartItems: get().cartItems.map(item =>
            item.productId === productId
              ? { ...item, quantity }
              : item
          )
        })
      },

      clearCart: () => {
        set({ cartItems: [] })
      },

      placeOrder: async (deliveryType, deliveryAddress) => {
        const { customer, cartItems } = get()
        
        if (!customer || cartItems.length === 0) {
          return false
        }

        try {
          const supabase = getSupabaseClient();
          if (!supabase) {
            throw new Error('Supabase client não disponível');
          }

          const total = get().getCartTotal();
          const orderId = Date.now().toString();
          
          // Create order in database
          const { error: orderError } = await supabase
            .from('orders')
            .insert([{
              id: orderId,
              customer_id: customer.id,
              total_amount: total,
              status: 'pending',
              delivery_type: deliveryType,
              delivery_address: deliveryAddress,
              estimated_delivery_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours from now
              created_at: new Date().toISOString()
            }]);

          if (orderError) {
            throw new Error('Erro ao criar pedido: ' + orderError.message);
          }

          // Create order items
          const orderItems = cartItems.map(item => ({
            order_id: orderId,
            product_id: item.productId,
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

          const newOrder: CustomerOrder = {
            id: orderId,
            customerId: customer.id,
            items: [...cartItems],
            total,
            status: 'pending',
            paymentStatus: 'pending',
            deliveryType,
            deliveryAddress,
            estimatedDeliveryTime: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
            created_at: new Date().toISOString()
          }

          set({
            orders: [...get().orders, newOrder],
            cartItems: []
          })

          return true
        } catch (error) {
          console.error('Erro ao criar pedido:', error);
          return false;
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

          set({
            orders: get().orders.map(order =>
              order.id === orderId ? { ...order, status } : order
            )
          })
        } catch (error) {
          console.error('Erro ao atualizar status do pedido:', error);
        }
      },

      getCartTotal: () => {
        return get().cartItems.reduce((total, item) => total + (item.price * item.quantity), 0)
      },

      getCartItemCount: () => {
        return get().cartItems.reduce((count, item) => count + item.quantity, 0)
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

          const orders: CustomerOrder[] = ordersData?.map((order: any) => ({
            id: order.id,
            customerId: order.customer_id,
            items: order.order_items?.map((item: any) => ({
              id: item.product_id,
              productId: item.product_id,
              name: 'Produto', // Would need to fetch product names separately
              price: parseFloat(item.unit_price) || 0,
              quantity: item.quantity,
              image: undefined,
              preparationTime: undefined
            })) || [],
            total: parseFloat(order.total_amount) || 0,
            status: order.status,
            paymentStatus: order.payment_status || 'pending',
            deliveryType: order.delivery_type,
            deliveryAddress: order.delivery_address,
            estimatedDeliveryTime: order.estimated_delivery_time,
            created_at: order.created_at
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
              created_at: customerData.created_at
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
      name: 'customer-store-stores',
      partialize: (state) => ({
        customer: state.customer,
        isAuthenticated: state.isAuthenticated,
        orders: state.orders
      })
    }
  )
)

// Initialize customer data on app start
useCustomerStore.getState().fetchCustomerData();