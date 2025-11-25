import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MetricCard from '@/components/MetricCard';
import SalesChart from '@/components/ui/SalesChart';
import PurposeFoodLogo from '@/components/ui/PurposeFoodLogo';
import UpcomingEventsWidget from '@/components/Dashboard/UpcomingEventsWidget';
import { supabase } from '@/lib/supabase';
import { 
  TrendingUp, 
  Package, 
  ShoppingCart, 
  Users, 
  DollarSign,
  AlertTriangle,
  Clock,
  CheckCircle,
  Clock3,
  Utensils,
  ChefHat
} from 'lucide-react';

interface DashboardData {
  totalRevenue: number;
  totalOrders: number;
  totalCustomers: number;
  avgOrderValue: number;
  lowStockProducts: any[];
  recentOrders: any[];
  monthlyOrders: number;
  monthlyRevenue: number;
  activeCustomers: number;
  ordersVariation: number;
  revenueVariation: number;
  customerGrowth: number;
  weeklySales: Array<{ day: string; value: number }>;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    totalRevenue: 0,
    totalOrders: 0,
    totalCustomers: 0,
    avgOrderValue: 0,
    lowStockProducts: [],
    recentOrders: [],
    monthlyOrders: 0,
    monthlyRevenue: 0,
    activeCustomers: 0,
    ordersVariation: 0,
    revenueVariation: 0,
    customerGrowth: 0,
    weeklySales: [
      { day: 'Seg', value: 0 },
      { day: 'Ter', value: 0 },
      { day: 'Qua', value: 0 },
      { day: 'Qui', value: 0 },
      { day: 'Sex', value: 0 },
      { day: 'Sáb', value: 0 },
      { day: 'Dom', value: 0 }
    ]
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('📊 Buscando dados integrados do dashboard...');
      
      // Buscar dados integrados do novo endpoint de dashboard
      const response = await fetch('/api/dashboard');
      
      if (!response.ok) {
        throw new Error('Erro ao buscar dados do dashboard');
      }
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Erro ao buscar dados do dashboard');
      }
      
      const data = result.data;
      
      console.log('✅ Dados integrados do dashboard carregados:', data);
      
      setDashboardData({
        totalRevenue: data.todayRevenue || 0,
        totalOrders: data.todayOrders || 0,
        totalCustomers: data.activeCustomers || 0,
        avgOrderValue: data.todayOrders > 0 ? data.todayRevenue / data.todayOrders : 0,
        lowStockProducts: data.lowStockProducts || [],
        recentOrders: data.recentOrders || [],
        monthlyOrders: data.monthlyOrders || 0,
        monthlyRevenue: data.monthlyRevenue || 0,
        activeCustomers: data.activeCustomers || 0,
        ordersVariation: data.ordersVariation || 0,
        revenueVariation: data.revenueVariation || 0,
        customerGrowth: data.customerGrowth || 0,
        weeklySales: data.weeklySales || [
          { day: 'Seg', value: 0 },
          { day: 'Ter', value: 0 },
          { day: 'Qua', value: 0 },
          { day: 'Qui', value: 0 },
          { day: 'Sex', value: 0 },
          { day: 'Sáb', value: 0 },
          { day: 'Dom', value: 0 }
        ]
      });
      
      console.log('✅ Dashboard atualizado com dados integrados de todos os módulos!');
      
    } catch (error) {
      console.error('❌ Erro ao buscar dados do dashboard:', error);
      setError('Erro ao carregar dados do dashboard. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleNewOrder = () => {
    navigate('/pedidos');
  };

  const handleNewSale = () => {
    navigate('/vendas');
  };

  const handleViewAllOrders = () => {
    navigate('/pedidos');
  };

  const handleManageStock = () => {
    navigate('/produtos');
  };

  const handleQuickAction = (path: string) => {
    navigate(path);
  };
  const metrics = [
    {
      title: 'Faturamento Mensal',
      value: `R$ ${dashboardData.monthlyRevenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
      change: `${dashboardData.revenueVariation >= 0 ? '+' : ''}${dashboardData.revenueVariation.toFixed(1)}% vs mês passado`,
      changeType: dashboardData.revenueVariation >= 0 ? 'positive' as const : 'negative' as const,
      icon: <DollarSign className="w-6 h-6" />,
      color: 'green' as const
    },
    {
      title: 'Pedidos do Mês',
      value: dashboardData.monthlyOrders.toString(),
      change: `${dashboardData.ordersVariation >= 0 ? '+' : ''}${dashboardData.ordersVariation.toFixed(1)}% vs mês passado`,
      changeType: dashboardData.ordersVariation >= 0 ? 'positive' as const : 'negative' as const,
      icon: <ShoppingCart className="w-6 h-6" />,
      color: 'blue' as const
    },
    {
      title: 'Clientes Ativos',
      value: dashboardData.activeCustomers.toString(),
      change: dashboardData.customerGrowth > 0 ? `Base ${dashboardData.customerGrowth.toFixed(0)}% maior` : 'Base estável',
      changeType: dashboardData.customerGrowth > 0 ? 'positive' as const : 'neutral' as const,
      icon: <Users className="w-6 h-6" />,
      color: 'purple' as const
    },
    {
      title: 'Vendas Hoje',
      value: `R$ ${dashboardData.totalRevenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
      change: dashboardData.totalRevenue > 0 ? 'Vendas realizadas' : 'Sem vendas hoje',
      changeType: dashboardData.totalRevenue > 0 ? 'positive' as const : 'neutral' as const,
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'orange' as const
    }
  ];

  const recentOrders = dashboardData.recentOrders.map(order => ({
    id: order.order_number || `PED-${order.id.toString().padStart(3, '0')}`,
    customer: order.customers?.name || 'Cliente não identificado',
    total: `R$ ${order.total_amount?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    status: order.status || 'pending',
    time: new Date(order.order_date).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }));

  const lowStockItems = dashboardData.lowStockProducts.map(product => ({
    name: product.name,
    current: product.stock,
    min: product.min_stock
  }));

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'preparing':
        return 'bg-yellow-100 text-yellow-800';
      case 'delivered':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'preparing':
        return <Clock className="w-4 h-4" />;
      case 'delivered':
        return <CheckCircle className="w-4 h-4" />;
      case 'pending':
        return <Clock3 className="w-4 h-4" />;
      default:
        return <Clock3 className="w-4 h-4" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Concluído';
      case 'preparing':
        return 'Preparando';
      case 'delivered':
        return 'Entregue';
      case 'pending':
        return 'Pendente';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="text-red-500 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-red-800 mb-2">Erro ao carregar dashboard</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  const noDataMessage = (
    <div className="text-center py-8">
      <div className="text-gray-400 mb-2">
        <Package className="w-12 h-12 mx-auto" />
      </div>
      <p className="text-gray-500">Nenhum dado disponível</p>
      <p className="text-sm text-gray-400 mt-1">Execute o script SQL para popular os dados</p>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-4">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Bem-vindo ao PURPOSE FOOD!</h1>
            <div className="flex items-center gap-2 text-gray-300">
              <Utensils className="w-8 h-8" />
              <ChefHat className="w-8 h-8" />
            </div>
          </div>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={handleNewOrder}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors"
          >
            Novo Pedido
          </button>
          <button 
            onClick={handleNewSale}
            className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors"
          >
            Nova Venda
          </button>
        </div>
      </div>
      <p className="text-gray-600 text-lg mb-8">Aqui está um resumo de como anda seu negócio hoje</p>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 lg:gap-6">
        {metrics.map((metric, index) => (
          <MetricCard key={index} {...metric} />
        ))}
      </div>

      {/* Sales Chart */}
      <SalesChart data={dashboardData.weeklySales} />

      {/* Upcoming Events */}
      <UpcomingEventsWidget />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Orders */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Pedidos Recentes</h2>
            <button 
              onClick={handleViewAllOrders}
              className="text-orange-500 hover:text-orange-600 text-sm font-medium"
            >
              Ver todos
            </button>
          </div>
          <div className="space-y-4">
            {recentOrders.length > 0 ? (
              recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="bg-white p-2 rounded-lg shadow-sm">
                      <ShoppingCart className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{order.id}</p>
                      <p className="text-sm text-gray-600">{order.customer}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{order.total}</p>
                      <p className="text-sm text-gray-500">{order.time}</p>
                    </div>
                    <div className={'flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ' + getStatusColor(order.status)}>
                      {getStatusIcon(order.status)}
                      <span>{getStatusLabel(order.status)}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <ShoppingCart className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                <p className="text-gray-500">Nenhum pedido recente</p>
              </div>
            )}
          </div>
        </div>

        {/* Low Stock Alerts */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Alertas de Estoque Baixo</h2>
            <AlertTriangle className="w-5 h-5 text-orange-500" />
          </div>
          <div className="space-y-4">
            {lowStockItems.length > 0 ? (
              lowStockItems.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="bg-white p-2 rounded-lg shadow-sm">
                      <Package className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{item.name}</p>
                      <p className="text-sm text-gray-600">Estoque: {item.current} unidades</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-orange-600">Mínimo: {item.min}</p>
                    <p className="text-xs text-orange-500">Reabastecer</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Package className="w-12 h-12 text-green-500 mx-auto mb-2" />
                <p className="text-gray-500">Nenhum produto com estoque baixo</p>
              </div>
            )}
          </div>
          <button 
            onClick={handleManageStock}
            className="w-full mt-4 bg-orange-500 text-white py-2 rounded-lg hover:bg-orange-600 transition-colors"
          >
            Gerenciar Estoque
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Ações Rápidas</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => handleQuickAction('/produtos')}
            className="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Package className="w-8 h-8 text-orange-500 mb-2" />
            <span className="text-sm font-medium text-gray-900">Produtos</span>
          </button>
          <button 
            onClick={() => handleQuickAction('/pedidos')}
            className="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ShoppingCart className="w-8 h-8 text-green-500 mb-2" />
            <span className="text-sm font-medium text-gray-900">Pedidos</span>
          </button>
          <button 
            onClick={() => handleQuickAction('/clientes')}
            className="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <Users className="w-8 h-8 text-blue-500 mb-2" />
            <span className="text-sm font-medium text-gray-900">Clientes</span>
          </button>
          <button 
            onClick={() => handleQuickAction('/financeiro')}
            className="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <DollarSign className="w-8 h-8 text-purple-500 mb-2" />
            <span className="text-sm font-medium text-gray-900">Financeiro</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;