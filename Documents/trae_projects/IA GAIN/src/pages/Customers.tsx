import React, { useState, useEffect } from 'react';
import DataTable from '@/components/ui/DataTable';
import CustomerFormModal from '@/components/ui/CustomerFormModal';
import CustomerGrid from '@/components/ui/CustomerGrid';
import { Plus, Users, Phone, Mail, MapPin, Calendar, Filter, Eye, Edit, Trash2, DollarSign, Search, Grid, List } from 'lucide-react';

interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  cpf: string;
  address: string;
  neighborhood: string;
  city: string;
  state: string;
  zipCode: string;
  birthDate: string;
  registrationDate: string;
  totalOrders: number;
  totalSpent: number;
  lastOrderDate?: string;
  status: 'active' | 'inactive';
  notes?: string;
}

const Customers: React.FC = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch customers from API
  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/customers');
      if (!response.ok) {
        throw new Error('Erro ao buscar clientes');
      }
      
      const data = await response.json();
      setCustomers(data.customers || []);
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      setError('Erro ao carregar clientes. Por favor, tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const formFields = [
    {
      name: 'name',
      label: 'Nome Completo',
      type: 'text' as const,
      required: true,
      placeholder: 'Digite o nome completo'
    },
    {
      name: 'email',
      label: 'E-mail',
      type: 'email' as const,
      required: true,
      placeholder: 'email@exemplo.com'
    },
    {
      name: 'phone',
      label: 'Telefone',
      type: 'text' as const,
      required: true,
      placeholder: '(00) 00000-0000'
    },
    {
      name: 'cpf',
      label: 'CPF',
      type: 'text' as const,
      required: true,
      placeholder: '000.000.000-00'
    },
    {
      name: 'address',
      label: 'Endereço',
      type: 'text' as const,
      required: true,
      placeholder: 'Rua, número'
    },
    {
      name: 'neighborhood',
      label: 'Bairro',
      type: 'text' as const,
      required: true,
      placeholder: 'Nome do bairro'
    },
    {
      name: 'city',
      label: 'Cidade',
      type: 'text' as const,
      required: true,
      placeholder: 'Nome da cidade'
    },
    {
      name: 'state',
      label: 'Estado',
      type: 'select' as const,
      required: true,
      options: [
        { value: 'SP', label: 'São Paulo' },
        { value: 'RJ', label: 'Rio de Janeiro' },
        { value: 'MG', label: 'Minas Gerais' },
        { value: 'ES', label: 'Espírito Santo' },
        { value: 'PR', label: 'Paraná' },
        { value: 'SC', label: 'Santa Catarina' },
        { value: 'RS', label: 'Rio Grande do Sul' },
        { value: 'DF', label: 'Distrito Federal' },
        { value: 'GO', label: 'Goiás' },
        { value: 'MS', label: 'Mato Grosso do Sul' }
      ]
    },
    {
      name: 'zipCode',
      label: 'CEP',
      type: 'text' as const,
      required: true,
      placeholder: '00000-000'
    },
    {
      name: 'birthDate',
      label: 'Data de Nascimento',
      type: 'date' as const,
      required: false
    },
    {
      name: 'status',
      label: 'Status',
      type: 'select' as const,
      required: true,
      options: [
        { value: 'active', label: 'Ativo' },
        { value: 'inactive', label: 'Inativo' }
      ]
    },
    {
      name: 'notes',
      label: 'Observações',
      type: 'textarea' as const,
      placeholder: 'Observações sobre o cliente (opcional)'
    }
  ];

  const handleSubmit = async (data: any, action: 'save-exit' | 'save-new') => {
    try {
      setError(null);
      
      if (editingCustomer) {
        // Update existing customer
        const response = await fetch(`/api/customers/${editingCustomer.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erro ao atualizar cliente');
        }

        const result = await response.json();
        
        // Update local state
        setCustomers(customers.map(c => 
          c.id === editingCustomer.id ? result.customer : c
        ));

        if (action === 'save-exit') {
          setIsFormOpen(false);
          setEditingCustomer(null);
        } else {
          // Reset form for new customer
          setEditingCustomer(null);
        }
      } else {
        // Create new customer
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
        
        // Add to local state
        setCustomers([...customers, result.customer]);

        if (action === 'save-exit') {
          setIsFormOpen(false);
        }
        // Reset form for 'save-new'
        setEditingCustomer(null);
      }
    } catch (error) {
      console.error('Erro ao salvar cliente:', error);
      setError(error instanceof Error ? error.message : 'Erro ao salvar cliente');
      alert(`Erro ao salvar cliente: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    }
  };

  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setIsFormOpen(true);
  };

  const handleDelete = async (customer: Customer) => {
    if (confirm(`Deseja realmente excluir o cliente ${customer.name}?\n\nAtenção: Esta ação não pode ser desfeita.`)) {
      try {
        const response = await fetch(`/api/customers/${customer.id}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erro ao excluir cliente');
        }

        // Remove from local state
        setCustomers(customers.filter(c => c.id !== customer.id));
        
        alert('Cliente excluído com sucesso!');
      } catch (error) {
        console.error('Erro ao excluir cliente:', error);
        alert(`Erro ao excluir cliente: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
      }
    }
  };

  const [showFilters, setShowFilters] = useState(false);
  const [filterCity, setFilterCity] = useState<string>('');
  const [filterState, setFilterState] = useState<string>('');
  const [filterMinOrders, setFilterMinOrders] = useState<string>('');
  const [filterMaxOrders, setFilterMaxOrders] = useState<string>('');
  const [filterMinSpent, setFilterMinSpent] = useState<string>('');
  const [filterMaxSpent, setFilterMaxSpent] = useState<string>('');

  const filteredCustomers = customers.filter(c => {
    const matchesStatus = filterStatus === 'all' || c.status === filterStatus;
    const matchesSearch = searchTerm === '' || 
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.phone.includes(searchTerm) ||
      c.cpf.includes(searchTerm);
    
    const matchesCity = !filterCity || c.city.toLowerCase().includes(filterCity.toLowerCase());
    const matchesState = !filterState || c.state === filterState;
    const matchesMinOrders = !filterMinOrders || c.totalOrders >= parseInt(filterMinOrders);
    const matchesMaxOrders = !filterMaxOrders || c.totalOrders <= parseInt(filterMaxOrders);
    const matchesMinSpent = !filterMinSpent || c.totalSpent >= parseFloat(filterMinSpent);
    const matchesMaxSpent = !filterMaxSpent || c.totalSpent <= parseFloat(filterMaxSpent);
    
    return matchesStatus && matchesSearch && matchesCity && matchesState && matchesMinOrders && matchesMaxOrders && matchesMinSpent && matchesMaxSpent;
  });

  const columns = [
    {
      key: 'id',
      header: 'Código',
      sortable: true
    },
    {
      key: 'name',
      header: 'Nome',
      sortable: true
    },
    {
      key: 'email',
      header: 'E-mail',
      sortable: true
    },
    {
      key: 'phone',
      header: 'Telefone',
      sortable: true
    },
    {
      key: 'totalOrders',
      header: 'Pedidos',
      sortable: true,
      render: (value: number) => (
        <span className="font-medium">{value}</span>
      )
    },
    {
      key: 'totalSpent',
      header: 'Total Gasto',
      sortable: true,
      render: (value: number) => (
        <span className="font-medium text-green-600">R$ {value.toFixed(2)}</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'active' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {value === 'active' ? 'Ativo' : 'Inativo'}
        </span>
      )
    },
    {
      key: 'lastOrderDate',
      header: 'Último Pedido',
      sortable: true,
      render: (value?: string) => value ? new Date(value).toLocaleDateString('pt-BR') : 'Nunca'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando clientes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-500 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Erro ao carregar clientes</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchCustomers}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Clientes</h1>
          <p className="text-gray-600 mt-1">Controle completo do seu cadastro de clientes</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchCustomers}
            className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center"
            title="Atualizar lista"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            onClick={() => {
              setEditingCustomer(null);
              setIsFormOpen(true);
            }}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Novo Cliente
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total de Clientes</p>
              <p className="text-2xl font-bold text-gray-900">{customers.length}</p>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Clientes Ativos</p>
              <p className="text-2xl font-bold text-green-600">{customers.filter(c => c.status === 'active').length}</p>
            </div>
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 font-bold text-sm">✓</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Ticket Médio</p>
              <p className="text-2xl font-bold text-purple-600">
                R$ {customers.length > 0 ? 
                  (customers.reduce((sum, c) => sum + c.totalSpent, 0) / Math.max(customers.reduce((sum, c) => sum + c.totalOrders, 0), 1) || 0).toFixed(2) 
                  : '0.00'
                }
              </p>
            </div>
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <span className="text-purple-600 font-bold text-sm">$</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Faturamento Total</p>
              <p className="text-2xl font-bold text-orange-600">
                R$ {customers.reduce((sum, c) => sum + c.totalSpent, 0).toFixed(2)}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filtrar por status:</span>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                <option value="all">Todos os clientes</option>
                <option value="active">Ativos</option>
                <option value="inactive">Inativos</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Buscar cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 w-64"
              />
            </div>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-2 px-3 py-1 text-sm rounded-lg border ${showFilters ? 'bg-orange-100 border-orange-300 text-orange-700' : 'border-gray-300 text-gray-700 hover:bg-gray-50'}`}
            >
              <Filter className="w-4 h-4" />
              <span>Filtros Avançados</span>
            </button>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">{filteredCustomers.length} cliente(s)</span>
            <div className="flex border border-gray-300 rounded-lg">
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-1 text-sm rounded-l-lg ${viewMode === 'list' ? 'bg-orange-500 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-1 text-sm rounded-r-lg ${viewMode === 'grid' ? 'bg-orange-500 text-white' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Cidade</label>
                <input
                  type="text"
                  placeholder="Filtrar por cidade..."
                  value={filterCity}
                  onChange={(e) => setFilterCity(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                <select
                  value={filterState}
                  onChange={(e) => setFilterState(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">Todos os estados</option>
                  <option value="SP">São Paulo</option>
                  <option value="RJ">Rio de Janeiro</option>
                  <option value="MG">Minas Gerais</option>
                  <option value="ES">Espírito Santo</option>
                  <option value="PR">Paraná</option>
                  <option value="SC">Santa Catarina</option>
                  <option value="RS">Rio Grande do Sul</option>
                  <option value="DF">Distrito Federal</option>
                  <option value="GO">Goiás</option>
                  <option value="MS">Mato Grosso do Sul</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pedidos</label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    placeholder="Mín."
                    value={filterMinOrders}
                    onChange={(e) => setFilterMinOrders(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                  <input
                    type="number"
                    placeholder="Máx."
                    value={filterMaxOrders}
                    onChange={(e) => setFilterMaxOrders(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Gasto Total (R$)</label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    placeholder="Mín."
                    step="0.01"
                    value={filterMinSpent}
                    onChange={(e) => setFilterMinSpent(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                  <input
                    type="number"
                    placeholder="Máx."
                    step="0.01"
                    value={filterMaxSpent}
                    onChange={(e) => setFilterMaxSpent(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  />
                </div>
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => {
                    setFilterCity('');
                    setFilterState('');
                    setFilterMinOrders('');
                    setFilterMaxOrders('');
                    setFilterMinSpent('');
                    setFilterMaxSpent('');
                  }}
                  className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
                >
                  Limpar Filtros
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Data Display */}
      {filteredCustomers.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
          <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {customers.length === 0 ? 'Nenhum cliente cadastrado' : 'Nenhum cliente encontrado'}
          </h3>
          <p className="text-gray-600 mb-6">
            {customers.length === 0 
              ? 'Comece cadastrando seu primeiro cliente para gerenciar seu negócio.'
              : 'Tente ajustar os filtros ou termos de busca para encontrar o que procura.'
            }
          </p>
          {customers.length === 0 && (
            <button
              onClick={() => {
                setEditingCustomer(null);
                setIsFormOpen(true);
              }}
              className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors flex items-center mx-auto"
            >
              <Plus className="w-4 h-4 mr-2" />
              Cadastrar Primeiro Cliente
            </button>
          )}
        </div>
      ) : viewMode === 'grid' ? (
        <CustomerGrid
          customers={filteredCustomers}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={(customer) => {
            alert(`Detalhes do Cliente:\n\nCódigo: ${customer.id}\nNome: ${customer.name}\nE-mail: ${customer.email}\nTelefone: ${customer.phone}\nCPF: ${customer.cpf}\n\nEndereço:\n${customer.address}\n${customer.neighborhood} - ${customer.city}/${customer.state}\nCEP: ${customer.zipCode}\n\nData de Nascimento: ${customer.birthDate ? new Date(customer.birthDate).toLocaleDateString('pt-BR') : 'Não informada'}\nData de Cadastro: ${new Date(customer.registrationDate).toLocaleDateString('pt-BR')}\n\nEstatísticas:\nTotal de Pedidos: ${customer.totalOrders}\nTotal Gasto: R$ ${customer.totalSpent.toFixed(2)}\nÚltimo Pedido: ${customer.lastOrderDate ? new Date(customer.lastOrderDate).toLocaleDateString('pt-BR') : 'Nunca'}\n\nObservações: ${customer.notes || 'Nenhuma'}`);
          }}
        />
      ) : (
        <DataTable
          columns={columns}
          data={filteredCustomers}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={(customer) => {
            alert(`Detalhes do Cliente:\n\nCódigo: ${customer.id}\nNome: ${customer.name}\nE-mail: ${customer.email}\nTelefone: ${customer.phone}\nCPF: ${customer.cpf}\n\nEndereço:\n${customer.address}\n${customer.neighborhood} - ${customer.city}/${customer.state}\nCEP: ${customer.zipCode}\n\nData de Nascimento: ${customer.birthDate ? new Date(customer.birthDate).toLocaleDateString('pt-BR') : 'Não informada'}\nData de Cadastro: ${new Date(customer.registrationDate).toLocaleDateString('pt-BR')}\n\nEstatísticas:\nTotal de Pedidos: ${customer.totalOrders}\nTotal Gasto: R$ ${customer.totalSpent.toFixed(2)}\nÚltimo Pedido: ${customer.lastOrderDate ? new Date(customer.lastOrderDate).toLocaleDateString('pt-BR') : 'Nunca'}\n\nObservações: ${customer.notes || 'Nenhuma'}`);
          }}
          showSearch={false}
          showFilters={false}
        />
      )}

      {/* Form Modal */}
      <CustomerFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingCustomer(null);
        }}
        onSubmit={handleSubmit}
        title={editingCustomer ? 'Editar Cliente' : 'Novo Cliente'}
        fields={formFields}
        initialData={editingCustomer || {}}
      />
    </div>
  );
};

export default Customers;