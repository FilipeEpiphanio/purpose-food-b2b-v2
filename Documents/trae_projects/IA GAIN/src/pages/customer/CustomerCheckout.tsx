import React, { useState } from 'react';
import { CreditCard, MapPin, Clock, DollarSign, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCustomerStore } from '../../stores/customerStore';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);

interface CheckoutFormData {
  deliveryOption: 'pickup' | 'delivery';
  deliveryAddress: string;
  deliveryTime: string;
  notes: string;
  paymentMethod: 'card' | 'pix' | 'cash';
}

const CustomerCheckout: React.FC = () => {
  const navigate = useNavigate();
  const { cartItems, getCartTotal, customer, createOrder } = useCustomerStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const [formData, setFormData] = useState<CheckoutFormData>({
    deliveryOption: 'pickup',
    deliveryAddress: customer?.address || '',
    deliveryTime: '',
    notes: '',
    paymentMethod: 'card'
  });

  const subtotal = getCartTotal();
  const deliveryFee = formData.deliveryOption === 'delivery' ? 10 : 0;

  const handlePaymentMethodChange = (method: 'card' | 'pix' | 'cash') => {
    setFormData({ ...formData, paymentMethod: method });
  };
  const total = subtotal + deliveryFee;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);

    try {
      // Criar pedido diretamente no banco de dados com horário de entrega
      const orderData = {
        customer_name: customer?.name || 'Cliente',
        customer_email: customer?.email || '',
        customer_phone: customer?.phone || '',
        delivery_address: formData.deliveryAddress,
        delivery_instructions: formData.notes,
        items: cartItems.map(item => ({
          product_id: item.id,
          quantity: item.quantity,
          price: item.price,
          name: item.name
        })),
        subtotal: subtotal,
        delivery_fee: deliveryFee,
        total: total,
        scheduled_date: formData.deliveryTime, // Horário agendado para entrega
        order_type: formData.deliveryOption,
        payment_method: formData.paymentMethod,
        notes: formData.notes
      };

      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
      });

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Erro ao criar pedido');
      }

      const orderId = result.order.id;
      
      // Processar pagamento com Stripe
      if (formData.paymentMethod === 'card') {
        const stripe = await stripePromise;
        if (!stripe) throw new Error('Stripe não disponível');

        // Criar sessão de checkout
        const stripeResponse = await fetch('/api/create-checkout-session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            orderId,
            items: cartItems.map(item => ({
              name: item.name,
              price: item.price,
              quantity: item.quantity
            })),
            deliveryFee,
            customerEmail: customer?.email,
            deliveryOption: formData.deliveryOption,
            deliveryAddress: formData.deliveryAddress
          }),
        });

        const { sessionId } = await stripeResponse.json();
        
        // Redirecionar para checkout do Stripe
        if (sessionId) {
          window.location.href = `/checkout?session_id=${sessionId}`;
        } else {
          throw new Error('Sessão de checkout não criada');
        }
      } else {
        // Para PIX ou dinheiro, apenas confirmar pedido
        navigate('/confirmacao-pedido');
      }
    } catch (error) {
      console.error('Erro no checkout:', error);
      alert('Erro ao processar pagamento. Tente novamente.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (cartItems.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Carrinho vazio</h2>
          <p className="text-gray-600">Adicione produtos ao carrinho antes de finalizar a compra</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Finalizar Compra</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Checkout Form */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Detalhes do Pedido</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Delivery Option */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Forma de Entrega
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="pickup"
                      checked={formData.deliveryOption === 'pickup'}
                      onChange={(e) => setFormData({ ...formData, deliveryOption: e.target.value as 'pickup' })}
                      className="mr-2 text-orange-500 focus:ring-orange-500"
                    />
                    <MapPin className="w-4 h-4 mr-2 text-gray-400" />
                    <span>Retirar na loja</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="delivery"
                      checked={formData.deliveryOption === 'delivery'}
                      onChange={(e) => setFormData({ ...formData, deliveryOption: e.target.value as 'delivery' })}
                      className="mr-2 text-orange-500 focus:ring-orange-500"
                    />
                    <MapPin className="w-4 h-4 mr-2 text-gray-400" />
                    <span>Entrega em domicílio</span>
                  </label>
                </div>
              </div>

              {/* Delivery Address */}
              {formData.deliveryOption === 'delivery' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Endereço de Entrega
                  </label>
                  <textarea
                    value={formData.deliveryAddress}
                    onChange={(e) => setFormData({ ...formData, deliveryAddress: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    rows={3}
                    placeholder="Digite seu endereço completo..."
                    required
                  />
                </div>
              )}

              {/* Delivery Time */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Horário de Entrega/Retirada
                </label>
                <div className="flex items-center">
                  <Clock className="w-5 h-5 text-gray-400 mr-2" />
                  <input
                    type="datetime-local"
                    value={formData.deliveryTime}
                    onChange={(e) => setFormData({ ...formData, deliveryTime: e.target.value })}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>

              {/* Payment Method */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Forma de Pagamento
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="card"
                      checked={formData.paymentMethod === 'card'}
                      onChange={() => handlePaymentMethodChange('card')}
                      className="mr-2 text-orange-500 focus:ring-orange-500"
                    />
                    <CreditCard className="w-4 h-4 mr-2 text-gray-400" />
                    <span>Cartão de Crédito/Débito</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="pix"
                      checked={formData.paymentMethod === 'pix'}
                      onChange={() => handlePaymentMethodChange('pix')}
                      className="mr-2 text-orange-500 focus:ring-orange-500"
                    />
                    <span>PIX</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="cash"
                      checked={formData.paymentMethod === 'cash'}
                      onChange={() => handlePaymentMethodChange('cash')}
                      className="mr-2 text-orange-500 focus:ring-orange-500"
                    />
                    <span>Dinheiro</span>
                  </label>
                </div>
              </div>

              {/* Special Instructions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Observações (opcional)
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  rows={3}
                  placeholder="Alguma observação sobre seu pedido?"
                />
              </div>

              <button
                type="submit"
                disabled={isProcessing}
                className="w-full bg-orange-500 text-white py-3 px-4 rounded-lg hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-semibold"
              >
                {isProcessing ? 'Processando...' : `Pagar R$ ${total.toFixed(2)}`}
              </button>
            </form>
          </div>

          {/* Order Summary */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Resumo do Pedido</h2>
            
            <div className="space-y-4">
              {cartItems.map((item) => (
                <div key={item.id} className="flex justify-between items-center">
                  <div>
                    <p className="font-medium text-gray-900">{item.name}</p>
                    <p className="text-sm text-gray-600">
                      {item.quantity} × R$ {item.price.toFixed(2)}
                    </p>
                  </div>
                  <p className="font-medium text-gray-900">
                    R$ {(item.price * item.quantity).toFixed(2)}
                  </p>
                </div>
              ))}
              
              <div className="border-t border-gray-200 pt-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-600">Subtotal</span>
                  <span>R$ {subtotal.toFixed(2)}</span>
                </div>
                
                {deliveryFee > 0 && (
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-600">Taxa de entrega</span>
                    <span>R$ {deliveryFee.toFixed(2)}</span>
                  </div>
                )}
                
                <div className="flex justify-between items-center text-lg font-semibold border-t border-gray-200 pt-2">
                  <span>Total</span>
                  <span>R$ {total.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerCheckout;