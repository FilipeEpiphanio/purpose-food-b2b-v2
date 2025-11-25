import React, { useState, useEffect } from 'react';
import { X, Save, Plus, User, Phone, MapPin, Clock, DollarSign, CreditCard, Package, ShoppingCart } from 'lucide-react';

interface OrderFormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'textarea';
  required?: boolean;
  options?: { value: string; label: string }[];
  placeholder?: string;
}

interface OrderFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any, action: 'save-exit' | 'save-new') => void;
  title: string;
  fields: any[];
  initialData?: any;
}

export default function OrderFormModal({
  isOpen,
  onClose,
  onSubmit,
  title,
  fields,
  initialData
}: OrderFormModalProps) {
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    } else {
      // Valores padrão para novo pedido
      setFormData({
        status: 'pending',
        paymentStatus: 'pending',
        orderType: 'pickup'
      });
    }
  }, [initialData, isOpen]);

  const handleInputChange = (name: string, value: any) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (action: 'save-exit' | 'save-new') => {
    onSubmit(formData, action);
    if (action === 'save-exit') {
      onClose();
    } else {
      // Reset form for new order
      setFormData({
        status: 'pending',
        paymentStatus: 'pending',
        orderType: 'pickup'
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <ShoppingCart className="w-5 h-5 mr-2 text-orange-500" />
            {title}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <div className="p-6 space-y-4">
          {fields.map((field) => (
            <div key={field.name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              
              {field.type === 'select' ? (
                <select
                  name={field.name}
                  value={formData[field.name] || ''}
                  onChange={(e) => handleInputChange(field.name, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
                  required={field.required}
                >
                  <option value="">Selecione...</option>
                  {field.options?.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : field.type === 'textarea' ? (
                <textarea
                  name={field.name}
                  value={formData[field.name] || ''}
                  onChange={(e) => handleInputChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500"
                  rows={3}
                  required={field.required}
                />
              ) : (
                <div className="relative">
                  {field.name === 'customer' && (
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  )}
                  {field.name === 'customerPhone' && (
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  )}
                  {field.name === 'address' && (
                    <MapPin className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  )}
                  <input
                    type={field.type}
                    name={field.name}
                    value={formData[field.name] || ''}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    placeholder={field.placeholder}
                    className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-orange-500 focus:border-orange-500 ${
                      field.name === 'customer' || field.name === 'customerPhone' || field.name === 'address' ? 'pl-10' : ''
                    }`}
                    required={field.required}
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Footer with new buttons */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          
          <div className="flex space-x-3">
            <button
              onClick={() => handleSubmit('save-new')}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Salvar e Novo
            </button>
            <button
              onClick={() => handleSubmit('save-exit')}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors flex items-center"
            >
              <Save className="w-4 h-4 mr-2" />
              Salvar e Sair
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
