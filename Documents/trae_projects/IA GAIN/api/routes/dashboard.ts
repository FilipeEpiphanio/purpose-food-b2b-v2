import express from 'express';
import { supabase } from '../server';

const router = express.Router();

// Get comprehensive dashboard data integrating all modules
router.get('/', async (req, res) => {
  try {
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    const todayStart = today + 'T00:00:00';
    const todayEnd = today + 'T23:59:59';
    
    // First day of current month
    const firstDayThisMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const lastDayThisMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);
    
    // First day of last month for comparison
    const firstDayLastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const lastDayLastMonth = new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59);
    
    // Last 7 days
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 6);
    sevenDaysAgo.setHours(0, 0, 0, 0);
    
    console.log('📊 Buscando dados integrados do dashboard...');
    console.log('📅 Período do mês:', firstDayThisMonth.toISOString(), 'até', lastDayThisMonth.toISOString());
    console.log('📅 Hoje:', todayStart, 'até', todayEnd);
    
    // 1. FATURAMENTO MENSAL - Integra VENDAS, PEDIDOS e FINANCEIRO
    // Busca de pedidos pagos do mês (tanto de vendas quanto de pedidos)
    const { data: monthlyOrders, error: monthlyOrdersError } = await supabase
      .from('orders')
      .select('total_amount, status, created_at, payment_status')
      .gte('created_at', firstDayThisMonth.toISOString())
      .lte('created_at', lastDayThisMonth.toISOString())
      .in('payment_status', ['paid', 'confirmed', 'completed']);
    
    if (monthlyOrdersError) {
      console.error('Erro ao buscar pedidos do mês:', monthlyOrdersError);
    }
    
    // Busca de registros financeiros de receita do mês
    const { data: monthlyFinancialRecords, error: monthlyFinancialError } = await supabase
      .from('financial_records')
      .select('amount, type, created_at')
      .eq('type', 'revenue')
      .gte('created_at', firstDayThisMonth.toISOString())
      .lte('created_at', lastDayThisMonth.toISOString());
    
    if (monthlyFinancialError) {
      console.error('Erro ao buscar registros financeiros do mês:', monthlyFinancialError);
    }
    
    // Busca de transações do mês
    const { data: monthlyTransactions, error: monthlyTransactionsError } = await supabase
      .from('transactions')
      .select('amount, type, transaction_date')
      .in('type', ['payment', 'receipt', 'revenue', 'income'])
      .gte('transaction_date', firstDayThisMonth.toISOString())
      .lte('transaction_date', lastDayThisMonth.toISOString());
    
    if (monthlyTransactionsError) {
      console.error('Erro ao buscar transações do mês:', monthlyTransactionsError);
    }
    
    // Calcula faturamento mensal total integrado
    const monthlyRevenueFromOrders = monthlyOrders?.reduce((sum, order) => sum + (order.total_amount || 0), 0) || 0;
    const monthlyRevenueFromFinancial = monthlyFinancialRecords?.reduce((sum, record) => sum + parseFloat(record.amount || 0), 0) || 0;
    const monthlyRevenueFromTransactions = monthlyTransactions?.reduce((sum, transaction) => sum + parseFloat(transaction.amount || 0), 0) || 0;
    
    const monthlyRevenue = monthlyRevenueFromOrders + monthlyRevenueFromFinancial + monthlyRevenueFromTransactions;
    const monthlyOrdersCount = monthlyOrders?.length || 0;
    
    console.log('💰 Faturamento mensal:', monthlyRevenue);
    console.log('📦 Pedidos do mês:', monthlyOrdersCount);
    
    // 2. COMPARAÇÃO COM MÊS ANTERIOR
    const { data: lastMonthOrders } = await supabase
      .from('orders')
      .select('total_amount, status, created_at, payment_status')
      .gte('created_at', firstDayLastMonth.toISOString())
      .lte('created_at', lastDayLastMonth.toISOString())
      .in('payment_status', ['paid', 'confirmed', 'completed']);
    
    const { data: lastMonthFinancial } = await supabase
      .from('financial_records')
      .select('amount, type, created_at')
      .eq('type', 'revenue')
      .gte('created_at', firstDayLastMonth.toISOString())
      .lte('created_at', lastDayLastMonth.toISOString());
    
    const { data: lastMonthTransactions } = await supabase
      .from('transactions')
      .select('amount, type, transaction_date')
      .in('type', ['payment', 'receipt', 'revenue', 'income'])
      .gte('transaction_date', firstDayLastMonth.toISOString())
      .lte('transaction_date', lastDayLastMonth.toISOString());
    
    const lastMonthRevenue = (lastMonthOrders?.reduce((sum, order) => sum + (order.total_amount || 0), 0) || 0) +
                           (lastMonthFinancial?.reduce((sum, record) => sum + parseFloat(record.amount || 0), 0) || 0) +
                           (lastMonthTransactions?.reduce((sum, transaction) => sum + parseFloat(transaction.amount || 0), 0) || 0);
    
    const lastMonthOrdersCount = lastMonthOrders?.length || 0;
    
    const revenueVariation = lastMonthRevenue > 0 ? ((monthlyRevenue - lastMonthRevenue) / lastMonthRevenue) * 100 : 0;
    const ordersVariation = lastMonthOrdersCount > 0 ? ((monthlyOrdersCount - lastMonthOrdersCount) / lastMonthOrdersCount) * 100 : 0;
    
    // 3. VENDAS DE HOJE - Integra VENDAS, PEDIDOS e FINANCEIRO
    const { data: todayOrders } = await supabase
      .from('orders')
      .select('total_amount, status, created_at, payment_status')
      .gte('created_at', todayStart)
      .lte('created_at', todayEnd)
      .in('payment_status', ['paid', 'confirmed', 'completed']);
    
    const { data: todayFinancial } = await supabase
      .from('financial_records')
      .select('amount, type, created_at')
      .eq('type', 'revenue')
      .gte('created_at', todayStart)
      .lte('created_at', todayEnd);
    
    const { data: todayTransactions } = await supabase
      .from('transactions')
      .select('amount, type, transaction_date')
      .in('type', ['payment', 'receipt', 'revenue', 'income'])
      .gte('transaction_date', todayStart)
      .lte('transaction_date', todayEnd);
    
    const todayRevenue = (todayOrders?.reduce((sum, order) => sum + (order.total_amount || 0), 0) || 0) +
                        (todayFinancial?.reduce((sum, record) => sum + parseFloat(record.amount || 0), 0) || 0) +
                        (todayTransactions?.reduce((sum, transaction) => sum + parseFloat(transaction.amount || 0), 0) || 0);
    
    const todayOrdersCount = todayOrders?.length || 0;
    
    // 4. CLIENTES ATIVOS - Reflete módulo CLIENTES
    const { data: activeCustomersData, error: customersError } = await supabase
      .from('customers')
      .select('id, status, created_at')
      .eq('status', 'active');
    
    if (customersError) {
      console.error('Erro ao buscar clientes ativos:', customersError);
    }
    
    const activeCustomers = activeCustomersData?.length || 0;
    
    // Crescimento de clientes (últimos 30 dias)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    const { data: newCustomers } = await supabase
      .from('customers')
      .select('id, created_at')
      .gte('created_at', thirtyDaysAgo.toISOString());
    
    const customerGrowth = activeCustomers > 0 ? ((newCustomers?.length || 0) / activeCustomers) * 100 : 0;
    
    // 5. VENDAS DOS ÚLTIMOS 7 DIAS - Integra VENDAS, PEDIDOS e FINANCEIRO
    const { data: weeklyOrders } = await supabase
      .from('orders')
      .select('total_amount, status, created_at, payment_status')
      .gte('created_at', sevenDaysAgo.toISOString())
      .in('payment_status', ['paid', 'confirmed', 'completed']);
    
    const { data: weeklyFinancial } = await supabase
      .from('financial_records')
      .select('amount, type, created_at')
      .eq('type', 'revenue')
      .gte('created_at', sevenDaysAgo.toISOString());
    
    const { data: weeklyTransactions } = await supabase
      .from('transactions')
      .select('amount, type, transaction_date')
      .in('type', ['payment', 'receipt', 'revenue', 'income'])
      .gte('transaction_date', sevenDaysAgo.toISOString());
    
    // Agrupar vendas por dia da semana
    const daysOfWeek = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    const weeklySales = daysOfWeek.map(day => ({ day, value: 0 }));
    
    // Processar pedidos da semana
    weeklyOrders?.forEach(order => {
      const orderDate = new Date(order.created_at);
      const dayIndex = orderDate.getDay();
      const dayName = daysOfWeek[dayIndex];
      const dayIndexInArray = weeklySales.findIndex(day => day.day === dayName);
      
      if (dayIndexInArray !== -1) {
        weeklySales[dayIndexInArray].value += order.total_amount || 0;
      }
    });
    
    // Processar registros financeiros da semana
    weeklyFinancial?.forEach(record => {
      const recordDate = new Date(record.created_at);
      const dayIndex = recordDate.getDay();
      const dayName = daysOfWeek[dayIndex];
      const dayIndexInArray = weeklySales.findIndex(day => day.day === dayName);
      
      if (dayIndexInArray !== -1) {
        weeklySales[dayIndexInArray].value += parseFloat(record.amount || 0);
      }
    });
    
    // Processar transações da semana
    weeklyTransactions?.forEach(transaction => {
      const transactionDate = new Date(transaction.transaction_date);
      const dayIndex = transactionDate.getDay();
      const dayName = daysOfWeek[dayIndex];
      const dayIndexInArray = weeklySales.findIndex(day => day.day === dayName);
      
      if (dayIndexInArray !== -1) {
        weeklySales[dayIndexInArray].value += parseFloat(transaction.amount || 0);
      }
    });
    
    const weeklyTotal = weeklySales.reduce((sum, day) => sum + day.value, 0);
    
    console.log('📈 Vendas da semana:', weeklySales);
    console.log('💰 Total da semana:', weeklyTotal);
    
    // 6. PEDIDOS RECENTES (integrados)
    const { data: recentOrdersData, error: recentOrdersError } = await supabase
      .from('orders')
      .select(`
        id,
        order_number,
        total_amount,
        status,
        created_at,
        payment_status,
        customers (name)
      `)
      .order('created_at', { ascending: false })
      .limit(5);
    
    if (recentOrdersError) {
      console.error('Erro ao buscar pedidos recentes:', recentOrdersError);
    }
    
    // 7. PRODUTOS COM ESTOQUE BAIXO
    const { data: lowStockProducts, error: lowStockError } = await supabase
      .from('products')
      .select('name, stock, min_stock, status')
      .lte('stock', 10)
      .eq('status', 'active');
    
    if (lowStockError) {
      console.error('Erro ao buscar produtos com estoque baixo:', lowStockError);
    }
    
    console.log('✅ Dados do dashboard integrados carregados com sucesso!');
    
    res.json({
      success: true,
      data: {
        // Faturamento Mensal (integrado)
        monthlyRevenue,
        monthlyOrders: monthlyOrdersCount,
        revenueVariation,
        ordersVariation,
        
        // Vendas de Hoje (integrado)
        todayRevenue,
        todayOrders: todayOrdersCount,
        
        // Clientes Ativos
        activeCustomers,
        customerGrowth,
        
        // Vendas da Semana (integrado)
        weeklySales,
        weeklyTotal,
        
        // Dados complementares
        recentOrders: recentOrdersData || [],
        lowStockProducts: lowStockProducts || []
      }
    });
    
  } catch (error) {
    console.error('❌ Erro ao buscar dados integrados do dashboard:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Erro ao buscar dados do dashboard',
      details: error instanceof Error ? error.message : 'Erro desconhecido'
    });
  }
});

export default router;