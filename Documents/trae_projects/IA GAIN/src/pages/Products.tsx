import React, { useState, useEffect } from 'react';
import DataTable from '@/components/ui/DataTable';
import ProductFormModal from '@/components/ui/ProductFormModal';
import ProductGrid from '@/components/ui/ProductGrid';
import { Plus, Package, Edit, Trash2, Eye, Filter, Grid, List, Search, AlertTriangle } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import { Product } from '@/types/product';

const Products: React.FC = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const categories = ['Bolos', 'Tortas', 'Brigadeiros', 'Salgados', 'Pães', 'Doces', 'Bebidas'];
  const units = [
    { value: 'un', label: 'Unidade (un)' },
    { value: 'kg', label: 'Quilograma (kg)' },
    { value: 'g', label: 'Grama (g)' },
    { value: 'lt', label: 'Litro (lt)' },
    { value: 'ml', label: 'Mililitro (ml)' },
    { value: 'cx', label: 'Caixa (cx)' },
    { value: 'pc', label: 'Pacote (pc)' },
    { value: 'porcao', label: 'Porção' }
  ];

  const formFields = [
    {
      name: 'name',
      label: 'Nome do Produto',
      type: 'text' as const,
      required: true,
      placeholder: 'Digite o nome do produto'
    },
    {
      name: 'category',
      label: 'Categoria',
      type: 'select' as const,
      required: true,
      options: categories.map(cat => ({ value: cat, label: cat }))
    },
    {
      name: 'description',
      label: 'Descrição',
      type: 'textarea' as const,
      placeholder: 'Descrição do produto (opcional)'
    },
    {
      name: 'ingredients',
      label: 'Ingredientes',
      type: 'ingredients' as const,
      placeholder: 'Digite um ingrediente'
    },
    {
      name: 'price',
      label: 'Preço de Venda',
      type: 'currency' as const,
      required: true,
      placeholder: '0.00'
    },
    {
      name: 'cost',
      label: 'Custo de Produção',
      type: 'currency' as const,
      required: true,
      placeholder: '0.00'
    },
    {
      name: 'stock',
      label: 'Estoque Atual',
      type: 'number' as const,
      required: true,
      placeholder: '0'
    },
    {
      name: 'min_stock',
      label: 'Estoque Mínimo',
      type: 'number' as const,
      required: true,
      placeholder: '0'
    },
    {
      name: 'unit',
      label: 'Unidade de Venda',
      type: 'select' as const,
      required: true,
      options: units
    },
    {
      name: 'preparation_time',
      label: 'Tempo de Preparo (horas)',
      type: 'number' as const,
      placeholder: '0.5'
    },
    {
      name: 'is_active',
      label: 'Produto Ativo',
      type: 'toggle' as const
    }
  ];

  // Fetch products from database
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Erro ao buscar produtos:', error);
      } else {
        setProducts(data || []);
      }
    } catch (error) {
      console.error('Erro ao buscar produtos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: any, action: 'save-exit' | 'save-new') => {
    try {
      let result;
      
      // Preparar dados para salvar, convertendo ingredients para JSON string se for array
      const productData = {
        ...data,
        ingredients: Array.isArray(data.ingredients) ? JSON.stringify(data.ingredients) : data.ingredients,
        status: data.is_active ? 'active' : 'inactive'
      };
      
      if (editingProduct) {
        // Update existing product
        result = await supabase
          .from('products')
          .update({
            ...productData,
            updated_at: new Date().toISOString()
          })
          .eq('id', editingProduct.id);
      } else {
        // Create new product
        result = await supabase
          .from('products')
          .insert([{
            ...productData,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }]);
      }

      if (result.error) {
        console.error('Erro ao salvar produto:', result.error);
        alert('Erro ao salvar produto: ' + result.error.message);
      } else {
        await fetchProducts(); // Refresh the list
        
        if (action === 'save-exit') {
          setIsFormOpen(false);
          setEditingProduct(null);
        } else {
          // Reset form for new product
          setEditingProduct(null);
        }
      }
    } catch (error) {
      console.error('Erro ao salvar produto:', error);
      alert('Erro ao salvar produto: ' + error);
    }
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setIsFormOpen(true);
  };

  const handleDelete = async (product: Product) => {
    if (confirm(`Deseja realmente excluir o produto ${product.name}?`)) {
      try {
        const { error } = await supabase
          .from('products')
          .delete()
          .eq('id', product.id);

        if (error) {
          console.error('Erro ao excluir produto:', error);
          alert('Erro ao excluir produto: ' + error.message);
        } else {
          await fetchProducts();
        }
      } catch (error) {
        console.error('Erro ao excluir produto:', error);
        alert('Erro ao excluir produto: ' + error);
      }
    }
  };

  const handleView = (product: Product) => {
    // Processar ingredientes de forma segura
    let ingredientsText = 'Não informado';
    if (product.ingredients) {
      try {
        let ingredientsArray: string[] = [];
        
        if (Array.isArray(product.ingredients)) {
          ingredientsArray = product.ingredients;
        } else if (typeof product.ingredients === 'string') {
          // Tentar fazer parse do JSON
          try {
            ingredientsArray = JSON.parse(product.ingredients);
          } catch {
            // Se não for JSON válido, tratar como string única
            ingredientsArray = [product.ingredients];
          }
        } else {
          // Se for outro tipo, converter para string
          ingredientsArray = [String(product.ingredients)];
        }
        
        // Garantir que é um array de strings válido
        ingredientsArray = ingredientsArray.filter(item => item && typeof item === 'string');
        
        if (ingredientsArray.length > 0) {
          ingredientsText = ingredientsArray.join(', ');
        }
      } catch (error) {
        console.error('Erro ao processar ingredientes:', error);
        ingredientsText = 'Não informado';
      }
    }
    
    alert(`Detalhes do Produto:

Nome: ${product.name}
Categoria: ${product.category}
Preço: R$ ${product.price.toFixed(2)}
Custo: R$ ${product.cost.toFixed(2)}
Estoque: ${product.stock} ${product.unit}
Estoque Mínimo: ${product.min_stock} ${product.unit}
Tempo de Preparo: ${product.preparation_time || 0}h
Status: ${product.status === 'active' ? 'Ativo' : 'Inativo'}

Descrição: ${product.description}

Ingredientes: ${ingredientsText}`);
  };

  // Filter products
  const filteredProducts = products.filter(product => {
    const matchesCategory = filterCategory === 'all' || product.category === filterCategory;
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const lowStockProducts = products.filter(p => p.stock <= p.min_stock);

  // Data table columns for list view
  const columns = [
    {
      key: 'name',
      header: 'Nome',
      sortable: true
    },
    {
      key: 'category',
      header: 'Categoria',
      sortable: true
    },
    {
      key: 'price',
      header: 'Preço',
      sortable: true,
      render: (value: number) => `R$ ${value.toFixed(2)}`
    },
    {
      key: 'stock',
      header: 'Estoque',
      sortable: true,
      render: (value: number, row: Product) => {
        const isLowStock = value <= row.min_stock;
        return (
          <span className={isLowStock ? 'text-red-600 font-medium' : ''}>
            {value} {row.unit}
          </span>
        );
      }
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
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando produtos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Produtos</h1>
          <p className="text-gray-600 mt-1">Controle completo do seu catálogo alimentar</p>
        </div>
        <button
          onClick={() => {
            setEditingProduct(null);
            setIsFormOpen(true);
          }}
          className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Novo Produto
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total de Produtos</p>
              <p className="text-2xl font-bold text-gray-900">{products.length}</p>
            </div>
            <Package className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Estoque Baixo</p>
              <p className="text-2xl font-bold text-red-600">{lowStockProducts.length}</p>
            </div>
            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-4 h-4 text-red-600" />
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Valor Total</p>
              <p className="text-2xl font-bold text-green-600">
                R$ {products.reduce((sum, p) => sum + (p.price * p.stock), 0).toFixed(2)}
              </p>
            </div>
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 font-bold text-sm">$</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Lucro Estimado</p>
              <p className="text-2xl font-bold text-purple-600">
                R$ {products.reduce((sum, p) => sum + ((p.price - p.cost) * p.stock), 0).toFixed(2)}
              </p>
            </div>
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <span className="text-purple-600 font-bold text-sm">%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar produtos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
            />
          </div>

          {/* Filters and View Toggle */}
          <div className="flex items-center space-x-4">
            {/* Category Filter */}
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              >
                <option value="all">Todas as categorias</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm text-orange-600' : 'text-gray-500'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm text-orange-600' : 'text-gray-500'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        
        {lowStockProducts.length > 0 && (
          <div className="mt-4 text-sm text-orange-600 font-medium">
            ⚠️ {lowStockProducts.length} produto(s) com estoque baixo
          </div>
        )}
      </div>

      {/* Products Display */}
      {viewMode === 'grid' ? (
        <ProductGrid
          products={filteredProducts}
          onEdit={handleEdit}
          onView={handleView}
        />
      ) : (
        <DataTable
          columns={columns}
          data={filteredProducts}
          title="Lista de Produtos"
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={handleView}
        />
      )}

      {/* Form Modal */}
      <ProductFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingProduct(null);
        }}
        onSubmit={handleSubmit}
        title={editingProduct ? 'Editar Produto' : 'Novo Produto'}
        fields={formFields}
        initialData={editingProduct || { is_active: true }}
      />
    </div>
  );
};

export default Products;