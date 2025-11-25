import React, { useState, useEffect } from 'react';
import { FileText, Download, Send, Plus, Search, Calendar, DollarSign, User, Building, Tag, Barcode, CheckCircle, XCircle, Clock } from 'lucide-react';
import DataTable from '../components/ui/DataTable';
import FormModal, { FormField } from '../components/ui/FormModal';
import MetricCard from '../components/ui/MetricCard';

interface Invoice {
  id: string;
  number: string;
  series: string;
  customer: {
    name: string;
    cpfCnpj: string;
    email: string;
    address: string;
  };
  items: InvoiceItem[];
  totalAmount: number;
  taxAmount: number;
  netAmount: number;
  status: 'draft' | 'issued' | 'cancelled' | 'paid';
  issueDate: string;
  dueDate: string;
  paymentMethod: string;
  notes?: string;
  xmlUrl?: string;
  pdfUrl?: string;
}

interface InvoiceItem {
  id: string;
  description: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  ncmCode: string;
  cfopCode: string;
  icmsRate: number;
  ipiRate: number;
}

interface Customer {
  id: string;
  name: string;
  cpfCnpj: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
}

export function Invoices() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [showInvoiceModal, setShowInvoiceModal] = useState(false);
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState<string>('all');

  // Fetch real data from API
  useEffect(() => {
    fetchInvoices();
    fetchCustomers();
  }, []);

  const fetchInvoices = async () => {
    try {
      const response = await fetch('/api/invoices');
      if (!response.ok) {
        throw new Error('Erro ao buscar notas fiscais');
      }
      
      const data = await response.json();
      setInvoices(data.invoices || []);
    } catch (error) {
      console.error('Erro ao buscar notas fiscais:', error);
      alert('Erro ao carregar notas fiscais');
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await fetch('/api/customers');
      if (!response.ok) {
        throw new Error('Erro ao buscar clientes');
      }
      
      const data = await response.json();
      setCustomers(data.customers || []);
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      alert('Erro ao carregar clientes');
    }
  };

  const statusIcons = {
    draft: <Clock className="w-4 h-4 text-gray-500" />,
    issued: <CheckCircle className="w-4 h-4 text-green-500" />,
    cancelled: <XCircle className="w-4 h-4 text-red-500" />,
    paid: <CheckCircle className="w-4 h-4 text-blue-500" />,
    pending: <Clock className="w-4 h-4 text-orange-500" />
  };

  const statusColors = {
    draft: 'bg-gray-100 text-gray-800',
    issued: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    paid: 'bg-blue-100 text-blue-800',
    pending: 'bg-orange-100 text-orange-800'
  };

  const statusLabels = {
    draft: 'Rascunho',
    issued: 'Emitida',
    cancelled: 'Cancelada',
    paid: 'Paga',
    pending: 'Pendente'
  };

  const invoiceFormFields: FormField[] = [
    {
      name: 'customerId',
      label: 'Cliente',
      type: 'select',
      required: true,
      options: customers.map(c => ({ value: c.id, label: `${c.name} - ${c.cpfCnpj}` }))
    },
    {
      name: 'series',
      label: 'Série',
      type: 'text',
      required: true
    },
    {
      name: 'dueDate',
      label: 'Data de Vencimento',
      type: 'date',
      required: true
    },
    {
      name: 'paymentMethod',
      label: 'Forma de Pagamento',
      type: 'select',
      required: true,
      options: [
        { value: 'Boleto Bancário', label: 'Boleto Bancário' },
        { value: 'PIX', label: 'PIX' },
        { value: 'Cartão de Crédito', label: 'Cartão de Crédito' },
        { value: 'Cartão de Débito', label: 'Cartão de Débito' }
      ]
    },
    {
      name: 'notes',
      label: 'Observações',
      type: 'textarea'
    }
  ];

  const customerFormFields: FormField[] = [
    {
      name: 'name',
      label: 'Nome/Razão Social',
      type: 'text',
      required: true
    },
    {
      name: 'cpfCnpj',
      label: 'CPF/CNPJ',
      type: 'text',
      required: true
    },
    {
      name: 'email',
      label: 'Email',
      type: 'email',
      required: true
    },
    {
      name: 'phone',
      label: 'Telefone',
      type: 'tel'
    },
    {
      name: 'address',
      label: 'Endereço',
      type: 'text',
      required: true
    },
    {
      name: 'city',
      label: 'Cidade',
      type: 'text',
      required: true
    },
    {
      name: 'state',
      label: 'Estado',
      type: 'text',
      required: true
    },
    {
      name: 'zipCode',
      label: 'CEP',
      type: 'text',
      required: true
    }
  ];

  const handleCreateInvoice = async (data: any) => {
    try {
      const customer = customers.find(c => c.id === data.customerId);
      if (!customer) {
        alert('Cliente não encontrado');
        return;
      }

      const response = await fetch('/api/invoices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customerId: data.customerId,
          series: data.series,
          totalAmount: 0, // Will be calculated when items are added
          taxAmount: 0,
          status: 'draft',
          issueDate: new Date().toISOString().split('T')[0],
          dueDate: data.dueDate,
          paymentMethod: data.paymentMethod,
          notes: data.notes
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao criar nota fiscal');
      }

      const result = await response.json();
      
      setInvoices([result.invoice, ...invoices]);
      setShowInvoiceModal(false);
      alert('Nota fiscal criada com sucesso!');
    } catch (error) {
      console.error('Erro ao criar nota fiscal:', error);
      alert(`Erro ao criar nota fiscal: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    }
  };

  const handleCreateCustomer = async (data: any) => {
    try {
      const response = await fetch('/api/customers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao criar cliente');
      }

      const result = await response.json();
      
      // Add the new customer to the list
      setCustomers([result.customer, ...customers]);
      setShowCustomerModal(false);
      alert('Cliente criado com sucesso!');
    } catch (error) {
      console.error('Erro ao criar cliente:', error);
      alert(`Erro ao criar cliente: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    }
  };

  const filteredInvoices = invoices.filter(invoice => {
    const statusMatch = selectedStatus === 'all' || invoice.status === selectedStatus;
    const searchMatch = searchTerm === '' || 
      invoice.customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      invoice.number.includes(searchTerm) ||
      invoice.customer.cpfCnpj.includes(searchTerm);
    return statusMatch && searchMatch;
  });

  const totalIssued = invoices.filter(i => i.status === 'issued').reduce((sum, i) => sum + i.totalAmount, 0);
  const totalPaid = invoices.filter(i => i.status === 'paid').reduce((sum, i) => sum + i.totalAmount, 0);
  const totalCancelled = invoices.filter(i => i.status === 'cancelled').reduce((sum, i) => sum + i.totalAmount, 0);
  const pendingInvoices = invoices.filter(i => i.status === 'issued').length;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Notas Fiscais</h1>
          <p className="text-gray-600">Gerencie a emissão e controle de notas fiscais eletrônicas</p>
        </div>

        {/* Métricas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Emitido"
            value={`R$ ${totalIssued.toFixed(2)}`}
            icon={<FileText className="w-6 h-6" />}
            color="blue"
          />
          <MetricCard
            title="Total Pago"
            value={`R$ ${totalPaid.toFixed(2)}`}
            icon={<DollarSign className="w-6 h-6" />}
            color="green"
          />
          <MetricCard
            title="Total Cancelado"
            value={`R$ ${totalCancelled.toFixed(2)}`}
            icon={<XCircle className="w-6 h-6" />}
            color="red"
          />
          <MetricCard
            title="Pendentes"
            value={pendingInvoices.toString()}
            icon={<Clock className="w-6 h-6" />}
            color="orange"
          />
        </div>

        {/* Ações e Filtros */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex gap-2">
            <button
              onClick={() => setShowInvoiceModal(true)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nova Nota
            </button>
            <button
              onClick={() => setShowCustomerModal(true)}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 flex items-center"
            >
              <User className="w-4 h-4 mr-2" />
              Novo Cliente
            </button>
            <button
              onClick={() => {
                fetchInvoices();
                fetchCustomers();
              }}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 flex items-center"
              title="Atualizar dados"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
          <div className="flex gap-2 flex-1">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar notas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Todos Status</option>
              <option value="pending">Pendente</option>
              <option value="draft">Rascunho</option>
              <option value="issued">Emitida</option>
              <option value="paid">Paga</option>
              <option value="cancelled">Cancelada</option>
            </select>
          </div>
        </div>

        {/* Lista de Notas Fiscais */}
        {filteredInvoices.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {invoices.length === 0 ? 'Nenhuma nota fiscal cadastrada' : 'Nenhuma nota fiscal encontrada'}
            </h3>
            <p className="text-gray-600 mb-6">
              {invoices.length === 0 
                ? 'Comece criando sua primeira nota fiscal para gerenciar suas vendas.'
                : 'Tente ajustar os filtros ou termos de busca para encontrar o que procura.'
              }
            </p>
            {invoices.length === 0 && (
              <button
                onClick={() => setShowInvoiceModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center mx-auto"
              >
                <Plus className="w-4 h-4 mr-2" />
                Criar Primeira Nota
              </button>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Número
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CPF/CNPJ
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data Emissão
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vencimento
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredInvoices.map(invoice => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {invoice.series}/{invoice.number}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {invoice.customer.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {invoice.customer.email}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {invoice.customer.cpfCnpj}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          R$ {invoice.totalAmount.toFixed(2)}
                        </div>
                        <div className="text-sm text-gray-500">
                          Imposto: R$ {invoice.taxAmount.toFixed(2)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[invoice.status]}`}>
                          {statusIcons[invoice.status]}
                          <span className="ml-1">{statusLabels[invoice.status]}</span>
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(invoice.issueDate).toLocaleDateString('pt-BR')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(invoice.dueDate).toLocaleDateString('pt-BR')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          {invoice.xmlUrl && (
                            <button className="text-blue-600 hover:text-blue-900">
                              <Download className="w-4 h-4" />
                            </button>
                          )}
                          {invoice.pdfUrl && (
                            <button className="text-green-600 hover:text-green-900">
                              <FileText className="w-4 h-4" />
                            </button>
                          )}
                          <button className="text-purple-600 hover:text-purple-900">
                            <Send className="w-4 h-4" />
                          </button>
                          {(invoice.status === 'draft') && (
                            <button className="text-orange-600 hover:text-orange-900">
                              <Tag className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Modais */}
        <FormModal
          isOpen={showInvoiceModal}
          onClose={() => setShowInvoiceModal(false)}
          title="Criar Nota Fiscal"
          fields={invoiceFormFields}
          onSubmit={handleCreateInvoice}
        />

        <FormModal
          isOpen={showCustomerModal}
          onClose={() => setShowCustomerModal(false)}
          title="Cadastrar Cliente"
          fields={customerFormFields}
          onSubmit={handleCreateCustomer}
        />
      </div>
    </div>
  );
}