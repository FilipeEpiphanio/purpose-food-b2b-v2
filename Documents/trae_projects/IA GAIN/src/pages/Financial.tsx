import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, CreditCard, Banknote, PiggyBank, Calendar, Filter, Download, Eye, Plus, Edit, Trash2, BarChart3, PieChart, TrendingUp as TrendingUpIcon } from 'lucide-react';
import GoalFormModal from '@/components/ui/GoalFormModal';
import TransactionFormModal from '@/components/ui/TransactionFormModal';
import CashFlowChart from '@/components/ui/CashFlowChart';
import { supabase } from '@/lib/supabase';

interface Transaction {
  id: string;
  type: 'income' | 'expense';
  category: string;
  description: string;
  amount: number;
  payment_method: 'cash' | 'card' | 'pix' | 'transfer';
  status: 'pending' | 'paid' | 'overdue' | 'cancelled';
  transaction_date: string;
  due_date?: string;
  reference_id?: string;
  reference_type?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface FinancialGoal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  deadline: string;
  category: string;
}

const Financial: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<string>('month');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [activeTab, setActiveTab] = useState<'overview' | 'transactions' | 'goals' | 'reports'>('overview');
  const [isGoalFormOpen, setIsGoalFormOpen] = useState(false);
  const [isTransactionFormOpen, setIsTransactionFormOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<FinancialGoal | null>(null);
  const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [goals, setGoals] = useState<FinancialGoal[]>([]);
  const [loading, setLoading] = useState(true);

  // Função para buscar metas financeiras do Supabase
  const fetchFinancialGoals = async () => {
    try {
      const { data, error } = await supabase
        .from('financial_goals')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Erro ao buscar metas:', error);
      } else {
        setGoals(data || []);
      }
    } catch (error) {
      console.error('Erro ao buscar metas financeiras:', error);
    }
  };

  // Buscar transações e metas do Supabase
  useEffect(() => {
    fetchFinancialData();
  }, []);

  const fetchFinancialData = async () => {
    try {
      setLoading(true);
      
      // Buscar transações financeiras da tabela correta
      const { data: transactionsData, error: transactionsError } = await supabase
        .from('transactions')
        .select('*')
        .order('transaction_date', { ascending: false });

      if (transactionsError) {
        console.error('Erro ao buscar transações:', transactionsError);
      } else {
        setTransactions(transactionsData || []);
      }

      // Buscar metas financeiras
      await fetchFinancialGoals();
    } catch (error) {
      console.error('Erro ao buscar dados financeiros:', error);
    } finally {
      setLoading(false);
    }
  };

  // Adicionar listener para atualização quando uma venda for concluída
  useEffect(() => {
    const handleSaleCompleted = () => {
      console.log('Venda concluída detectada, atualizando dados financeiros...');
      fetchFinancialData();
    };

    window.addEventListener('saleCompleted', handleSaleCompleted);
    
    return () => {
      window.removeEventListener('saleCompleted', handleSaleCompleted);
    };
  }, []);

  // Filter transactions by period
  const getFilteredTransactionsByPeriod = () => {
    const now = new Date();
    const startOfPeriod = new Date();
    
    switch (selectedPeriod) {
      case 'day':
        startOfPeriod.setHours(0, 0, 0, 0);
        break;
      case 'week':
        startOfPeriod.setDate(now.getDate() - 7);
        break;
      case 'month':
        startOfPeriod.setDate(1);
        startOfPeriod.setHours(0, 0, 0, 0);
        break;
      case 'quarter':
        const quarter = Math.floor(now.getMonth() / 3);
        startOfPeriod.setMonth(quarter * 3, 1);
        startOfPeriod.setHours(0, 0, 0, 0);
        break;
      case 'year':
        startOfPeriod.setMonth(0, 1);
        startOfPeriod.setHours(0, 0, 0, 0);
        break;
      default:
        startOfPeriod.setDate(1);
        startOfPeriod.setHours(0, 0, 0, 0);
    }

    return transactions.filter(t => new Date(t.transaction_date) >= startOfPeriod);
  };

  const filteredTransactions = getFilteredTransactionsByPeriod().filter(t => {
    if (filterCategory !== 'all' && t.type !== filterCategory) return false;
    if (filterType !== 'all' && t.category !== filterType) return false;
    return true;
  });

  // Calculations based on selected period
  const periodTransactions = getFilteredTransactionsByPeriod();
  const totalRevenue = periodTransactions.filter(t => t.type === 'income' && t.status === 'paid').reduce((sum, t) => sum + t.amount, 0);
  const totalExpenses = periodTransactions.filter(t => t.type === 'expense' && t.status === 'paid').reduce((sum, t) => sum + t.amount, 0);
  const netProfit = totalRevenue - totalExpenses;
  const profitMargin = totalRevenue > 0 ? (netProfit / totalRevenue) * 100 : 0;

  const pendingRevenue = periodTransactions.filter(t => t.type === 'income' && t.status === 'pending').reduce((sum, t) => sum + t.amount, 0);
  const pendingExpenses = periodTransactions.filter(t => t.type === 'expense' && t.status === 'pending').reduce((sum, t) => sum + t.amount, 0);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'overdue': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (type: string) => {
    return type === 'income' ? 'text-green-600' : 'text-red-600';
  };

  const getPaymentMethodIcon = (method: string) => {
    switch (method) {
      case 'cash': return <Banknote className="w-4 h-4" />;
      case 'card': return <CreditCard className="w-4 h-4" />;
      case 'pix': return <DollarSign className="w-4 h-4" />;
      case 'transfer': return <DollarSign className="w-4 h-4" />;
      default: return <DollarSign className="w-4 h-4" />;
    }
  };

  // Generate cash flow data for chart
  const generateCashFlowData = () => {
    const data = [];
    const now = new Date();
    const days = selectedPeriod === 'day' ? 1 : selectedPeriod === 'week' ? 7 : selectedPeriod === 'month' ? 30 : selectedPeriod === 'quarter' ? 90 : 365;
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      const dayTransactions = periodTransactions.filter(t => t.transaction_date === dateStr);
      const revenue = dayTransactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
      const expenses = dayTransactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
      
      data.push({
        date: dateStr,
        revenue,
        expenses,
        netFlow: revenue - expenses
      });
    }
    
    return data;
  };

  // Funções para transações
  const handleTransactionSubmit = async (data: any, action: 'save-exit' | 'save-new') => {
    try {
      if (editingTransaction) {
        // Atualizar transação existente
        const { error } = await supabase
          .from('financial_transactions')
          .update({
            type: data.type,
            category: data.category,
            description: data.description,
            amount: data.amount,
            payment_method: data.payment_method,
            status: data.status,
            transaction_date: data.transaction_date,
            due_date: data.due_date,
            reference_id: data.reference_id,
            reference_type: data.reference_type,
            notes: data.notes,
            updated_at: new Date().toISOString()
          })
          .eq('id', editingTransaction.id);

        if (error) {
          console.error('Erro ao atualizar transação:', error);
        } else {
          await fetchFinancialData();
          if (action === 'save-exit') {
            setIsTransactionFormOpen(false);
            setEditingTransaction(null);
          }
        }
      } else {
        // Criar nova transação
        const { error } = await supabase
          .from('financial_transactions')
          .insert({
            type: data.type,
            category: data.category,
            description: data.description,
            amount: data.amount,
            payment_method: data.payment_method,
            status: data.status,
            transaction_date: data.transaction_date,
            due_date: data.due_date,
            reference_id: data.reference_id,
            reference_type: data.reference_type,
            notes: data.notes,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          });

        if (error) {
          console.error('Erro ao criar transação:', error);
        } else {
          await fetchFinancialData();
          if (action === 'save-exit') {
            setIsTransactionFormOpen(false);
          }
        }
      }
    } catch (error) {
      console.error('Erro ao salvar transação:', error);
    }
  };

  const handleEditTransaction = (transaction: Transaction) => {
    setEditingTransaction(transaction);
    setIsTransactionFormOpen(true);
  };

  const handleDeleteTransaction = async (transaction: Transaction) => {
    if (confirm(`Deseja realmente excluir a transação "${transaction.description}"?`)) {
      try {
        const { error } = await supabase
          .from('financial_transactions')
          .delete()
          .eq('id', transaction.id);

        if (error) {
          console.error('Erro ao excluir transação:', error);
        } else {
          await fetchFinancialData();
        }
      } catch (error) {
        console.error('Erro ao excluir transação:', error);
      }
    }
  };

  const handleGoalSubmit = async (data: any, action: 'save-exit' | 'save-new') => {
    try {
      if (editingGoal) {
        // Atualizar meta existente
        const { error } = await supabase
          .from('financial_goals')
          .update({
            name: data.name,
            target_amount: data.targetAmount,
            current_amount: data.currentAmount,
            deadline: data.deadline,
            category: data.category,
            updated_at: new Date().toISOString()
          })
          .eq('id', editingGoal.id);

        if (error) {
          console.error('Erro ao atualizar meta:', error);
        } else {
          await fetchFinancialGoals();
          if (action === 'save-exit') {
            setIsGoalFormOpen(false);
            setEditingGoal(null);
          }
        }
      } else {
        // Criar nova meta
        const { error } = await supabase
          .from('financial_goals')
          .insert({
            name: data.name,
            target_amount: data.targetAmount,
            current_amount: data.currentAmount || 0,
            deadline: data.deadline,
            category: data.category,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          });

        if (error) {
          console.error('Erro ao criar meta:', error);
        } else {
          await fetchFinancialGoals();
          if (action === 'save-exit') {
            setIsGoalFormOpen(false);
          }
        }
      }
    } catch (error) {
      console.error('Erro ao salvar meta:', error);
    }
  };

  const handleEditGoal = (goal: FinancialGoal) => {
    setEditingGoal(goal);
    setIsGoalFormOpen(true);
  };

  const handleDeleteGoal = async (goal: FinancialGoal) => {
    if (confirm(`Deseja realmente excluir a meta ${goal.name}?`)) {
      try {
        const { error } = await supabase
          .from('financial_goals')
          .delete()
          .eq('id', goal.id);

        if (error) {
          console.error('Erro ao excluir meta:', error);
        } else {
          await fetchFinancialGoals();
        }
      } catch (error) {
        console.error('Erro ao excluir meta:', error);
      }
    }
  };

  const exportToCSV = () => {
    const csvContent = [
      'Data,Descrição,Categoria,Tipo,Valor,Forma de Pagamento,Status',
      ...filteredTransactions.map(t => 
        `${t.transaction_date},${t.description},${t.type === 'income' ? 'Receita' : 'Despesa'},${t.category},R$ ${t.amount.toFixed(2)},${t.payment_method},${t.status}`
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transacoes_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const OverviewTab = () => (
    <div className="space-y-6">
      {/* Financial Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Receita Total</p>
              <p className="text-2xl font-bold text-green-600">R$ {totalRevenue.toFixed(2)}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Despesas Totais</p>
              <p className="text-2xl font-bold text-red-600">R$ {totalExpenses.toFixed(2)}</p>
            </div>
            <TrendingDown className="w-8 h-8 text-red-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Lucro Líquido</p>
              <p className={`text-2xl font-bold ${netProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                R$ {netProfit.toFixed(2)}
              </p>
            </div>
            <DollarSign className={`w-8 h-8 ${netProfit >= 0 ? 'text-green-500' : 'text-red-500'}`} />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Margem de Lucro</p>
              <p className={`text-2xl font-bold ${profitMargin >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {profitMargin.toFixed(1)}%
              </p>
            </div>
            <PiggyBank className={`w-8 h-8 ${profitMargin >= 0 ? 'text-green-500' : 'text-red-500'}`} />
          </div>
        </div>
      </div>

      {/* Pending Transactions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Receitas Pendentes</h3>
          <div className="space-y-3">
            {periodTransactions.filter(t => t.type === 'income' && t.status === 'pending').map(t => (
              <div key={t.id} className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{t.description}</p>
                  <p className="text-sm text-gray-600">{new Date(t.transaction_date).toLocaleDateString('pt-BR')}</p>
                </div>
                <span className="font-semibold text-yellow-600">R$ {t.amount.toFixed(2)}</span>
              </div>
            ))}
            {pendingRevenue === 0 && (
              <p className="text-gray-500 text-center py-4">Nenhuma receita pendente</p>
            )}
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Despesas Pendentes</h3>
          <div className="space-y-3">
            {periodTransactions.filter(t => t.type === 'expense' && t.status === 'pending').map(t => (
              <div key={t.id} className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{t.description}</p>
                  <p className="text-sm text-gray-600">{new Date(t.transaction_date).toLocaleDateString('pt-BR')}</p>
                </div>
                <span className="font-semibold text-orange-600">R$ {t.amount.toFixed(2)}</span>
              </div>
            ))}
            {pendingExpenses === 0 && (
              <p className="text-gray-500 text-center py-4">Nenhuma despesa pendente</p>
            )}
          </div>
        </div>
      </div>

      {/* Cash Flow Chart */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Fluxo de Caixa</h3>
        <CashFlowChart data={generateCashFlowData()} period={selectedPeriod} />
      </div>
    </div>
  );

  const TransactionsTab = () => (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                <option value="all">Todas</option>
                <option value="income">Receita</option>
                <option value="expense">Despesa</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                <option value="all">Todos</option>
                <option value="Venda de Produtos">Venda de Produtos</option>
                <option value="Serviços Prestados">Serviços Prestados</option>
                <option value="Compra de Produtos">Compra de Produtos</option>
                <option value="Salários">Salários</option>
                <option value="Aluguel">Aluguel</option>
                <option value="Utilidades">Utilidades</option>
                <option value="Marketing">Marketing</option>
                <option value="Outros">Outros</option>
              </select>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => {
                setEditingTransaction(null);
                setIsTransactionFormOpen(true);
              }}
              className="flex items-center px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nova Transação
            </button>
            <button
              onClick={exportToCSV}
              className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </button>
          </div>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Transações</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoria</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pagamento</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTransactions.map((transaction) => (
                <tr key={transaction.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(transaction.transaction_date).toLocaleDateString('pt-BR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transaction.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      transaction.type === 'income' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {transaction.type === 'income' ? 'Receita' : 'Despesa'}
                    </span>
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getCategoryColor(transaction.type)}`}>
                    R$ {transaction.amount.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center space-x-2">
                      {getPaymentMethodIcon(transaction.payment_method)}
                      <span className="capitalize">{transaction.payment_method}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(transaction.status)}`}>
                      {transaction.status === 'paid' ? 'Pago' : 
                       transaction.status === 'pending' ? 'Pendente' : 
                       transaction.status === 'overdue' ? 'Vencido' : 'Cancelado'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEditTransaction(transaction)}
                        className="text-orange-600 hover:text-orange-800 p-1"
                        title="Editar transação"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteTransaction(transaction)}
                        className="text-red-600 hover:text-red-800 p-1"
                        title="Excluir transação"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const GoalsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">Metas Financeiras</h2>
        <button
          onClick={() => {
            setEditingGoal(null);
            setIsGoalFormOpen(true);
          }}
          className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nova Meta
        </button>
      </div>
      
      <div className="space-y-4">
        {goals.map((goal) => {
          const progress = (goal.currentAmount / goal.targetAmount) * 100;
          const daysLeft = Math.ceil((new Date(goal.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
          
          return (
            <div key={goal.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-medium text-gray-900">{goal.name}</h3>
                  <p className="text-sm text-gray-600">{goal.category}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">{daysLeft} dias restantes</span>
                  <button
                    onClick={() => handleEditGoal(goal)}
                    className="text-orange-600 hover:text-orange-800 p-1"
                    title="Editar meta"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteGoal(goal)}
                    className="text-red-600 hover:text-red-800 p-1"
                    title="Excluir meta"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span>R$ {goal.currentAmount.toFixed(2)}</span>
                  <span>R$ {goal.targetAmount.toFixed(2)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(progress, 100)}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-1">{progress.toFixed(1)}% completo</p>
              </div>
            </div>
          );
        })}
      </div>

      <GoalFormModal
        isOpen={isGoalFormOpen}
        onClose={() => {
          setIsGoalFormOpen(false);
          setEditingGoal(null);
        }}
        onSubmit={handleGoalSubmit}
        title={editingGoal ? 'Editar Meta' : 'Nova Meta'}
        initialData={editingGoal || {}}
      />
    </div>
  );

  const ReportsTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Relatório de Vendas</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Vendas por Produto</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Vendas por Período</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Clientes Mais Frequentes</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Relatório Financeiro</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Fluxo de Caixa</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">DRE (Demonstração de Resultados)</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Análise de Margem de Lucro</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Relatório de Estoque</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Produtos em Falta</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Movimentação de Estoque</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Análise de Giro de Estoque</span>
              <button className="text-orange-600 hover:text-orange-800 text-sm">Gerar</button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Relatórios Personalizados</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Período</label>
            <div className="flex space-x-2">
              <input
                type="date"
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
              <input
                type="date"
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>
          </div>
          <div className="flex items-end">
            <button className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors">
              Gerar Relatório Personalizado
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Módulo Financeiro</h1>
          <p className="text-gray-600 mt-1">Controle financeiro completo do seu negócio</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Período</label>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            >
              <option value="day">Hoje</option>
              <option value="week">Esta Semana</option>
              <option value="month">Este Mês</option>
              <option value="quarter">Este Trimestre</option>
              <option value="year">Este Ano</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'overview', label: 'Visão Geral' },
            { key: 'transactions', label: 'Transações' },
            { key: 'goals', label: 'Metas' },
            { key: 'reports', label: 'Relatórios' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-orange-500 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'transactions' && <TransactionsTab />}
      {activeTab === 'goals' && <GoalsTab />}
      {activeTab === 'reports' && <ReportsTab />}

      {/* Goal Form Modal */}
      <GoalFormModal
        isOpen={isGoalFormOpen}
        onClose={() => {
          setIsGoalFormOpen(false);
          setEditingGoal(null);
        }}
        onSubmit={handleGoalSubmit}
        title={editingGoal ? 'Editar Meta' : 'Nova Meta'}
        initialData={editingGoal || {}}
      />

      {/* Transaction Form Modal */}
      <TransactionFormModal
        isOpen={isTransactionFormOpen}
        onClose={() => {
          setIsTransactionFormOpen(false);
          setEditingTransaction(null);
        }}
        onSubmit={handleTransactionSubmit}
        title={editingTransaction ? 'Editar Transação' : 'Nova Transação'}
        initialData={editingTransaction || {}}
      />
    </div>
  );
};

export default Financial;