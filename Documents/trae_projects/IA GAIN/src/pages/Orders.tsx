import React, { useState, useEffect } from 'react';
import DataTable from '@/components/ui/DataTable';
import OrderFormModal from '@/components/ui/OrderFormModal';
import { Plus, ShoppingCart, Clock, CheckCircle, Truck, DollarSign, User, Calendar, Filter, Eye, Edit, Trash2, Search } from 'lucide-react';
import { supabase } from '@/lib/supabase';

interface Order {
  id: string;
  customer_id: string;
  customer_name?: string;
  customer_phone?: string;
  order_number: string;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered' | 'cancelled';
  order_type: 'delivery' | 'pickup' | 'dine-in';
  total_amount: number;
  payment_method: 'cash' | 'card' | 'pix';
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded';
  delivery_address?: string;
  delivery_fee: number;
  notes?: string;
  scheduled_date?: string;
  needs_invoice?: boolean;
  invoice_issued?: boolean;
  created_at: string;
  updated_at: string;
  items?: Array<{
    id: string;
    product_id: string;
    product_name?: string;
    quantity: number;
    unit_price: number;
    total_price: number;
    notes?: string;
  }>;
}

const Orders: React.FC = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState<Order | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'kanban'>('kanban');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  // Buscar pedidos do Supabase
  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      
      // Buscar pedidos com informações dos clientes
      const { data: ordersData, error: ordersError } = await supabase
        .from('orders')
        .select(`
          *,
          customers (
            id,
            name,
            email,
            phone
          )
        `)
        .order('created_at', { ascending: false });

      if (ordersError) {
        console.error('Erro ao buscar pedidos:', ordersError);
        return;
      }

      // Buscar itens dos pedidos
      const { data: itemsData, error: itemsError } = await supabase
        .from('order_items')
        .select(`
          *,
          products (
            id,
            name,
            price
          )
        `);

      if (itemsError) {
        console.error('Erro ao buscar itens dos pedidos:', itemsError);
        return;
      }

      // Combinar dados
      const ordersWithItems = ordersData?.map(order => ({
        ...order,
        customer_name: order.customers?.name,
        customer_phone: order.customers?.phone,
        items: itemsData?.filter(item => item.order_id === order.id) || []
      })) || [];

      setOrders(ordersWithItems);
    } catch (error) {
      console.error('Erro ao buscar pedidos:', error);
    } finally {
      setLoading(false);
    }
  };

  const formFields = [
  {
    name: 'customer_name',
    label: 'Cliente',
    type: 'text',
    required: true,
    placeholder: 'Nome do cliente'
  },
  {
    name: 'customer_phone',
    label: 'Telefone',
    type: 'text',
    required: true,
    placeholder: '(00) 00000-0000'
  },
  {
    name: 'delivery_address',
    label: 'Endereço de Entrega',
    type: 'text',
    required: true,
    placeholder: 'Rua, número, bairro'
  },
  {
    name: 'status',
    label: 'Status do Pedido',
    type: 'select',
    required: true,
    options: [
      { value: 'pending', label: 'Pendente' },
      { value: 'confirmed', label: 'Confirmado' },
      { value: 'preparing', label: 'Preparando' },
      { value: 'ready', label: 'Pronto' },
      { value: 'delivered', label: 'Entregue' },
      { value: 'cancelled', label: 'Cancelado' }
    ]
  },
  {
    name: 'payment_method',
    label: 'Forma de Pagamento',
    type: 'select',
    required: true,
    options: [
      { value: 'cash', label: 'Dinheiro' },
      { value: 'card', label: 'Cartão' },
      { value: 'pix', label: 'PIX' }
    ]
  },
  {
    name: 'payment_status',
    label: 'Status do Pagamento',
    type: 'select',
    required: true,
    options: [
      { value: 'pending', label: 'Pendente' },
      { value: 'paid', label: 'Pago' },
      { value: 'failed', label: 'Falhou' }
    ]
  },
  {
    name: 'notes',
    label: 'Observações',
    type: 'textarea',
    required: false,
    placeholder: 'Observações do pedido'
  }
];

  const handleSubmit = async (data: any, action: 'save-exit' | 'save-new') => {
    try {
      if (editingOrder) {
        // Atualizar pedido existente
        const { error } = await supabase
          .from('orders')
          .update({
            status: data.status,
            payment_method: data.payment_method,
            payment_status: data.payment_status,
            delivery_address: data.delivery_address,
            notes: data.notes,
            needs_invoice: data.needs_invoice || false,
            updated_at: new Date().toISOString()
          })
          .eq('id', editingOrder.id);

        if (error) {
          console.error('Erro ao atualizar pedido:', error);
          alert('Erro ao atualizar pedido: ' + error.message);
          return;
        }
      } else {
        // Criar novo pedido usando a API (que já cria o cliente automaticamente)
        try {
          const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              customer_name: data.customer_name,
              customer_phone: data.customer_phone,
              delivery_address: data.delivery_address,
              status: data.status || 'pending',
              payment_method: data.payment_method,
              payment_status: data.payment_status || 'pending',
              notes: data.notes,
              needs_invoice: data.needs_invoice || false,
              order_type: 'delivery'
            })
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao criar pedido');
          }

          const result = await response.json();
          console.log('Pedido criado com sucesso:', result);
        } catch (error) {
          console.error('Erro ao criar pedido:', error);
          alert('Erro ao criar pedido: ' + error.message);
          return;
        }
      }

      // Recarregar lista de pedidos
      await fetchOrders();
      
      if (action === 'save-exit') {
        setIsFormOpen(false);
        setEditingOrder(null);
      } else {
        // Resetar formulário para novo pedido
        setEditingOrder(null);
      }
    } catch (error) {
      console.error('Erro ao salvar pedido:', error);
      alert('Erro ao salvar pedido: ' + error);
    }
  };

  const handleEdit = (order: Order) => {
    setEditingOrder(order);
    setIsFormOpen(true);
  };

  const handleDelete = async (order: Order) => {
    if (confirm(`Deseja realmente excluir o pedido ${order.order_number}?`)) {
      try {
        const { error } = await supabase
          .from('orders')
          .delete()
          .eq('id', order.id);

        if (error) {
          console.error('Erro ao excluir pedido:', error);
          alert('Erro ao excluir pedido: ' + error.message);
        } else {
          await fetchOrders();
        }
      } catch (error) {
        console.error('Erro ao excluir pedido:', error);
        alert('Erro ao excluir pedido: ' + error);
      }
    }
  };

  const handleStatusChange = async (orderId: string, newStatus: Order['status']) => {
    try {
      const { error } = await supabase
        .from('orders')
        .update({ 
          status: newStatus,
          updated_at: new Date().toISOString()
        })
        .eq('id', orderId);

      if (error) {
        console.error('Erro ao atualizar status:', error);
        alert('Erro ao atualizar status: ' + error.message);
      } else {
        await fetchOrders();
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      alert('Erro ao atualizar status: ' + error);
    }
  };

  const filteredOrders = orders.filter(order => {
    const matchesStatus = filterStatus === 'all' || order.status === filterStatus;
    const matchesSearch = searchTerm === '' || 
      order.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.customer_phone?.includes(searchTerm) ||
      order.order_number.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const getStatusColor = (status: Order['status']) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'preparing': return 'bg-blue-100 text-blue-800';
      case 'ready': return 'bg-green-100 text-green-800';
      case 'delivered': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: Order['status']) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'preparing': return <Clock className="w-4 h-4" />;
      case 'ready': return <CheckCircle className="w-4 h-4" />;
      case 'delivered': return <Truck className="w-4 h-4" />;
      case 'cancelled': return <Trash2 className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getStatusLabel = (status: Order['status']) => {
    switch (status) {
      case 'pending': return 'Pendente';
      case 'confirmed': return 'Confirmado';
      case 'preparing': return 'Preparando';
      case 'ready': return 'Pronto';
      case 'delivered': return 'Entregue';
      case 'cancelled': return 'Cancelado';
      default: return status;
    }
  };

  const columns = [
    {
      key: 'order_number',
      header: 'Pedido',
      sortable: true
    },
    {
      key: 'customer_name',
      header: 'Cliente',
      sortable: true,
      render: (value: string) => value || 'Cliente não identificado'
    },
    {
      key: 'total_amount',
      header: 'Total',
      sortable: true,
      render: (value: number) => `R$ ${value?.toFixed(2) || '0.00'}`
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getStatusColor(value as Order['status'])}`}>
          {getStatusIcon(value as Order['status'])}
          <span>{getStatusLabel(value as Order['status'])}</span>
        </span>
      )
    },
    {
      key: 'payment_status',
      header: 'Pagamento',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'paid' ? 'bg-green-100 text-green-800' :
          value === 'pending' ? 'bg-yellow-100 text-yellow-800' :
          value === 'failed' ? 'bg-red-100 text-red-800' :
          'bg-orange-100 text-orange-800'
        }`}>
          {value === 'paid' ? 'Pago' : 
           value === 'pending' ? 'Pendente' :
           value === 'failed' ? 'Falhou' :
           'Reembolsado'}
        </span>
      )
    },
    {
      key: 'created_at',
      header: 'Data',
      sortable: true,
      render: (value: string) => new Date(value).toLocaleDateString('pt-BR')
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (_: any, order: Order) => (
        <div className="flex space-x-2">
          <button
            onClick={() => {
              const confirmAccess = confirm(`Deseja acessar o SAT SEF/SC para emitir nota fiscal para o pedido ${order.order_number}?`);
              if (confirmAccess) {
                window.open('https://sat.sef.sc.gov.br/tax.NET/Login.aspx', '_blank');
              }
            }}
            className="bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700 flex items-center space-x-1"
            title="Acessar SAT SEF/SC para emitir nota fiscal"
          >
            <span>📝</span>
            <span>NF</span>
          </button>
        </div>
      )
    }
  ];

  // Kanban Board View with Drag and Drop
  const KanbanBoard = () => {
    const statuses: Order['status'][] = ['pending', 'confirmed', 'preparing', 'ready', 'delivered'];
    const [draggedOrder, setDraggedOrder] = useState<Order | null>(null);

    const handleDragStart = (e: React.DragEvent, order: Order) => {
      setDraggedOrder(order);
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', order.id);
    };

    const handleDragOver = (e: React.DragEvent) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    };

    const handleDrop = async (e: React.DragEvent, newStatus: Order['status']) => {
      e.preventDefault();
      if (draggedOrder && draggedOrder.status !== newStatus) {
        await handleStatusChange(draggedOrder.id, newStatus);
        setDraggedOrder(null);
      }
    };

    const handleDragEnd = () => {
      setDraggedOrder(null);
    };
    
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {statuses.map((status) => {
          const statusOrders = filteredOrders.filter(o => o.status === status);
          
          return (
            <div 
              key={status} 
              className="bg-gray-50 rounded-lg p-4 min-h-96"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, status)}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">{getStatusLabel(status)}</h3>
                <span className="bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-sm font-medium">
                  {statusOrders.length}
                </span>
              </div>
              
              <div className="space-y-3">
                {statusOrders.map((order) => (
                  <div 
                    key={order.id} 
                    className={`bg-white rounded-lg p-4 shadow-sm border hover:shadow-md transition-all cursor-move ${
                      draggedOrder?.id === order.id ? 'opacity-50 transform rotate-2' : ''
                    }`}
                    draggable
                    onDragStart={(e) => handleDragStart(e, order)}
                    onDragEnd={handleDragEnd}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900 text-sm">{order.order_number}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(order.created_at).toLocaleTimeString('pt-BR', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </div>
                    
                    {/* Indicador de necessidade de nota fiscal */}
                    {order.needs_invoice && (
                      <div className="mb-2">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                          📝 Precisa de NF
                        </span>
                      </div>
                    )}
                    
                    <p className="font-medium text-gray-800 mb-1">{order.customer_name || 'Cliente não identificado'}</p>
                    <p className="text-sm text-gray-600 mb-2">{order.customer_phone || 'Sem telefone'}</p>
                    
                    <div className="space-y-1 mb-3">
                      {order.items?.slice(0, 2).map((item, idx) => (
                        <div key={idx} className="text-xs text-gray-600">
                          {item.quantity}x {item.product_name || 'Produto'}
                        </div>
                      ))}
                      {order.items && order.items.length > 2 && (
                        <div className="text-xs text-gray-500">+{order.items.length - 2} itens</div>
                      )}
                    </div>
                    
                    <div className="flex justify-between items-center mb-3">
                      <span className="font-semibold text-gray-900">R$ {order.total_amount?.toFixed(2) || '0.00'}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        order.payment_status === 'paid' ? 'bg-green-100 text-green-800' :
                        order.payment_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        order.payment_status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-orange-100 text-orange-800'
                      }`}>
                        {order.payment_status === 'paid' ? 'Pago' : 
                         order.payment_status === 'pending' ? 'Pendente' :
                         order.payment_status === 'failed' ? 'Falhou' :
                         'Reembolsado'}
                      </span>
                    </div>
                    
                    {order.delivery_address && (
                      <p className="text-xs text-gray-500 mb-2">📍 {order.delivery_address}</p>
                    )}
                    
                    <div className="flex space-x-1">
                      {status !== 'delivered' && status !== 'cancelled' && (
                        <>
                          {status === 'pending' && (
                            <button
                              onClick={() => handleStatusChange(order.id, 'confirmed')}
                              className="flex-1 bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600"
                            >
                              Confirmar
                            </button>
                          )}
                          {status === 'confirmed' && (
                            <button
                              onClick={() => handleStatusChange(order.id, 'preparing')}
                              className="flex-1 bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600"
                            >
                              Preparar
                            </button>
                          )}
                          {status === 'preparing' && (
                            <button
                              onClick={() => handleStatusChange(order.id, 'ready')}
                              className="flex-1 bg-green-500 text-white px-2 py-1 rounded text-xs hover:bg-green-600"
                            >
                              Pronto
                            </button>
                          )}
                          {status === 'ready' && (
                            <button
                              onClick={() => handleStatusChange(order.id, 'delivered')}
                              className="flex-1 bg-gray-500 text-white px-2 py-1 rounded text-xs hover:bg-gray-600"
                            >
                              Entregar
                            </button>
                          )}
                        </>
                      )}
                      
                      <button
                        onClick={() => handleEdit(order)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                        title="Editar"
                      >
                        <Edit className="w-3 h-3" />
                      </button>
                    </div>
                    
                    {/* Botão para SAT SEF/SC */}
                    <div className="mt-2 pt-2 border-t border-gray-100">
                      <button
                        onClick={() => {
                          const confirmAccess = confirm(`Deseja acessar o SAT SEF/SC para emitir nota fiscal para o pedido ${order.order_number}?`);
                          if (confirmAccess) {
                            window.open('https://sat.sef.sc.gov.br/tax.NET/Login.aspx', '_blank');
                          }
                        }}
                        className="w-full bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700 flex items-center justify-center space-x-1"
                        title="Acessar SAT SEF/SC para emitir nota fiscal"
                      >
                        <span>📝</span>
                        <span>NF SEF/SC</span>
                      </button>
                    </div>
                  </div>
                ))}
                
                {statusOrders.length === 0 && (
                  <div className="text-center text-gray-500 py-8">
                    <ShoppingCart className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Nenhum pedido</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Pedidos</h1>
          <p className="text-gray-600 mt-1">Controle e acompanhamento de pedidos</p>
        </div>
        <div className="flex space-x-3">
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('kanban')}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                viewMode === 'kanban' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Quadro
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                viewMode === 'table' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Lista
            </button>
          </div>
          <button
            onClick={() => {
              setEditingOrder(null);
              setIsFormOpen(true);
            }}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Novo Pedido
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Pedidos</p>
              <p className="text-2xl font-bold text-gray-900">{orders.length}</p>
            </div>
            <ShoppingCart className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pendentes</p>
              <p className="text-2xl font-bold text-yellow-600">{orders.filter(o => o.status === 'pending').length}</p>
            </div>
            <Clock className="w-8 h-8 text-yellow-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Confirmados</p>
              <p className="text-2xl font-bold text-blue-600">{orders.filter(o => o.status === 'confirmed').length}</p>
            </div>
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-bold text-sm">✓</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Preparando</p>
              <p className="text-2xl font-bold text-blue-600">{orders.filter(o => o.status === 'preparing').length}</p>
            </div>
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-bold text-sm">!</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Prontos</p>
              <p className="text-2xl font-bold text-green-600">{orders.filter(o => o.status === 'ready').length}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Faturamento</p>
              <p className="text-2xl font-bold text-purple-600">
                R$ {orders.reduce((sum, o) => sum + (o.total_amount || 0), 0).toFixed(2)}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div className="flex flex-col sm:flex-row gap-4 w-full lg:w-auto">
            {/* Search by customer */}
            <div className="relative flex-1 lg:w-80">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nome do cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
            
            {/* Status filter */}
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Status:</span>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                <option value="all">Todos</option>
                <option value="pending">Pendente</option>
                <option value="confirmed">Confirmado</option>
                <option value="preparing">Preparando</option>
                <option value="ready">Pronto</option>
                <option value="delivered">Entregue</option>
                <option value="cancelled">Cancelado</option>
              </select>
            </div>
          </div>
          
          <div className="text-sm text-gray-600">
            {filteredOrders.length} pedido(s) encontrado(s)
          </div>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando pedidos...</p>
          </div>
        </div>
      ) : viewMode === 'kanban' ? (
        <KanbanBoard />
      ) : (
        <DataTable
          columns={columns}
          data={filteredOrders}
          title="Lista de Pedidos"
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={(order) => {
            const itemsText = order.items?.map(item => 
              `${item.quantity}x ${item.product_name || 'Produto'} (R$ ${item.total_price.toFixed(2)})`
            ).join('\n') || 'Nenhum item';
            
            alert(`Detalhes do Pedido:\n\nPedido: ${order.order_number}\nCliente: ${order.customer_name || 'Não identificado'}\nTelefone: ${order.customer_phone || 'Não informado'}\nTotal: R$ ${order.total_amount?.toFixed(2) || '0.00'}\n\nItens:\n${itemsText}\n\n${order.delivery_address ? 'Entrega' : 'Retirada'}\nPagamento: ${order.payment_method === 'cash' ? 'Dinheiro' : order.payment_method === 'card' ? 'Cartão' : 'PIX'}\nObservações: ${order.notes || 'Nenhuma'}`);
          }}
        />
      )}

      {/* Form Modal */}
      <OrderFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingOrder(null);
        }}
        onSubmit={handleSubmit}
        title={editingOrder ? 'Editar Pedido' : 'Novo Pedido'}
        fields={formFields}
        initialData={editingOrder ? {
          customer_name: editingOrder.customer_name,
          customer_phone: editingOrder.customer_phone,
          payment_method: editingOrder.payment_method,
          payment_status: editingOrder.payment_status,
          status: editingOrder.status,
          delivery_address: editingOrder.delivery_address,
          notes: editingOrder.notes,
          needs_invoice: editingOrder.needs_invoice || false
        } : undefined}
      />
    </div>
  );
};

export default Orders;

