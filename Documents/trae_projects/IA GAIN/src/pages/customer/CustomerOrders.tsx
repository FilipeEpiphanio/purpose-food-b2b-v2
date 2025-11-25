import React, { useState, useEffect } from 'react';
import { Package, Clock, CheckCircle, XCircle, Truck, Eye, Calendar, DollarSign } from 'lucide-react';
import { useCustomerStore } from '../../store/customerStore';
import { supabase } from '../../lib/supabase';

interface Order {
  id: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  delivery_address: string;
  delivery_instructions?: string;
  items: any[];
  subtotal: number;
  delivery_fee: number;
  total: number;
  status: 'pending' | 'confirmed' | 'preparing' | 'delivering' | 'delivered' | 'cancelled';
  payment_status: 'pending' | 'paid' | 'failed';
  created_at: string;
  updated_at: string;
}

const statusConfig = {
  pending: {
    label: 'Pendente',
    icon: Clock,
    color: 'text-yellow-600 bg-yellow-100',
    description: 'Aguardando confirmação'
  },
  confirmed: {
    label: 'Confirmado',
    icon: CheckCircle,
    color: 'text-blue-600 bg-blue-100',
    description: 'Pedido confirmado'
  },
  preparing: {
    label: 'Em Preparação',
    icon: Package,
    color: 'text-purple-600 bg-purple-100',
    description: 'Preparando seu pedido'
  },
  delivering: {
    label: 'Em Entrega',
    icon: Truck,
    color: 'text-indigo-600 bg-indigo-100',
    description: 'Saiu para entrega'
  },
  delivered: {
    label: 'Entregue',
    icon: CheckCircle,
    color: 'text-green-600 bg-green-100',
    description: 'Pedido entregue'
  },
  cancelled: {
    label: 'Cancelado',
    icon: XCircle,
    color: 'text-red-600 bg-red-100',
    description: 'Pedido cancelado'
  }
};

const paymentStatusConfig = {
  pending: {
    label: 'Pendente',
    color: 'text-yellow-600 bg-yellow-100'
  },
  paid: {
    label: 'Pago',
    color: 'text-green-600 bg-green-100'
  },
  failed: {
    label: 'Falhou',
    color: 'text-red-600 bg-red-100'
  }
};

const CustomerOrders: React.FC = () => {
  const { customer } = useCustomerStore();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      let query = supabase
        .from('orders')
        .select('*')
        .order('created_at', { ascending: false });

      // Se o cliente estiver logado, filtrar por email
      if (customer?.email) {
        query = query.eq('customer_email', customer.email);
      }

      const { data, error } = await query;

      if (error) throw error;
      setOrders(data || []);
    } catch (error) {
      console.error('Erro ao carregar pedidos:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Meus Pedidos</h1>
          <p className="text-gray-600">
            Acompanhe o status dos seus pedidos e histórico de compras
          </p>
        </div>

        {orders.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Nenhum pedido encontrado</h3>
            <p className="text-gray-600 mb-6">
              {customer 
                ? 'Você ainda não fez nenhum pedido.' 
                : 'Faça login para ver seus pedidos.'
              }
            </p>
            <button
              onClick={() => window.location.href = '/customer/products'}
              className="inline-flex items-center px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
            >
              <Package className="w-5 h-5 mr-2" />
              Fazer Primeiro Pedido
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => {
              const StatusIcon = statusConfig[order.status].icon;
              const PaymentStatus = paymentStatusConfig[order.payment_status];
              
              return (
                <div key={order.id} className="bg-white rounded-lg shadow-sm border">
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          Pedido #{order.id.slice(-8).toUpperCase()}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusConfig[order.status].color}`}>
                          <StatusIcon className="w-4 h-4 mr-1" />
                          {statusConfig[order.status].label}
                        </span>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${PaymentStatus.color}`}>
                          {PaymentStatus.label}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Status</p>
                        <p className="text-sm font-medium text-gray-900">
                          {statusConfig[order.status].description}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Endereço</p>
                        <p className="text-sm font-medium text-gray-900 line-clamp-1">
                          {order.delivery_address}
                        </p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Total</p>
                        <p className="text-lg font-bold text-orange-600">
                          {formatCurrency(order.total)}
                        </p>
                      </div>
                    </div>

                    <div className="border-t pt-4">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-gray-600">
                          {order.items.length} item{order.items.length !== 1 ? 's' : ''}
                        </p>
                        
                        <button
                          onClick={() => setSelectedOrder(selectedOrder?.id === order.id ? null : order)}
                          className="inline-flex items-center text-orange-600 hover:text-orange-700 text-sm font-medium"
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          {selectedOrder?.id === order.id ? 'Ocultar' : 'Ver'} Detalhes
                        </button>
                      </div>

                      {selectedOrder?.id === order.id && (
                        <div className="mt-4 pt-4 border-t">
                          <h4 className="text-sm font-semibold text-gray-900 mb-3">Itens do Pedido</h4>
                          <div className="space-y-2">
                            {order.items.map((item: any, index: number) => (
                              <div key={index} className="flex items-center justify-between text-sm">
                                <span className="text-gray-700">
                                  {item.quantity}x {item.name}
                                </span>
                                <span className="font-medium text-gray-900">
                                  {formatCurrency(item.price * item.quantity)}
                                </span>
                              </div>
                            ))}
                          </div>
                          
                          <div className="mt-3 pt-3 border-t">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">Subtotal</span>
                              <span className="text-gray-900">
                                {formatCurrency(order.subtotal)}
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-gray-600">Taxa de Entrega</span>
                              <span className="text-gray-900">
                                {formatCurrency(order.delivery_fee)}
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-sm font-semibold mt-2">
                              <span className="text-gray-900">Total</span>
                              <span className="text-orange-600">
                                {formatCurrency(order.total)}
                              </span>
                            </div>
                          </div>

                          {order.delivery_instructions && (
                            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                              <p className="text-sm text-gray-600 mb-1">Instruções de entrega:</p>
                              <p className="text-sm text-gray-900">{order.delivery_instructions}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerOrders;