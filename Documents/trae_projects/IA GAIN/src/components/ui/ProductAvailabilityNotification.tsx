import React, { useState, useEffect } from 'react';
import { AlertCircle, Clock, CheckCircle, Package } from 'lucide-react';

interface ProductAvailabilityNotificationProps {
  product: {
    id: string;
    name: string;
    stock: number;
    minStock: number;
    preparationTime: number;
    isActive: boolean;
  };
  onClose: () => void;
}

const ProductAvailabilityNotification: React.FC<ProductAvailabilityNotificationProps> = ({ 
  product, 
  onClose 
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300);
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  const getAvailabilityStatus = () => {
    if (!product.isActive) {
      return {
        type: 'inactive',
        title: 'Produto Indisponível',
        message: 'Este produto não está disponível no momento',
        icon: <Package className="w-5 h-5" />,
        bgColor: 'bg-gray-100',
        borderColor: 'border-gray-300',
        textColor: 'text-gray-700'
      };
    }

    if (product.stock <= 0) {
      return {
        type: 'out-of-stock',
        title: 'Fora de Estoque',
        message: `Este produto está em produção. Tempo estimado: ${product.preparationTime}h`,
        icon: <Clock className="w-5 h-5" />,
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        textColor: 'text-orange-800'
      };
    }

    if (product.stock <= product.minStock) {
      return {
        type: 'low-stock',
        title: 'Estoque Baixo',
        message: `Apenas ${product.stock} unidades disponíveis. Pedido pode levar ${product.preparationTime}h para preparo`,
        icon: <AlertCircle className="w-5 h-5" />,
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        textColor: 'text-yellow-800'
      };
    }

    if (product.preparationTime > 0) {
      return {
        type: 'preparation',
        title: 'Tempo de Preparo',
        message: `Produto disponível! Tempo de preparo: ${product.preparationTime}h`,
        icon: <Clock className="w-5 h-5" />,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        textColor: 'text-blue-800'
      };
    }

    return {
      type: 'available',
      title: 'Disponível',
      message: 'Produto em estoque e pronto para entrega',
      icon: <CheckCircle className="w-5 h-5" />,
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-800'
    };
  };

  const status = getAvailabilityStatus();

  return (
    <div className={`fixed top-4 right-4 z-50 transition-all duration-300 ${
      isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
    }`}>
      <div className={`max-w-sm rounded-lg border-l-4 p-4 shadow-lg ${
        status.bgColor
      } ${status.borderColor} ${status.textColor}`}>
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <div className={`p-2 rounded-full ${
              status.type === 'inactive' ? 'bg-gray-200' :
              status.type === 'out-of-stock' ? 'bg-orange-200' :
              status.type === 'low-stock' ? 'bg-yellow-200' :
              status.type === 'preparation' ? 'bg-blue-200' :
              'bg-green-200'
            }`}>
              {status.icon}
            </div>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium">{status.title}</h3>
            <p className="mt-1 text-sm opacity-90">{status.message}</p>
            <p className="mt-2 text-xs font-medium">{product.name}</p>
          </div>
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={handleClose}
              className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 transition ease-in-out duration-150"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductAvailabilityNotification;