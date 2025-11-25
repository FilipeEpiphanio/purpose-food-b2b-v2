import React from 'react';
import { Clock, AlertCircle, CheckCircle, Package } from 'lucide-react';

interface AvailabilityInfoProps {
  stock: number;
  minStock: number;
  preparationTime: number;
  isActive: boolean;
  className?: string;
}

const AvailabilityInfo: React.FC<AvailabilityInfoProps> = ({ 
  stock, 
  minStock, 
  preparationTime, 
  isActive,
  className = ''
}) => {
  if (!isActive) {
    return (
      <div className={`flex items-center text-gray-500 ${className}`}>
        <Package className="w-4 h-4 mr-2" />
        <span className="text-sm">Produto indisponível</span>
      </div>
    );
  }

  if (stock <= 0) {
    return (
      <div className={`flex items-center text-orange-600 ${className}`}>
        <Clock className="w-4 h-4 mr-2" />
        <span className="text-sm">Em produção: {preparationTime}h</span>
      </div>
    );
  }

  if (stock <= minStock) {
    return (
      <div className={`flex items-center text-yellow-600 ${className}`}>
        <AlertCircle className="w-4 h-4 mr-2" />
        <span className="text-sm">Últimas {stock} unidades</span>
      </div>
    );
  }

  if (preparationTime > 0) {
    return (
      <div className={`flex items-center text-blue-600 ${className}`}>
        <Clock className="w-4 h-4 mr-2" />
        <span className="text-sm">Pronto em: {preparationTime}h</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center text-green-600 ${className}`}>
      <CheckCircle className="w-4 h-4 mr-2" />
      <span className="text-sm">Disponível para entrega imediata</span>
    </div>
  );
};

export default AvailabilityInfo;