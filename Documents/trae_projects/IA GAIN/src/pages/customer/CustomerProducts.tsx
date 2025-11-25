import React, { useState, useEffect } from 'react';
import { Search, Filter, ShoppingCart, Star, Clock, ChevronDown } from 'lucide-react';
import { useCustomerStore } from '../../stores/customerStore';
import { supabase } from '../../lib/supabase';
import { realTimeSyncService } from '../../services/realTimeSync';
import { notificationService } from '../../services/notificationService';
import { useProductAvailability } from '../../hooks/useProductAvailability';
import ProductAvailabilityNotification from '../../components/ui/ProductAvailabilityNotification';
import { loadProductsWithFallback } from '../../utils/databaseHelpers';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  category: string;
  is_active: boolean;
  preparation_time: number;
  ingredients: string[];
  stock_current: number;
}

const CustomerProducts: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [priceRange, setPriceRange] = useState({ min: 0, max: 1000 });
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  
  const { addToCart, customer } = useCustomerStore();
  const { notifications, showNotification, removeNotification, subscribeToProduct, unsubscribeFromProduct } = useProductAvailability();

  const categories = [
    'all', 'Salgados', 'Doces', 'Bolos', 'Tortas', 'Pães', 'Bebidas'
  ];

  useEffect(() => {
    loadProducts();
    
    // Configurar listener para mudanças em tempo real nos produtos
    try {
      const unsubscribe = realTimeSyncService.onProductChange((data: any) => {
        console.log('Produto atualizado via sincronização:', data);
        loadProducts(); // Recarregar produtos quando houver mudanças
        
        // Mostrar notificação para o cliente se for uma mudança relevante
        if (customer && data.changes && data.changes.length > 0) {
          const product = data.product;
          if (data.changes.includes('price') || data.changes.includes('stock_current')) {
            notificationService.createAvailabilityNotification(
              customer.id,
              product.name,
              {
                delivery_type: product.stock_current > 0 ? 'immediate' : 'production',
                preparation_time: product.preparation_time,
                stock_current: product.stock_current
              }
            );
          }
        }
      });

      return () => {
        try {
          unsubscribe();
        } catch (error) {
          console.error('Erro ao remover listener:', error);
        }
      };
    } catch (error) {
      console.error('Erro ao configurar sincronização em tempo real:', error);
      // Continuar funcionando mesmo sem sincronização
    }
  }, [customer]);

  useEffect(() => {
    filterProducts();
  }, [products, searchTerm, selectedCategory, priceRange, sortBy, sortOrder]);

  const loadProducts = async () => {
    try {
      const { data, error } = await loadProductsWithFallback(supabase, {
        orderBy: 'name',
        ascending: true
      });

      if (error) throw error;
      // Filtrar manualmente produtos ativos (caso a coluna is_active não exista no banco)
      const activeProducts = data?.filter(product => 
        product.is_active === undefined || product.is_active === true
      ) || [];
      setProducts(activeProducts);
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterProducts = () => {
    let filtered = products.filter(product => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.description.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
      
      const matchesPrice = product.price >= priceRange.min && product.price <= priceRange.max;
      
      return matchesSearch && matchesCategory && matchesPrice;
    });

    // Sort products
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'price':
          aValue = a.price;
          bValue = b.price;
          break;
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'preparation_time':
          aValue = a.preparation_time;
          bValue = b.preparation_time;
          break;
        default:
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
      }
      
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    setFilteredProducts(filtered);
  };

  const handleAddToCart = (product: Product) => {
    // Mostrar notificação de disponibilidade antes de adicionar ao carrinho
    showNotification({
      id: product.id,
      name: product.name,
      stock: product.stock_current,
      minStock: 5, // Valor padrão, pode ser ajustado
      preparationTime: product.preparation_time,
      isActive: product.is_active
    });

    addToCart({
      id: product.id,
      name: product.name,
      price: product.price,
      quantity: 1,
      image: product.image_url
    });
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedCategory('all');
    setPriceRange({ min: 0, max: 1000 });
    setSortBy('name');
    setSortOrder('asc');
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
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Nossos Produtos</h1>
          <p className="text-gray-600">Descubra nossa seleção de delícias artesanais</p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4 mb-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Buscar produtos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <div className="relative">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'Todas Categorias' : category}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
            </div>

            {/* Sort */}
            <div className="relative">
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-');
                  setSortBy(field);
                  setSortOrder(order as 'asc' | 'desc');
                }}
                className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              >
                <option value="name-asc">Nome (A-Z)</option>
                <option value="name-desc">Nome (Z-A)</option>
                <option value="price-asc">Preço (Menor)</option>
                <option value="price-desc">Preço (Maior)</option>
                <option value="preparation_time-asc">Tempo (Rápido)</option>
                <option value="preparation_time-desc">Tempo (Lento)</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-4 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
            >
              <Filter className="w-5 h-5 mr-2" />
              Filtros
            </button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="border-t pt-4 mt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preço Mínimo: R$ {priceRange.min}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1000"
                    value={priceRange.min}
                    onChange={(e) => setPriceRange({ ...priceRange, min: parseInt(e.target.value) })}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preço Máximo: R$ {priceRange.max}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1000"
                    value={priceRange.max}
                    onChange={(e) => setPriceRange({ ...priceRange, max: parseInt(e.target.value) })}
                    className="w-full"
                  />
                </div>
              </div>
              <button
                onClick={clearFilters}
                className="text-orange-600 hover:text-orange-700 font-medium"
              >
                Limpar Filtros
              </button>
            </div>
          )}
        </div>

        {/* Results Info */}
        <div className="mb-6">
          <p className="text-gray-600">
            {filteredProducts.length} produto{filteredProducts.length !== 1 ? 's' : ''} encontrado{filteredProducts.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Products Grid */}
        {filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Nenhum produto encontrado</h3>
            <p className="text-gray-600">Tente ajustar seus filtros de busca</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProducts.map((product) => (
              <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <div className="relative h-48 bg-gray-200">
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-full object-cover rounded-t-lg"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full bg-gray-100 rounded-t-lg">
                      <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
                        <span className="text-gray-400 text-xs">Sem imagem</span>
                      </div>
                    </div>
                  )}
                  {product.stock_current <= 5 && (
                    <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-semibold">
                      Últimas unidades
                    </div>
                  )}
                </div>

                <div className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {product.category}
                    </span>
                    <div className="flex items-center text-gray-600">
                      <Clock className="w-3 h-3 mr-1" />
                      <span className="text-xs">{product.preparation_time}h</span>
                    </div>
                  </div>

                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">
                    {product.name}
                  </h3>
                  
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                    {product.description}
                  </p>

                  {product.ingredients && (
                    <div className="mb-3">
                      <p className="text-xs text-gray-500 mb-1">Ingredientes:</p>
                      <p className="text-xs text-gray-700 line-clamp-2">
                        {(() => {
                          try {
                            let ingredientsArray: string[] = [];
                            
                            if (Array.isArray(product.ingredients)) {
                              ingredientsArray = product.ingredients;
                            } else if (typeof product.ingredients === 'string') {
                              try {
                                ingredientsArray = JSON.parse(product.ingredients);
                              } catch {
                                ingredientsArray = [product.ingredients];
                              }
                            } else {
                              ingredientsArray = [String(product.ingredients)];
                            }
                            
                            ingredientsArray = ingredientsArray.filter(item => item && typeof item === 'string');
                            
                            return ingredientsArray.length > 0 ? ingredientsArray.join(', ') : 'Não informado';
                          } catch (error) {
                            console.error('Erro ao processar ingredientes:', error);
                            return 'Não informado';
                          }
                        })()}
                      </p>
                    </div>
                  )}

                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xl font-bold text-orange-600">
                      R$ {product.price.toFixed(2)}
                    </span>
                    <span className="text-xs text-gray-500">
                      Estoque: {product.stock_current}
                    </span>
                  </div>

                  <button
                    onClick={() => handleAddToCart(product)}
                    disabled={product.stock_current === 0}
                    className={`w-full flex items-center justify-center px-4 py-2 rounded-lg transition-colors ${
                      product.stock_current === 0
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-orange-500 text-white hover:bg-orange-600'
                    }`}
                  >
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    {product.stock_current === 0 ? 'Indisponível' : 'Adicionar'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Notifications */}
      {notifications.map((notification) => (
        <ProductAvailabilityNotification
          key={notification.id}
          product={{
            id: notification.productId,
            name: products.find(p => p.id === notification.productId)?.name || 'Produto',
            stock: products.find(p => p.id === notification.productId)?.stock_current || 0,
            minStock: 5,
            preparationTime: products.find(p => p.id === notification.productId)?.preparation_time || 0,
            isActive: products.find(p => p.id === notification.productId)?.is_active || false
          }}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
};

export default CustomerProducts;