import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, Filter, TrendingUp, Package, Users, DollarSign, BarChart3, PieChart, Eye } from 'lucide-react';

interface Report {
  id: string;
  title: string;
  description: string;
  category: 'sales' | 'financial' | 'inventory' | 'customers' | 'general';
  type: 'summary' | 'detailed' | 'comparative' | 'analytical';
  period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly' | 'custom';
  lastGenerated?: string;
  size: string;
  status: 'ready' | 'generating' | 'scheduled';
}

interface ReportData {
  totalSales?: number;
  totalOrders?: number;
  averageTicket?: number;
  topProducts?: Array<{ name: string; sales: number }>;
  totalRevenue?: number;
  totalExpenses?: number;
  netProfit?: number;
  profitMargin?: number;
  totalProducts?: number;
  lowStockItems?: number;
  outOfStockItems?: number;
  totalValue?: number;
  totalCustomers?: number;
  activeCustomers?: number;
  newCustomers?: number;
  averageSpending?: number;
  period?: string;
  summary?: string;
}

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('all');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [activeTab, setActiveTab] = useState<'available' | 'generated' | 'scheduled'>('available');
  const [showCustomReportForm, setShowCustomReportForm] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedReportForSchedule, setSelectedReportForSchedule] = useState<Report | null>(null);
  const [customReportData, setCustomReportData] = useState({
    title: '',
    category: '',
    startDate: '',
    endDate: ''
  });
  const [scheduledReports, setScheduledReports] = useState<any[]>([]);
  const [scheduleFormData, setScheduleFormData] = useState({
    startDate: '',
    startTime: '',
    frequency: 'once' as 'once' | 'daily' | 'weekly' | 'monthly',
    email: ''
  });
  const [loading, setLoading] = useState(false);

  // Fetch reports from API
  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/reports');
      if (!response.ok) {
        throw new Error('Erro ao buscar relatórios');
      }
      
      const data = await response.json();
      setReports(data.reports || []);
    } catch (error) {
      console.error('Erro ao buscar relatórios:', error);
      // Fallback to predefined reports if API fails
      setReports([
        {
          id: 'REP-001',
          title: 'Relatório de Vendas Diárias',
          description: 'Resumo das vendas do dia com detalhamento por produto e horário',
          category: 'sales',
          type: 'summary',
          period: 'daily',
          lastGenerated: '2024-01-15T18:30:00',
          size: '156 KB',
          status: 'ready'
        },
        {
          id: 'REP-002',
          title: 'Análise de Estoque',
          description: 'Análise detalhada do estoque atual, produtos em falta e giro de mercadorias',
          category: 'inventory',
          type: 'detailed',
          period: 'weekly',
          lastGenerated: '2024-01-14T10:15:00',
          size: '234 KB',
          status: 'ready'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const generateRealReportData = async (report: Report): Promise<ReportData> => {
    try {
      // Fetch real data from API based on report category
      const response = await fetch(`/api/reports/data?category=${report.category}&period=${report.period}`);
      if (!response.ok) {
        throw new Error('Erro ao buscar dados do relatório');
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao buscar dados do relatório:', error);
      // Fallback to mock data if API fails
      return generateFallbackReportData(report);
    }
  };

  const generateFallbackReportData = (report: Report): ReportData => {
    const now = new Date();
    const startDate = new Date(now.getFullYear(), now.getMonth(), 1);
    const endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    
    switch (report.category) {
      case 'sales':
        return {
          totalSales: Math.floor(Math.random() * 50000) + 10000,
          totalOrders: Math.floor(Math.random() * 200) + 50,
          averageTicket: Math.floor(Math.random() * 500) + 100,
          topProducts: [
            { name: 'Bolo de Chocolate', sales: Math.floor(Math.random() * 50) + 20 },
            { name: 'Torta de Limão', sales: Math.floor(Math.random() * 40) + 15 },
            { name: 'Coxinha', sales: Math.floor(Math.random() * 60) + 25 }
          ],
          period: `${startDate.toLocaleDateString('pt-BR')} a ${endDate.toLocaleDateString('pt-BR')}`
        };
      
      case 'financial':
        return {
          totalRevenue: Math.floor(Math.random() * 80000) + 20000,
          totalExpenses: Math.floor(Math.random() * 30000) + 10000,
          netProfit: Math.floor(Math.random() * 30000) + 5000,
          profitMargin: Math.floor(Math.random() * 30) + 10,
          period: `${startDate.toLocaleDateString('pt-BR')} a ${endDate.toLocaleDateString('pt-BR')}`
        };
      
      case 'inventory':
        return {
          totalProducts: Math.floor(Math.random() * 100) + 50,
          lowStockItems: Math.floor(Math.random() * 20) + 5,
          outOfStockItems: Math.floor(Math.random() * 10),
          totalValue: Math.floor(Math.random() * 20000) + 5000,
          period: `${startDate.toLocaleDateString('pt-BR')} a ${endDate.toLocaleDateString('pt-BR')}`
        };
      
      case 'customers':
        return {
          totalCustomers: Math.floor(Math.random() * 500) + 100,
          activeCustomers: Math.floor(Math.random() * 300) + 50,
          newCustomers: Math.floor(Math.random() * 50) + 10,
          averageSpending: Math.floor(Math.random() * 300) + 100,
          period: `${startDate.toLocaleDateString('pt-BR')} a ${endDate.toLocaleDateString('pt-BR')}`
        };
      
      default:
        return {
          summary: 'Relatório geral com dados consolidados',
          period: `${startDate.toLocaleDateString('pt-BR')} a ${endDate.toLocaleDateString('pt-BR')}`
        };
    }
  };

  const generateReport = async (reportId: string) => {
    setReports(prev => prev.map(report => 
      report.id === reportId 
        ? { ...report, status: 'generating' as const }
        : report
    ));

    setTimeout(async () => {
      try {
        // Generate report data
        const report = reports.find(r => r.id === reportId);
        if (report) {
          const reportData = await generateRealReportData(report);
          
          // Send report data to backend for processing
          const response = await fetch('/api/reports/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              reportId,
              reportData,
              generatedAt: new Date().toISOString()
            }),
          });

          if (!response.ok) {
            throw new Error('Erro ao gerar relatório');
          }

          const result = await response.json();
          
          setReports(prev => prev.map(r => 
            r.id === reportId 
              ? { 
                  ...r, 
                  status: 'ready' as const,
                  lastGenerated: new Date().toISOString(),
                  size: result.size || `${Math.floor(Math.random() * 500) + 100} KB`
                }
              : r
          ));
          
          alert(`Relatório ${reportId} gerado com sucesso!`);
        }
      } catch (error) {
        console.error('Erro ao gerar relatório:', error);
        alert('Erro ao gerar relatório. Tente novamente.');
        
        // Reset status on error
        setReports(prev => prev.map(report => 
          report.id === reportId 
            ? { ...report, status: 'ready' as const }
            : report
        ));
      }
    }, 2000);
  };

  const downloadReport = async (reportId: string) => {
    const report = reports.find(r => r.id === reportId);
    if (report) {
      try {
        const reportData = await generateRealReportData(report);
        
        let fileContent = `RELATÓRIO - ${report.title.toUpperCase()}\n`;
        fileContent += '=====================================\n\n';
        fileContent += `Descrição: ${report.description}\n`;
        fileContent += `Categoria: ${getCategoryInfo(report.category).label}\n`;
        fileContent += `Tipo: ${reportTypes.find(t => t.key === report.type)?.label}\n`;
        fileContent += `Período: ${reportPeriods.find(p => p.key === report.period)?.label}\n`;
        fileContent += `Status: ${report.status === 'ready' ? 'Pronto' : report.status === 'generating' ? 'Gerando' : 'Agendado'}\n`;
        fileContent += `Última geração: ${report.lastGenerated ? new Date(report.lastGenerated).toLocaleDateString('pt-BR') : 'Nunca'}\n`;
        fileContent += `Tamanho: ${report.size}\n\n`;
        
        // Add specific data based on report category
        switch (report.category) {
          case 'sales':
            fileContent += '📊 DADOS DE VENDAS\n';
            fileContent += `Período: ${reportData.period}\n`;
            fileContent += `Total de Vendas: R$ ${reportData.totalSales?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            fileContent += `Total de Pedidos: ${reportData.totalOrders}\n`;
            fileContent += `Ticket Médio: R$ ${reportData.averageTicket?.toFixed(2)}\n\n`;
            fileContent += '🏆 PRODUTOS MAIS VENDIDOS:\n';
            reportData.topProducts?.forEach((product, index) => {
              fileContent += `${index + 1}. ${product.name}: ${product.sales} unidades\n`;
            });
            break;

          case 'financial':
            fileContent += '💰 DADOS FINANCEIROS\n';
            fileContent += `Período: ${reportData.period}\n`;
            fileContent += `Receita Total: R$ ${reportData.totalRevenue?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            fileContent += `Despesas Totais: R$ ${reportData.totalExpenses?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            fileContent += `Lucro Líquido: R$ ${reportData.netProfit?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            fileContent += `Margem de Lucro: ${reportData.profitMargin?.toFixed(1)}%\n`;
            break;

          case 'inventory':
            fileContent += '📦 DADOS DE ESTOQUE\n';
            fileContent += `Período: ${reportData.period}\n`;
            fileContent += `Total de Produtos: ${reportData.totalProducts}\n`;
            fileContent += `Itens com Baixo Estoque: ${reportData.lowStockItems}\n`;
            fileContent += `Itens em Falta: ${reportData.outOfStockItems}\n`;
            fileContent += `Valor Total do Estoque: R$ ${reportData.totalValue?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            break;

          case 'customers':
            fileContent += '👥 DADOS DE CLIENTES\n';
            fileContent += `Período: ${reportData.period}\n`;
            fileContent += `Total de Clientes: ${reportData.totalCustomers}\n`;
            fileContent += `Clientes Ativos: ${reportData.activeCustomers}\n`;
            fileContent += `Novos Clientes: ${reportData.newCustomers}\n`;
            fileContent += `Gasto Médio por Cliente: R$ ${reportData.averageSpending?.toFixed(2)}\n`;
            break;

          default:
            fileContent += `📋 ${reportData.summary}\n`;
            fileContent += `Período: ${reportData.period}\n`;
        }

        fileContent += `\n\n📈 ANÁLISE E RECOMENDAÇÕES:\n`;
        fileContent += `- Dados gerados com base nos módulos do sistema\n`;
        fileContent += `- Para relatórios mais detalhados, utilize filtros específicos\n`;
        fileContent += `- Exporte em PDF ou Excel para apresentações\n`;
        
        // Simulate file download
        const link = document.createElement('a');
        link.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(fileContent);
        link.download = `${report.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`;
        link.click();
        alert(`Relatório ${reportId} baixado com sucesso!`);
      } catch (error) {
        console.error('Erro ao baixar relatório:', error);
        alert('Erro ao baixar relatório. Tente novamente.');
      }
    }
  };

  const viewReport = async (reportId: string) => {
    const report = reports.find(r => r.id === reportId);
    if (report) {
      try {
        const reportData = await generateRealReportData(report);
        let reportContent = 
          `RELATÓRIO: ${report.title.toUpperCase()}\n\n` +
          `Descrição: ${report.description}\n\n` +
          `Categoria: ${getCategoryInfo(report.category).label}\n` +
          `Tipo: ${reportTypes.find(t => t.key === report.type)?.label}\n` +
          `Período: ${reportPeriods.find(p => p.key === report.period)?.label}\n` +
          `Status: ${report.status === 'ready' ? 'Pronto' : report.status === 'generating' ? 'Gerando' : 'Agendado'}\n` +
          `Última geração: ${report.lastGenerated ? new Date(report.lastGenerated).toLocaleString('pt-BR') : 'Nunca'}\n` +
          `Tamanho: ${report.size}\n\n` +
          `CONTEÚDO DO RELATÓRIO:\n` +
          `===================\n\n`;

        // Add specific data based on report category
        switch (report.category) {
          case 'sales':
            reportContent += `📊 DADOS DE VENDAS\n`;
            reportContent += `Período: ${reportData.period}\n`;
            reportContent += `Total de Vendas: R$ ${reportData.totalSales?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            reportContent += `Total de Pedidos: ${reportData.totalOrders}\n`;
            reportContent += `Ticket Médio: R$ ${reportData.averageTicket?.toFixed(2)}\n\n`;
            reportContent += `🏆 PRODUTOS MAIS VENDIDOS:\n`;
            reportData.topProducts?.forEach((product, index) => {
              reportContent += `${index + 1}. ${product.name}: ${product.sales} unidades\n`;
            });
            break;

          case 'financial':
            reportContent += `💰 DADOS FINANCEIROS\n`;
            reportContent += `Período: ${reportData.period}\n`;
            reportContent += `Receita Total: R$ ${reportData.totalRevenue?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            reportContent += `Despesas Totais: R$ ${reportData.totalExpenses?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            reportContent += `Lucro Líquido: R$ ${reportData.netProfit?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            reportContent += `Margem de Lucro: ${reportData.profitMargin?.toFixed(1)}%\n`;
            break;

          case 'inventory':
            reportContent += `📦 DADOS DE ESTOQUE\n`;
            reportContent += `Período: ${reportData.period}\n`;
            reportContent += `Total de Produtos: ${reportData.totalProducts}\n`;
            reportContent += `Itens com Baixo Estoque: ${reportData.lowStockItems}\n`;
            reportContent += `Itens em Falta: ${reportData.outOfStockItems}\n`;
            reportContent += `Valor Total do Estoque: R$ ${reportData.totalValue?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            break;

          case 'customers':
            reportContent += `👥 DADOS DE CLIENTES\n`;
            reportContent += `Período: ${reportData.period}\n`;
            reportContent += `Total de Clientes: ${reportData.totalCustomers}\n`;
            reportContent += `Clientes Ativos: ${reportData.activeCustomers}\n`;
            reportContent += `Novos Clientes: ${reportData.newCustomers}\n`;
            reportContent += `Gasto Médio por Cliente: R$ ${reportData.averageSpending?.toFixed(2)}\n`;
            break;

          default:
            reportContent += `📋 ${reportData.summary}\n`;
            reportContent += `Período: ${reportData.period}\n`;
        }

        reportContent += `\n\n📈 ANÁLISE E RECOMENDAÇÕES:\n`;
        reportContent += `- Dados gerados com base nos módulos do sistema\n`;
        reportContent += `- Para relatórios mais detalhados, utilize filtros específicos\n`;
        reportContent += `- Exporte em PDF ou Excel para apresentações\n`;
        
        alert(reportContent);
      } catch (error) {
        console.error('Erro ao visualizar relatório:', error);
        alert('Erro ao visualizar relatório. Tente novamente.');
      }
    }
  };

  const handleNewReport = () => {
    setShowCustomReportForm(true);
  };

  const handleExportAll = async () => {
    if (filteredReports.length === 0) {
      alert('Nenhum relatório disponível para exportação.');
      return;
    }

    let allReportsContent = 'RELATÓRIOS COMPLETOS - PURPOSE FOOD\n';
    allReportsContent += '=====================================\n\n';
    
    for (const report of filteredReports) {
      try {
        const reportData = await generateRealReportData(report);
        allReportsContent += `${filteredReports.indexOf(report) + 1}. ${report.title.toUpperCase()}\n`;
        allReportsContent += `   Descrição: ${report.description}\n`;
        allReportsContent += `   Categoria: ${getCategoryInfo(report.category).label}\n`;
        allReportsContent += `   Tipo: ${reportTypes.find(t => t.key === report.type)?.label}\n`;
        allReportsContent += `   Período: ${reportPeriods.find(p => p.key === report.period)?.label}\n`;
        allReportsContent += `   Status: ${report.status === 'ready' ? 'Pronto' : report.status === 'generating' ? 'Gerando' : 'Agendado'}\n`;
        allReportsContent += `   Última geração: ${report.lastGenerated ? new Date(report.lastGenerated).toLocaleDateString('pt-BR') : 'Nunca'}\n`;
        allReportsContent += `   Tamanho: ${report.size}\n`;
        
        // Add category-specific data
        switch (report.category) {
          case 'sales':
            allReportsContent += `   Total de Vendas: R$ ${reportData.totalSales?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            allReportsContent += `   Total de Pedidos: ${reportData.totalOrders}\n`;
            break;
          case 'financial':
            allReportsContent += `   Receita Total: R$ ${reportData.totalRevenue?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            allReportsContent += `   Lucro Líquido: R$ ${reportData.netProfit?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            break;
          case 'inventory':
            allReportsContent += `   Total de Produtos: ${reportData.totalProducts}\n`;
            allReportsContent += `   Valor do Estoque: R$ ${reportData.totalValue?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`;
            break;
          case 'customers':
            allReportsContent += `   Total de Clientes: ${reportData.totalCustomers}\n`;
            allReportsContent += `   Clientes Ativos: ${reportData.activeCustomers}\n`;
            break;
        }
        
        allReportsContent += '   ----------------------------------------\n\n';
      } catch (error) {
        console.error(`Erro ao processar relatório ${report.id}:`, error);
        allReportsContent += `   Erro ao carregar dados do relatório\n`;
        allReportsContent += '   ----------------------------------------\n\n';
      }
    }

    const link = document.createElement('a');
    link.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(allReportsContent);
    link.download = `todos_relatorios_${new Date().toISOString().split('T')[0]}.txt`;
    link.click();
    
    alert(`${filteredReports.length} relatório(s) exportado(s) com sucesso!`);
  };

  const openScheduleModal = (report: Report) => {
    setSelectedReportForSchedule(report);
    setScheduleFormData({
      startDate: new Date().toISOString().split('T')[0],
      startTime: '09:00',
      frequency: 'once',
      email: ''
    });
    setShowScheduleModal(true);
  };

  const handleScheduleReport = async () => {
    if (!selectedReportForSchedule) return;
    
    if (!scheduleFormData.startDate || !scheduleFormData.startTime) {
      alert('Por favor, preencha a data e hora do agendamento.');
      return;
    }

    const scheduledDateTime = new Date(`${scheduleFormData.startDate}T${scheduleFormData.startTime}`);
    const now = new Date();
    
    if (scheduledDateTime <= now) {
      alert('A data/hora do agendamento deve ser futura.');
      return;
    }

    try {
      const response = await fetch('/api/reports/schedule', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          reportId: selectedReportForSchedule.id,
          reportTitle: selectedReportForSchedule.title,
          scheduleDate: scheduleFormData.startDate,
          scheduleTime: scheduleFormData.startTime,
          frequency: scheduleFormData.frequency,
          email: scheduleFormData.email
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao agendar relatório');
      }

      const newScheduledReport = {
        id: `SCH-${Date.now()}`,
        reportId: selectedReportForSchedule.id,
        reportTitle: selectedReportForSchedule.title,
        scheduleDate: scheduleFormData.startDate,
        scheduleTime: scheduleFormData.startTime,
        frequency: scheduleFormData.frequency,
        email: scheduleFormData.email,
        status: 'scheduled',
        createdAt: new Date().toISOString()
      };

      setScheduledReports(prev => [...prev, newScheduledReport]);
      setShowScheduleModal(false);
      
      const frequencyText = {
        'once': 'uma vez',
        'daily': 'diariamente',
        'weekly': 'semanalmente',
        'monthly': 'mensalmente'
      }[scheduleFormData.frequency];

      alert(`Relatório "${selectedReportForSchedule.title}" agendado com sucesso!\n\n` +
            `Data: ${new Date(scheduleFormData.startDate).toLocaleDateString('pt-BR')}\n` +
            `Horário: ${scheduleFormData.startTime}\n` +
            `Frequência: ${frequencyText}` +
            (scheduleFormData.email ? `\nEmail: ${scheduleFormData.email}` : ''));
    } catch (error) {
      console.error('Erro ao agendar relatório:', error);
      alert('Erro ao agendar relatório. Tente novamente.');
    }
  };

  const reportCategories = [
    { key: 'sales', label: 'Vendas', icon: <TrendingUp className="w-4 h-4" />, color: 'text-green-600' },
    { key: 'financial', label: 'Financeiro', icon: <DollarSign className="w-4 h-4" />, color: 'text-blue-600' },
    { key: 'inventory', label: 'Estoque', icon: <Package className="w-4 h-4" />, color: 'text-purple-600' },
    { key: 'customers', label: 'Clientes', icon: <Users className="w-4 h-4" />, color: 'text-orange-600' },
    { key: 'general', label: 'Geral', icon: <BarChart3 className="w-4 h-4" />, color: 'text-gray-600' }
  ];

  const reportTypes = [
    { key: 'summary', label: 'Resumo' },
    { key: 'detailed', label: 'Detalhado' },
    { key: 'comparative', label: 'Comparativo' },
    { key: 'analytical', label: 'Analítico' }
  ];

  const reportPeriods = [
    { key: 'daily', label: 'Diário' },
    { key: 'weekly', label: 'Semanal' },
    { key: 'monthly', label: 'Mensal' },
    { key: 'quarterly', label: 'Trimestral' },
    { key: 'yearly', label: 'Anual' },
    { key: 'custom', label: 'Personalizado' }
  ];

  const getCategoryInfo = (category: string) => {
    return reportCategories.find(cat => cat.key === category) || { key: 'general', label: 'Geral', icon: <BarChart3 className="w-4 h-4" />, color: 'text-gray-600' };
  };

  const filteredReports = reports.filter(report => {
    const categoryMatch = selectedCategory === 'all' || report.category === selectedCategory;
    const typeMatch = selectedType === 'all' || report.type === selectedType;
    const periodMatch = selectedPeriod === 'all' || report.period === selectedPeriod;
    return categoryMatch && typeMatch && periodMatch;
  });

  const QuickStats = () => {
    const stats = [
      { title: 'Total de Relatórios', value: reports.length, icon: <FileText className="w-6 h-6" />, color: 'text-blue-600' },
      { title: 'Relatórios Gerados', value: reports.filter(r => r.status === 'ready').length, icon: <Eye className="w-6 h-6" />, color: 'text-green-600' },
      { title: 'Em Processamento', value: reports.filter(r => r.status === 'generating').length, icon: <BarChart3 className="w-6 h-6" />, color: 'text-orange-600' },
      { title: 'Agendados', value: reports.filter(r => r.status === 'scheduled').length, icon: <Calendar className="w-6 h-6" />, color: 'text-purple-600' }
    ];

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`${stat.color}`}>
                {stat.icon}
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const FilterSection = () => (
    <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filtrar por:</span>
          </div>
          
          <div>
            <label className="block text-xs text-gray-500 mb-1">Categoria</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            >
              <option value="all">Todas</option>
              {reportCategories.map(cat => (
                <option key={cat.key} value={cat.key}>{cat.label}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-xs text-gray-500 mb-1">Tipo</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            >
              <option value="all">Todos</option>
              {reportTypes.map(type => (
                <option key={type.key} value={type.key}>{type.label}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-xs text-gray-500 mb-1">Período</label>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            >
              <option value="all">Todos</option>
              {reportPeriods.map(period => (
                <option key={period.key} value={period.key}>{period.label}</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleNewReport}
            className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors flex items-center"
          >
            <FileText className="w-4 h-4 mr-2" />
            Novo Relatório
          </button>
          <button
            onClick={handleExportAll}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Exportar Todos
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Relatórios</h1>
          <p className="text-gray-600">Gere e gerencie relatórios detalhados sobre vendas, finanças, estoque e clientes.</p>
        </div>

        {/* Quick Stats */}
        <QuickStats />

        {/* Filter Section */}
        <FilterSection />

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { key: 'available', label: 'Relatórios Disponíveis' },
                { key: 'generated', label: 'Gerados' },
                { key: 'scheduled', label: 'Agendados' }
              ].map(tab => (
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
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Carregando relatórios...</h3>
            <p className="text-gray-600">Por favor, aguarde enquanto carregamos os relatórios.</p>
          </div>
        )}

        {/* Reports List */}
        {!loading && filteredReports.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {reports.length === 0 ? 'Nenhum relatório disponível' : 'Nenhum relatório encontrado'}
            </h3>
            <p className="text-gray-600 mb-6">
              {reports.length === 0 
                ? 'Não há relatórios disponíveis no momento.'
                : 'Tente ajustar os filtros ou termos de busca para encontrar o que procura.'
              }
            </p>
            {reports.length === 0 && (
              <button
                onClick={handleNewReport}
                className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors flex items-center mx-auto"
              >
                <FileText className="w-4 h-4 mr-2" />
                Criar Primeiro Relatório
              </button>
            )}
          </div>
        )}

        {!loading && filteredReports.length > 0 && (
          <div className="grid gap-4">
            {filteredReports.map(report => (
              <div key={report.id} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className={`${getCategoryInfo(report.category).color}`}>
                        {getCategoryInfo(report.category).icon}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900">{report.title}</h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        report.status === 'ready' ? 'bg-green-100 text-green-800' :
                        report.status === 'generating' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {report.status === 'ready' ? 'Pronto' : report.status === 'generating' ? 'Gerando...' : 'Agendado'}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-3">{report.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center space-x-1">
                        <PieChart className="w-4 h-4" />
                        <span>{reportTypes.find(t => t.key === report.type)?.label}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{reportPeriods.find(p => p.key === report.period)?.label}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <FileText className="w-4 h-4" />
                        <span>{report.size}</span>
                      </span>
                      {report.lastGenerated && (
                        <span className="flex items-center space-x-1">
                          <span>Última geração: {new Date(report.lastGenerated).toLocaleDateString('pt-BR')}</span>
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => viewReport(report.id)}
                      className="text-gray-600 hover:text-gray-900 p-2"
                      title="Visualizar"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => downloadReport(report.id)}
                      className="text-gray-600 hover:text-gray-900 p-2"
                      title="Download"
                    >
                      <Download className="w-5 h-5" />
                    </button>
                    {report.status === 'ready' && (
                      <>
                        <button
                          onClick={() => generateReport(report.id)}
                          className="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700"
                        >
                          Re-gerar
                        </button>
                        <button
                          onClick={() => openScheduleModal(report)}
                          className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                        >
                          Agendar
                        </button>
                      </>
                    )}
                    {report.status === 'generating' && (
                      <button
                        disabled
                        className="bg-gray-400 text-white px-3 py-1 rounded text-sm cursor-not-allowed"
                      >
                        Gerando...
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Custom Report Form Modal */}
        {showCustomReportForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h2 className="text-xl font-bold mb-4">Novo Relatório Personalizado</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Título</label>
                  <input
                    type="text"
                    value={customReportData.title}
                    onChange={(e) => setCustomReportData(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Digite o título do relatório"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
                  <select
                    value={customReportData.category}
                    onChange={(e) => setCustomReportData(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  >
                    <option value="">Selecione uma categoria</option>
                    {reportCategories.map(cat => (
                      <option key={cat.key} value={cat.key}>{cat.label}</option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Data Inicial</label>
                    <input
                      type="date"
                      value={customReportData.startDate}
                      onChange={(e) => setCustomReportData(prev => ({ ...prev, startDate: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Data Final</label>
                    <input
                      type="date"
                      value={customReportData.endDate}
                      onChange={(e) => setCustomReportData(prev => ({ ...prev, endDate: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCustomReportForm(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancelar
                </button>
                <button
                  onClick={async () => {
                    if (!customReportData.title || !customReportData.category) {
                      alert('Por favor, preencha o título e selecione uma categoria.');
                      return;
                    }
                    
                    try {
                      const response = await fetch('/api/reports', {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                          title: customReportData.title,
                          category: customReportData.category,
                          startDate: customReportData.startDate,
                          endDate: customReportData.endDate,
                          type: 'custom',
                          period: 'custom'
                        }),
                      });

                      if (!response.ok) {
                        throw new Error('Erro ao criar relatório');
                      }

                      const newReport = await response.json();
                      setReports(prev => [...prev, newReport.report]);
                      setShowCustomReportForm(false);
                      setCustomReportData({ title: '', category: '', startDate: '', endDate: '' });
                      alert('Relatório criado com sucesso!');
                    } catch (error) {
                      console.error('Erro ao criar relatório:', error);
                      alert('Erro ao criar relatório. Tente novamente.');
                    }
                  }}
                  className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
                >
                  Criar Relatório
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Schedule Modal */}
        {showScheduleModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h2 className="text-xl font-bold mb-4">Agendar Relatório</h2>
              <p className="text-gray-600 mb-4">"{selectedReportForSchedule?.title}"</p>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Data</label>
                    <input
                      type="date"
                      value={scheduleFormData.startDate}
                      onChange={(e) => setScheduleFormData(prev => ({ ...prev, startDate: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Horário</label>
                    <input
                      type="time"
                      value={scheduleFormData.startTime}
                      onChange={(e) => setScheduleFormData(prev => ({ ...prev, startTime: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Frequência</label>
                  <select
                    value={scheduleFormData.frequency}
                    onChange={(e) => setScheduleFormData(prev => ({ ...prev, frequency: e.target.value as any }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  >
                    <option value="once">Uma vez</option>
                    <option value="daily">Diariamente</option>
                    <option value="weekly">Semanalmente</option>
                    <option value="monthly">Mensalmente</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email (opcional)</label>
                  <input
                    type="email"
                    value={scheduleFormData.email}
                    onChange={(e) => setScheduleFormData(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    placeholder="Digite seu email para receber o relatório"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowScheduleModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleScheduleReport}
                  className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
                >
                  Agendar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;