import React from 'react';
import { TrendingUp } from 'lucide-react';

interface SalesChartProps {
  data: Array<{
    day: string;
    value: number;
  }>;
}

export default function SalesChart({ data }: SalesChartProps) {
  const maxValue = Math.max(...data.map(d => d.value), 1);
  
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center mb-4">
        <TrendingUp className="w-5 h-5 text-green-500 mr-2" />
        <h2 className="text-xl font-semibold text-gray-900">Vendas dos Últimos 7 Dias</h2>
      </div>
      
      <div className="h-64 relative">
        {/* Grid lines */}
        <div className="absolute inset-0">
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="absolute w-full border-t border-gray-100"
              style={{ top: `${(i * 25)}%` }}
            />
          ))}
        </div>
        
        {/* Chart bars */}
        <div className="relative h-full flex items-end justify-between px-4">
          {data.map((item, index) => {
            const height = (item.value / maxValue) * 100;
            return (
              <div key={index} className="flex flex-col items-center flex-1 mx-1">
                <div className="w-full relative h-full flex items-end">
                  <div
                    className="w-full bg-gradient-to-t from-green-500 to-green-400 rounded-t-md transition-all duration-300 hover:from-green-600 hover:to-green-500"
                    style={{ height: `${height}%` }}
                  >
                    <div className="text-xs text-white text-center pt-1 font-medium">
                      {item.value > 0 ? `R$${item.value}` : ''}
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-500 mt-2 font-medium">
                  {item.day}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Total do período:</span>
          <span className="font-semibold text-gray-900">
            R$ {data.reduce((sum, item) => sum + item.value, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </span>
        </div>
      </div>
    </div>
  );
}