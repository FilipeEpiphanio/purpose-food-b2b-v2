import React, { useState, useEffect } from 'react';
import { ShoppingCart, Plus, Minus, Trash2, CreditCard, Smartphone, DollarSign, Search, User, Phone, Mail, MapPin, X } from 'lucide-react';
import DataTable from '../components/ui/DataTable';
import FormModal from '../components/ui/FormModal';
import MetricCard from '../components/ui/MetricCard';

interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  stock: number;
  image?: string;
}

interface CartItem {
  product: Product;
  quantity: number;
}

interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  cpf: string;
}

interface PaymentMethod {
  id: string;
  name: string;
  type: 'credit_card' | 'debit_card' | 'pix' | 'cash';
  icon: React.ReactNode;
}

export function Sales() {
  const [activeTab, setActiveTab] = useState<'products' | 'cart' | 'payment'>('products');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showCustomerModal, setShowCustomerModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [loadingCustomers, setLoadingCustomers] = useState(false);

  // Função para obter imagem do produto
  const getProductImage = (product: Product) => {
    if (product.image) return product.image;
    
    // Imagens padrão por categoria
    const categoryImages = {
      'salgados': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Coxinha%20de%20frango%20tradicional%2C%20pastel%20de%20carne%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'bolos': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Bolo%20de%20chocolate%20com%20cobertura%20de%20brigadeiro%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'tortas': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Torta%20de%20morango%20com%20creme%20de%20baunilha%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'brigadeiros': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Brigadeiros%20gourmet%20artesanais%20com%20chocolate%20belga%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'pães': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=P%C3%A3o%20de%20queijo%20mineiro%20tradicional%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'doces': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Doces%20gourmet%20artesanais%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'bebidas': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Bebidas%20naturais%2C%20sucos%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square'
    };
    
    const categoryKey = product.category.toLowerCase();
    return categoryImages[categoryKey] || categoryImages['salgados'];
  };

  const categories = ['all', 'Salgados', 'Doces'];

  const paymentMethods: PaymentMethod[] = [
    { id: 'credit_card', name: 'Cartão de Crédito', type: 'credit_card', icon: <CreditCard className="w-5 h-5" /> },
    { id: 'debit_card', name: 'Cartão de Débito', type: 'debit_card', icon: <CreditCard className="w-5 h-5" /> },
    { id: 'pix', name: 'PIX', type: 'pix', icon: <Smartphone className="w-5 h-5" /> },
    { id: 'cash', name: 'Dinheiro', type: 'cash', icon: <DollarSign className="w-5 h-5" /> }
  ];

  // Buscar produtos reais do banco de dados
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoadingProducts(true);
        const response = await fetch('/api/products');
        if (!response.ok) {
          throw new Error('Erro ao buscar produtos');
        }
        const data = await response.json();
        setProducts(data.products || []);
      } catch (error) {
        console.error('Erro ao buscar produtos:', error);
        // Fallback para dados mockados se a API falhar
        setProducts([
          { id: '1', name: 'Coxinha de Frango', price: 8.50, category: 'Salgados', stock: 50 },
          { id: '2', name: 'Pastel de Carne', price: 12.00, category: 'Salgados', stock: 30 },
          { id: '3', name: 'Brigadeiro Gourmet', price: 6.00, category: 'Doces', stock: 100 }
        ]);
      } finally {
        setLoadingProducts(false);
      }
    };

    fetchProducts();
  }, []);

  // Buscar clientes reais do banco de dados
  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoadingCustomers(true);
        const response = await fetch('/api/customers');
        if (!response.ok) {
          throw new Error('Erro ao buscar clientes');
        }
        const data = await response.json();
        setCustomers(data.customers || []);
      } catch (error) {
        console.error('Erro ao buscar clientes:', error);
        // Fallback para dados mockados se a API falhar
        setCustomers([
          { id: '1', name: 'João Silva', email: 'joao@email.com', phone: '(11) 98765-4321', address: 'Rua A, 123', cpf: '123.456.789-00' },
          { id: '2', name: 'Maria Santos', email: 'maria@email.com', phone: '(11) 99876-5432', address: 'Rua B, 456', cpf: '987.654.321-00' }
        ]);
      } finally {
        setLoadingCustomers(false);
      }
    };

    fetchCustomers();
  }, []);

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Adicionar indicadores de loading na UI
  if (loadingProducts) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando produtos...</p>
        </div>
      </div>
    );
  }

  const addToCart = (product: Product) => {
    setCart(prev => {
      const existingItem = prev.find(item => item.product.id === product.id);
      if (existingItem) {
        return prev.map(item =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { product, quantity: 1 }];
    });
  };

  const updateQuantity = (productId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart(prev =>
      prev.map(item =>
        item.product.id === productId
          ? { ...item, quantity }
          : item
      )
    );
  };

  const removeFromCart = (productId: string) => {
    setCart(prev => prev.filter(item => item.product.id !== productId));
  };

  const getTotalValue = () => {
    return cart.reduce((total, item) => total + (item.product.price * item.quantity), 0);
  };

  const getTotalItems = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  const handlePayment = async () => {
    if (!selectedCustomer || !paymentMethod) {
      alert('Por favor, selecione o cliente e o método de pagamento');
      return;
    }

    setLoading(true);
    
    try {
      // Preparar dados do pedido
      const orderData = {
        customerId: selectedCustomer.id,
        items: cart.map(item => ({
          id: item.product.id,
          name: item.product.name,
          price: item.product.price,
          quantity: item.quantity,
          category: item.product.category
        })),
        totalAmount: getTotalValue(),
        paymentMethod: paymentMethod
      };

      console.log('Enviando dados do pedido:', orderData);

      // Criar cliente no Stripe se necessário (ou usar cliente existente)
      let customerResponse = null;
      if (selectedCustomer) {
        const createCustomerResponse = await fetch('/api/sales/create-customer', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: selectedCustomer.email,
            name: selectedCustomer.name,
            phone: selectedCustomer.phone,
            cpf: selectedCustomer.cpf,
            address: selectedCustomer.address
          })
        });

        if (!createCustomerResponse.ok) {
          throw new Error('Erro ao criar cliente');
        }

        customerResponse = await createCustomerResponse.json();
      }

      // Processar pagamento baseado no método escolhido
      let paymentResponse;
      
      if (paymentMethod === 'pix') {
        // Processar PIX
        const pixResponse = await fetch('/api/sales/process-pix', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            items: orderData.items,
            customerId: customerResponse?.customer?.stripeCustomer?.id || selectedCustomer.id,
            totalAmount: orderData.totalAmount
          })
        });

        if (!pixResponse.ok) {
          throw new Error('Erro ao processar PIX');
        }

        paymentResponse = await pixResponse.json();
      } else {
        // Processar cartão de crédito/débito
        const paymentIntentResponse = await fetch('/api/sales/create-payment-intent', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            items: orderData.items,
            customerId: customerResponse?.customer?.stripeCustomer?.id || selectedCustomer.id,
            paymentMethodId: paymentMethod,
            totalAmount: orderData.totalAmount
          })
        });

        if (!paymentIntentResponse.ok) {
          throw new Error('Erro ao processar pagamento');
        }

        paymentResponse = await paymentIntentResponse.json();
      }

      console.log('Resposta do pagamento:', paymentResponse);

      // Criar transação financeira
      try {
        const financialTransaction = await fetch('/api/financial/transactions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'income',
            category: 'sales',
            description: `Venda - ${cart.map(item => item.product.name).join(', ')}`,
            amount: getTotalValue(),
            payment_method: paymentMethod,
            transaction_date: new Date().toISOString().split('T')[0],
            order_id: paymentResponse.order?.id
          })
        });

        if (!financialTransaction.ok) {
          console.warn('Aviso: Transação financeira não foi criada, mas o pedido foi processado');
        }
      } catch (financialError) {
        console.warn('Erro ao criar transação financeira:', financialError);
      }

      alert('Pagamento processado com sucesso!');
      setCart([]);
      setActiveTab('products');
      setSelectedCustomer(null);
      setPaymentMethod('');
      
      // Recarregar dashboard para atualizar métricas
      window.dispatchEvent(new CustomEvent('saleCompleted'));

    } catch (error) {
      console.error('Erro ao processar pagamento:', error);
      alert(`Erro ao processar pagamento: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const customerFormFields = [
    { name: 'name', label: 'Nome', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'phone', label: 'Telefone', type: 'tel', required: true },
    { name: 'cpf', label: 'CPF', type: 'text', required: true },
    { name: 'address', label: 'Endereço', type: 'textarea', required: true }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Vendas</h1>
          <p className="text-gray-600">Gerencie suas vendas e processamento de pedidos</p>
        </div>

        {/* Métricas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total do Carrinho"
            value={`R$ ${getTotalValue().toFixed(2)}`}
            icon={<ShoppingCart className="w-6 h-6" />}
            color="orange"
          />
          <MetricCard
            title="Itens no Carrinho"
            value={getTotalItems().toString()}
            icon={<Plus className="w-6 h-6" />}
            color="blue"
          />
          <MetricCard
            title="Cliente Selecionado"
            value={selectedCustomer ? selectedCustomer.name : 'Nenhum'}
            icon={<User className="w-6 h-6" />}
            color="green"
          />
          <MetricCard
            title="Método de Pagamento"
            value={paymentMethods.find(p => p.id === paymentMethod)?.name || 'Nenhum'}
            icon={<CreditCard className="w-6 h-6" />}
            color="purple"
          />
        </div>

        {/* Abas de Navegação */}
        <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('products')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === 'products'
                ? 'bg-white text-orange-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Produtos
          </button>
          <button
            onClick={() => setActiveTab('cart')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors relative ${
              activeTab === 'cart'
                ? 'bg-white text-orange-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Carrinho
            {getTotalItems() > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {getTotalItems()}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('payment')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === 'payment'
                ? 'bg-white text-orange-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
            disabled={cart.length === 0}
          >
            Pagamento
          </button>
        </div>

        {/* Conteúdo das Abas */}
        {activeTab === 'products' && (
          <div>
            {/* Filtros */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar produtos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                />
              </div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'Todas Categorias' : category}
                  </option>
                ))}
              </select>
            </div>

            {/* Grade de Produtos */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredProducts.map(product => (
                <div key={product.id} className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
                  <div className="w-full h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
                    <img
                      src={getProductImage(product)}
                      alt={product.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Produto%20aliment%C3%ADcio%20gourmet%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita&image_size=square';
                      }}
                    />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{product.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{product.category}</p>
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-lg font-bold text-orange-600">R$ {product.price.toFixed(2)}</span>
                    <span className="text-sm text-gray-500">Estoque: {product.stock}</span>
                  </div>
                  <button
                    onClick={() => addToCart(product)}
                    disabled={product.stock === 0}
                    className="w-full bg-orange-600 text-white py-2 px-4 rounded-lg hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    {product.stock === 0 ? 'Sem Estoque' : 'Adicionar'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'cart' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            {cart.length === 0 ? (
              <div className="text-center py-12">
                <ShoppingCart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Carrinho vazio</h3>
                <p className="text-gray-600">Adicione produtos ao carrinho para continuar</p>
              </div>
            ) : (
              <div>
                <h2 className="text-xl font-semibold mb-6">Itens do Carrinho</h2>
                <div className="space-y-4">
                  {cart.map(item => (
                    <div key={item.product.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{item.product.name}</h4>
                        <p className="text-sm text-gray-600">{item.product.category}</p>
                        <p className="text-orange-600 font-semibold">R$ {item.product.price.toFixed(2)}</p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                          className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 flex items-center justify-center"
                        >
                          <Minus className="w-4 h-4" />
                        </button>
                        <span className="w-8 text-center font-medium">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                          className="w-8 h-8 rounded-full bg-orange-600 hover:bg-orange-700 text-white flex items-center justify-center"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => removeFromCart(item.product.id)}
                          className="ml-4 text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="flex justify-between items-center text-xl font-bold">
                    <span>Total:</span>
                    <span className="text-orange-600">R$ {getTotalValue().toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'payment' && (
          <div className="space-y-6">
            {/* Seleção de Cliente */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Cliente</h2>
              {selectedCustomer ? (
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium text-gray-900">{selectedCustomer.name}</h3>
                    <p className="text-sm text-gray-600">{selectedCustomer.email}</p>
                    <p className="text-sm text-gray-600">{selectedCustomer.phone}</p>
                  </div>
                  <button
                    onClick={() => setSelectedCustomer(null)}
                    className="text-red-500 hover:text-red-700"
                  >
                    Alterar
                  </button>
                </div>
              ) : (
                <div className="text-center py-8">
                  <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">Selecione um cliente para continuar</p>
                  <button
                    onClick={() => setShowCustomerModal(true)}
                    className="bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700"
                  >
                    Selecionar Cliente
                  </button>
                </div>
              )}
            </div>

            {/* Método de Pagamento */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Método de Pagamento</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {paymentMethods.map(method => (
                  <button
                    key={method.id}
                    onClick={() => setPaymentMethod(method.id)}
                    className={`flex items-center p-4 border-2 rounded-lg transition-colors ${
                      paymentMethod === method.id
                        ? 'border-orange-600 bg-orange-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="mr-3">{method.icon}</div>
                    <span className="font-medium">{method.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Resumo do Pedido */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Resumo do Pedido</h2>
              <div className="space-y-2 mb-4">
                {cart.map(item => (
                  <div key={item.product.id} className="flex justify-between">
                    <span>{item.product.name} x {item.quantity}</span>
                    <span>R$ {(item.product.price * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <div className="pt-4 border-t border-gray-200">
                <div className="flex justify-between text-xl font-bold">
                  <span>Total:</span>
                  <span className="text-orange-600">R$ {getTotalValue().toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Botão Finalizar */}
            <button
              onClick={handlePayment}
              disabled={!selectedCustomer || !paymentMethod || loading}
              className="w-full bg-orange-600 text-white py-4 px-6 rounded-lg font-semibold text-lg hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Processando...' : 'Finalizar Pagamento'}
            </button>
          </div>
        )}

        {/* Modais */}
        {showCustomerModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Selecionar Cliente</h2>
                <button
                  onClick={() => setShowCustomerModal(false)}
                  className="text-gray-400 hover:text-gray-600 focus:outline-none"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              <div className="p-6">
                {loadingCustomers ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Carregando clientes...</p>
                  </div>
                ) : customers.length === 0 ? (
                  <div className="text-center py-8">
                    <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">Nenhum cliente encontrado</p>
                    <p className="text-sm text-gray-500">Cadastre clientes na página de clientes primeiro</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {customers.map(customer => (
                      <div
                        key={customer.id}
                        onClick={() => {
                          setSelectedCustomer(customer);
                          setShowCustomerModal(false);
                        }}
                        className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      >
                        <h4 className="font-medium">{customer.name}</h4>
                        <p className="text-sm text-gray-600">{customer.email}</p>
                        <p className="text-sm text-gray-600">{customer.phone}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}