import React from 'react';
import { Edit, Package, Clock, DollarSign, AlertTriangle } from 'lucide-react';
import { Product } from '@/types/product';

interface ProductGridProps {
  products: Product[];
  onEdit: (product: Product) => void;
  onView: (product: Product) => void;
}

export default function ProductGrid({ products, onEdit, onView }: ProductGridProps) {
  const getProfitMargin = (price: number, cost: number) => {
    return ((price - cost) / price * 100).toFixed(1);
  };

  const getStockStatus = (stock: number, min_stock: number) => {
    if (stock <= 0) return { status: 'out', label: 'Sem estoque', color: 'text-red-600 bg-red-50' };
    if (stock <= min_stock) return { status: 'low', label: 'Estoque baixo', color: 'text-orange-600 bg-orange-50' };
    return { status: 'ok', label: 'Estoque OK', color: 'text-green-600 bg-green-50' };
  };

  const getImageUrl = (product: Product) => {
    if (product.image_url) return product.image_url;
    
    // Imagens padrão por categoria
    const categoryImages = {
      'bolos': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Bolo%20de%20chocolate%20com%20cobertura%20de%20brigadeiro%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'tortas': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Torta%20de%20morango%20com%20creme%20de%20baunilha%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'brigadeiros': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Brigadeiros%20gourmet%20artesanais%20com%20chocolate%20belga%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'salgados': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Coxinha%20de%20frango%20tradicional%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square',
      'pães': 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=P%C3%A3o%20de%20queijo%20mineiro%20tradicional%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita%2C%20estilo%20gourmet&image_size=square'
    };
    
    const categoryKey = product.category.toLowerCase();
    return categoryImages[categoryKey] || categoryImages['salgados'];
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {products.map((product) => {
        const stockStatus = getStockStatus(product.stock, product.min_stock);
        const profitMargin = getProfitMargin(product.price, product.cost);
        
        return (
          <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden">
            {/* Product Image */}
            <div className="relative h-48 bg-gray-100">
              <img
                src={getImageUrl(product)}
                alt={product.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.src = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=Produto%20aliment%C3%ADcio%20gourmet%2C%20foto%20profissional%2C%20ilumina%C3%A7%C3%A3o%20perfeita&image_size=square';
                }}
              />
              {product.status === 'inactive' && (
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                  <span className="bg-gray-800 text-white px-3 py-1 rounded-full text-sm font-medium">
                    INATIVO
                  </span>
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="p-4">
              {/* Header */}
              <div className="mb-3">
                <h3 className="font-semibold text-gray-900 text-lg mb-1">{product.name}</h3>
                <span className="inline-block px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full font-medium">
                  {product.category}
                </span>
              </div>

              {/* Description */}
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                {product.description}
              </p>

              {/* Price and Stock */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <DollarSign className="w-4 h-4 text-green-600" />
                    <span className="font-bold text-green-600 text-lg">
                      R$ {product.price.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Package className="w-4 h-4 text-gray-500" />
                    <span className={`text-sm font-medium ${stockStatus.color}`}>
                      {product.stock} {product.unit}
                    </span>
                  </div>
                </div>

                {/* Preparation Time */}
                {product.preparation_time && (
                  <div className="flex items-center space-x-2 text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">
                      {product.preparation_time}h de preparo
                    </span>
                  </div>
                )}

                {/* Profit Margin */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Margem:</span>
                  <span className="text-sm font-medium text-purple-600">
                    {profitMargin}%
                  </span>
                </div>

                {/* Stock Status */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Status:</span>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${stockStatus.color}`}>
                    {stockStatus.label}
                  </span>
                </div>
              </div>

              {/* Ingredients Preview */}
              {product.ingredients && (
                <div className="mb-4">
                  <p className="text-sm text-gray-500 mb-1">Ingredientes principais:</p>
                  <div className="flex flex-wrap gap-1">
                    {(() => {
                      try {
                        // Garantir que ingredients seja sempre um array
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
                        } else if (product.ingredients) {
                          // Se for outro tipo, converter para string
                          ingredientsArray = [String(product.ingredients)];
                        }
                        
                        // Garantir que é um array de strings
                        ingredientsArray = ingredientsArray.filter(item => item && typeof item === 'string');
                        
                        return (
                          <>
                            {ingredientsArray.slice(0, 3).map((ingredient: string, index: number) => (
                              <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                                {ingredient}
                              </span>
                            ))}
                            {ingredientsArray.length > 3 && (
                              <span className="text-xs text-gray-500">+{ingredientsArray.length - 3}</span>
                            )}
                          </>
                        );
                      } catch (error) {
                        console.error('Erro ao processar ingredientes:', error);
                        return null;
                      }
                    })()}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <button
                  onClick={() => onView(product)}
                  className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm font-medium"
                >
                  Ver Detalhes
                </button>
                <button
                  onClick={() => onEdit(product)}
                  className="flex items-center justify-center px-3 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 transition-colors"
                >
                  <Edit className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}