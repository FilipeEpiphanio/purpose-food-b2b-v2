import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple' | 'pink';
}

export default function MetricCard({
  title,
  value,
  icon,
  trend,
  color = 'blue'
}: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    pink: 'bg-pink-50 text-pink-600 border-pink-200'
  };

  const trendColorClasses = {
    blue: trend?.isPositive ? 'text-blue-600' : 'text-blue-400',
    green: trend?.isPositive ? 'text-green-600' : 'text-green-400',
    orange: trend?.isPositive ? 'text-orange-600' : 'text-orange-400',
    red: trend?.isPositive ? 'text-red-600' : 'text-red-400',
    purple: trend?.isPositive ? 'text-purple-600' : 'text-purple-400',
    pink: trend?.isPositive ? 'text-pink-600' : 'text-pink-400'
  };

  return (
    <div className={`bg-white rounded-lg border p-6 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <div className="flex items-center mt-2">
              <span className={`text-sm font-medium ${trendColorClasses[color]}`}>
                {trend.isPositive ? '↗' : '↘'} {Math.abs(trend.value)}%
              </span>
              <span className="text-xs text-gray-500 ml-2">vs mês anterior</span>
            </div>
          )}
        </div>
        <div className="flex-shrink-0">
          {icon}
        </div>
      </div>
    </div>
  );
}