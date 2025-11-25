import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, ArrowLeft, Package, Clock, DollarSign, AlertTriangle, CheckCircle, Filter } from 'lucide-react';
import { useNotifications, Notification } from '@/services/notificationTypes';

const Notifications: React.FC = () => {
  const navigate = useNavigate();
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();
  const [filter, setFilter] = useState<string>('all');

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'product_out_of_stock':
      case 'product_low_stock':
        return <Package className="w-5 h-5 text-orange-500" />;
      case 'production_needed':
      case 'delivery_scheduled':
        return <Clock className="w-5 h-5 text-blue-500" />;
      case 'payment_confirmed':
        return <DollarSign className="w-5 h-5 text-green-500" />;
      case 'product_updated':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'order_status_changed':
        return <Package className="w-5 h-5 text-purple-500" />;
      default:
        return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Agora';
    if (diffInMinutes < 60) return `${diffInMinutes} min atrás`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h atrás`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d atrás`;
  };

  const handleNotificationClick = (notification: Notification) => {
    if (notification.id && !notification.is_read) {
      markAsRead(notification.id);
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !notification.is_read;
    return notification.type === filter;
  });

  const filterOptions = [
    { value: 'all', label: 'Todas' },
    { value: 'unread', label: 'Não lidas' },
    { value: 'product_low_stock', label: 'Estoque baixo' },
    { value: 'order_status_changed', label: 'Pedidos' },
    { value: 'payment_confirmed', label: 'Pagamentos' },
  ];

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Notificações</h1>
              <p className="text-gray-600">{unreadCount} notificações não lidas</p>
            </div>
          </div>
          
          {notifications.length > 0 && (
            <button
              onClick={markAllAsRead}
              className="px-4 py-2 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
            >
              Marcar todas como lidas
            </button>
          )}
        </div>

        {/* Filter */}
        <div className="flex items-center space-x-4 mb-6">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              {filterOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Notifications List */}
        {filteredNotifications.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filter === 'unread' ? 'Nenhuma notificação não lida' : 'Nenhuma notificação'}
            </h3>
            <p className="text-gray-600">
              {filter === 'unread' 
                ? 'Você não tem notificações não lidas no momento.' 
                : 'Você não tem notificações no momento.'
              }
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-4 border rounded-lg transition-colors cursor-pointer ${
                  !notification.is_read 
                    ? 'bg-blue-50 border-blue-200 hover:bg-blue-100' 
                    : 'bg-white border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    {getNotificationIcon(notification.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-medium text-gray-900">
                        {notification.title}
                      </h3>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-500">
                          {formatTime(notification.created_at)}
                        </span>
                        {!notification.is_read && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {notification.message}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Notifications;