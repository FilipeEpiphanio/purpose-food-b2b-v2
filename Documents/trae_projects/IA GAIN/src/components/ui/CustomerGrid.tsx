import React from 'react';
import { User, Mail, Phone, MapPin, Calendar, DollarSign, Package, Eye, Edit, Trash2 } from 'lucide-react';

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

interface CustomerGridProps {
  customers: Customer[];
  onEdit: (customer: Customer) => void;
  onDelete: (customer: Customer) => void;
  onView: (customer: Customer) => void;
}

export default function CustomerGrid({ customers, onEdit, onDelete, onView }: CustomerGridProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Ativo';
      case 'inactive':
        return 'Inativo';
      default:
        return status;
    }
  };

  const formatCurrency = (value: number) => {
    return `R$ ${value.toFixed(2)}`;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Nunca';
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {customers.map((customer) => (
        <div key={customer.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-orange-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">{customer.name}</h3>
                  <p className="text-sm text-gray-500">{customer.id}</p>
                </div>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(customer.status)}`}>
                {getStatusLabel(customer.status)}
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="p-4 space-y-3">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Mail className="w-4 h-4 text-gray-400" />
              <span className="truncate">{customer.email}</span>
            </div>

            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Phone className="w-4 h-4 text-gray-400" />
              <span>{customer.phone}</span>
            </div>

            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="truncate">{customer.neighborhood}, {customer.city}</span>
            </div>

            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span>Cadastro: {formatDate(customer.registrationDate)}</span>
            </div>

            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Package className="w-4 h-4 text-gray-400" />
              <span>{customer.totalOrders} pedidos</span>
            </div>

            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <DollarSign className="w-4 h-4 text-gray-400" />
              <span className="font-medium text-green-600">{formatCurrency(customer.totalSpent)}</span>
            </div>

            {customer.lastOrderDate && (
              <div className="text-xs text-gray-500">
                Último pedido: {formatDate(customer.lastOrderDate)}
              </div>
            )}

            {customer.notes && (
              <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
                <strong>Obs:</strong> {customer.notes}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <button
                onClick={() => onView(customer)}
                className="flex-1 flex items-center justify-center px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 border border-blue-200 rounded-md transition-colors"
                title="Visualizar"
              >
                <Eye className="w-4 h-4 mr-1" />
                Ver
              </button>
              <button
                onClick={() => onEdit(customer)}
                className="flex-1 flex items-center justify-center px-3 py-2 text-sm text-orange-600 hover:bg-orange-50 border border-orange-200 rounded-md transition-colors"
                title="Editar"
              >
                <Edit className="w-4 h-4 mr-1" />
                Editar
              </button>
              <button
                onClick={() => onDelete(customer)}
                className="flex-1 flex items-center justify-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 border border-red-200 rounded-md transition-colors"
                title="Excluir"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Excluir
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}