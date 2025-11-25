import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: React.ReactNode;
  color?: 'green' | 'red' | 'blue' | 'orange' | 'purple';
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  color = 'blue'
}) => {
  const getColorClasses = (color: string) => {
    const colors = {
      green: 'bg-green-50 text-green-600 border-green-200',
      red: 'bg-red-50 text-red-600 border-red-200',
      blue: 'bg-blue-50 text-blue-600 border-blue-200',
      orange: 'bg-orange-50 text-orange-600 border-orange-200',
      purple: 'bg-purple-50 text-purple-600 border-purple-200'
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return <TrendingUp className="w-4 h-4" />;
      case 'negative':
        return <TrendingDown className="w-4 h-4" />;
      default:
        return <Minus className="w-4 h-4" />;
    }
  };

  const getChangeColor = (type: string) => {
    switch (type) {
      case 'positive':
        return 'text-green-600';
      case 'negative':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={'bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow duration-200 ' + getColorClasses(color)}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <div className={'flex items-center mt-2 text-sm ' + getChangeColor(changeType)}>
              {getChangeIcon(changeType)}
              <span className="ml-1">{change}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="ml-4">
            <div className="p-3 bg-white rounded-full shadow-sm">
              {icon}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;