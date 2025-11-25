import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle, Package, Clock, MapPin, CreditCard } from 'lucide-react';

interface OrderConfirmationProps {
  orderId?: string;
  total?: number;
  deliveryOption?: 'delivery' | 'pickup';
  estimatedTime?: string;
}

const OrderConfirmation: React.FC<OrderConfirmationProps> = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Obter dados do state da navegação ou usar valores padrão
  const orderData = location.state as OrderConfirmationProps || {
    orderId: 'PED-' + Date.now().toString().slice(-6),
    total: 0,
    deliveryOption: 'delivery' as const,
    estimatedTime: '30-45 minutos'
  };

  const { orderId, total, deliveryOption, estimatedTime } = orderData;

  const handleContinueShopping = () => {
    navigate('/cardapio');
  };

  const handleViewOrders = () => {
    navigate('/pedidos');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Pedido Confirmado!</h1>
          <p className="text-gray-600">Seu pedido foi recebido e está sendo preparado</p>
        </div>

        {/* Order Details */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Detalhes do Pedido</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Package className="w-5 h-5 text-orange-500 mr-3" />
                <span className="text-gray-700">Número do Pedido</span>
              </div>
              <span className="font-semibold text-gray-900">#{orderId}</span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="w-5 h-5 text-orange-500 mr-3" />
                <span className="text-gray-700">Tempo Estimado</span>
              </div>
              <span className="font-semibold text-gray-900">{estimatedTime}</span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <MapPin className="w-5 h-5 text-orange-500 mr-3" />
                <span className="text-gray-700">Tipo de Entrega</span>
              </div>
              <span className="font-semibold text-gray-900">
                {deliveryOption === 'delivery' ? 'Entrega' : 'Retirada'}
              </span>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="flex items-center">
                <CreditCard className="w-5 h-5 text-orange-500 mr-3" />
                <span className="text-gray-700 text-lg">Total</span>
              </div>
              <span className="text-2xl font-bold text-orange-600">
                R$ {total?.toFixed(2) || '0.00'}
              </span>
            </div>
          </div>
        </div>

        {/* Status Information */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <Clock className="w-5 h-5 text-blue-600 mr-3 mt-0.5" />
            <div>
              <h3 className="text-blue-900 font-semibold mb-1">Acompanhamento do Pedido</h3>
              <p className="text-blue-800 text-sm">
                Você pode acompanhar o status do seu pedido na página "Meus Pedidos". 
                Enviaremos atualizações sobre o progresso.
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={handleContinueShopping}
            className="flex-1 bg-orange-500 text-white py-3 px-6 rounded-lg font-semibold hover:bg-orange-600 transition-colors"
          >
            Continuar Comprando
          </button>
          <button
            onClick={handleViewOrders}
            className="flex-1 bg-gray-100 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
          >
            Ver Meus Pedidos
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;