import { useState, useEffect } from 'react'

export interface Notification {
  id: string
  type: 'product_out_of_stock' | 'product_low_stock' | 'production_needed' | 'delivery_scheduled' | 'payment_confirmed' | 'product_updated' | 'order_status_changed'
  title: string
  message: string
  created_at: string
  is_read: boolean
  userId: string
  actionUrl?: string
  icon?: string
}

export interface NotificationPreferences {
  email: boolean
  inApp: boolean
  sound: boolean
  orderUpdates: boolean
  stockAlerts: boolean
  paymentAlerts: boolean
  systemAlerts: boolean
}

export const useNotifications = (userId?: string, customerId?: string) => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email: true,
    inApp: true,
    sound: true,
    orderUpdates: true,
    stockAlerts: true,
    paymentAlerts: true,
    systemAlerts: true
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const targetUserId = userId || customerId
    if (!targetUserId) return

    // Fetch notifications from API
    const fetchNotifications = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(`/api/notifications?userId=${targetUserId}`)
        if (!response.ok) {
          throw new Error('Erro ao buscar notificações')
        }

        const data = await response.json()
        setNotifications(data.notifications || [])
      } catch (error) {
        console.error('Erro ao buscar notificações:', error)
        setError('Erro ao carregar notificações. Usando dados locais.')
        
        // Fallback to localStorage or mock data
        const loadNotifications = () => {
          const saved = localStorage.getItem(`notifications_${targetUserId}`)
          if (saved) {
            setNotifications(JSON.parse(saved))
          } else {
            // Notificações mock iniciais como fallback
            const mockNotifications: Notification[] = [
              {
                id: '1',
                type: 'order_status_changed',
                title: 'Novo Pedido',
                message: 'Pedido #1234 recebido - R$ 150,00',
                created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
                is_read: false,
                userId: targetUserId,
                icon: '📦'
              },
              {
                id: '2',
                type: 'product_low_stock',
                title: 'Estoque Baixo',
                message: 'Bolo de Chocolate - apenas 2 unidades',
                created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
                is_read: false,
                userId: targetUserId,
                icon: '📊'
              },
              {
                id: '3',
                type: 'payment_confirmed',
                title: 'Pagamento Confirmado',
                message: 'Pagamento do pedido #1233 aprovado',
                created_at: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
                is_read: true,
                userId: targetUserId,
                icon: '💳'
              }
            ]
            setNotifications(mockNotifications)
          }
        }

        loadNotifications()
      } finally {
        setLoading(false)
      }
    }

    fetchNotifications()
  }, [userId, customerId])

  useEffect(() => {
    const unread = notifications.filter(n => !n.is_read).length
    setUnreadCount(unread)
  }, [notifications])

  const markAsRead = async (notificationId: string) => {
    const targetUserId = userId || customerId
    if (!targetUserId) return

    try {
      const response = await fetch(`/api/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId: targetUserId }),
      })

      if (!response.ok) {
        throw new Error('Erro ao marcar notificação como lida')
      }

      // Update local state
      setNotifications(prev => {
        const updated = prev.map(n => 
          n.id === notificationId ? { ...n, is_read: true } : n
        )
        localStorage.setItem(`notifications_${targetUserId}`, JSON.stringify(updated))
        return updated
      })
    } catch (error) {
      console.error('Erro ao marcar notificação como lida:', error)
      // Fallback to local update only
      setNotifications(prev => {
        const updated = prev.map(n => 
          n.id === notificationId ? { ...n, is_read: true } : n
        )
        localStorage.setItem(`notifications_${targetUserId}`, JSON.stringify(updated))
        return updated
      })
    }
  }

  const markAllAsRead = async () => {
    const targetUserId = userId || customerId
    if (!targetUserId) return

    try {
      const response = await fetch('/api/notifications/mark-all-read', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId: targetUserId }),
      })

      if (!response.ok) {
        throw new Error('Erro ao marcar todas as notificações como lidas')
      }

      // Update local state
      setNotifications(prev => {
        const updated = prev.map(n => ({ ...n, is_read: true }))
        localStorage.setItem(`notifications_${targetUserId}`, JSON.stringify(updated))
        return updated
      })
    } catch (error) {
      console.error('Erro ao marcar todas as notificações como lidas:', error)
      // Fallback to local update only
      setNotifications(prev => {
        const updated = prev.map(n => ({ ...n, is_read: true }))
        localStorage.setItem(`notifications_${targetUserId}`, JSON.stringify(updated))
        return updated
      })
    }
  }

  const addNotification = async (notification: Omit<Notification, 'id' | 'created_at' | 'is_read'>) => {
    const targetUserId = userId || customerId
    if (!targetUserId) return

    try {
      const response = await fetch('/api/notifications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...notification,
          userId: targetUserId
        }),
      })

      if (!response.ok) {
        throw new Error('Erro ao adicionar notificação')
      }

      const newNotification = await response.json()
      
      setNotifications(prev => {
        const updated = [newNotification, ...prev]
        localStorage.setItem(`notifications_${targetUserId}`, JSON.stringify(updated))
        return updated
      })
    } catch (error) {
      console.error('Erro ao adicionar notificação:', error)
      // Fallback to local creation only
      const newNotification: Notification = {
        ...notification,
        id: Date.now().toString(),
        created_at: new Date().toISOString(),
        is_read: false
      }
      
      setNotifications(prev => {
        const updated = [newNotification, ...prev]
        localStorage.setItem(`notifications_${targetUserId}`, JSON.stringify(updated))
        return updated
      })
    }
  }

  const removeNotification = (notificationId: string) => {
    const targetUserId = userId || customerId
    if (!targetUserId) return

    setNotifications(prev => {
      const updated = prev.filter(n => n.id !== notificationId)
      localStorage.setItem(`notifications_${targetUserId}`, JSON.stringify(updated))
      return updated
    })
  }

  const clearAllNotifications = () => {
    const targetUserId = userId || customerId
    if (!targetUserId) return

    setNotifications([])
    localStorage.removeItem(`notifications_${targetUserId}`)
  }

  const updatePreferences = (newPreferences: Partial<NotificationPreferences>) => {
    const targetUserId = userId || customerId
    if (!targetUserId) return

    const updatedPreferences = { ...preferences, ...newPreferences }
    setPreferences(updatedPreferences)
    localStorage.setItem(`notification_prefs_${targetUserId}`, JSON.stringify(updatedPreferences))
  }

  const getNotificationsByType = (type: Notification['type']) => {
    return notifications.filter(n => n.type === type)
  }

  const getUnreadNotifications = () => {
    return notifications.filter(n => !n.is_read)
  }

  return {
    notifications,
    unreadCount,
    preferences,
    markAsRead,
    markAllAsRead,
    addNotification,
    removeNotification,
    clearAllNotifications,
    updatePreferences,
    getNotificationsByType,
    getUnreadNotifications
  }
}

// Funções auxiliares para criar notificações específicas
export const createOrderNotification = (orderId: string, total: number, customerName: string): Omit<Notification, 'id' | 'created_at' | 'is_read'> => {
  return {
    type: 'order_status_changed',
    title: 'Novo Pedido',
    message: `Pedido #${orderId} de ${customerName} - R$ ${total.toFixed(2)}`,
    userId: 'system',
    actionUrl: `/orders/${orderId}`,
    icon: '📦'
  }
}

export const createStockNotification = (productName: string, currentStock: number): Omit<Notification, 'id' | 'created_at' | 'is_read'> => {
  return {
    type: 'product_low_stock',
    title: 'Estoque Baixo',
    message: `${productName} - apenas ${currentStock} unidades restantes`,
    userId: 'system',
    actionUrl: '/products',
    icon: '📊'
  }
}

export const createPaymentNotification = (orderId: string, status: 'approved' | 'rejected'): Omit<Notification, 'id' | 'created_at' | 'is_read'> => {
  return {
    type: 'payment_confirmed',
    title: status === 'approved' ? 'Pagamento Aprovado' : 'Pagamento Rejeitado',
    message: `Pagamento do pedido #${orderId} ${status === 'approved' ? 'aprovado' : 'rejeitado'}`,
    userId: 'system',
    actionUrl: `/orders/${orderId}`,
    icon: status === 'approved' ? '✅' : '❌'
  }
}

export const createSystemNotification = (title: string, message: string): Omit<Notification, 'id' | 'created_at' | 'is_read'> => {
  return {
    type: 'production_needed',
    title,
    message,
    userId: 'system',
    icon: '⚙️'
  }
}