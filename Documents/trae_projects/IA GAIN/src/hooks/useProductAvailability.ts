import { useState, useCallback, useEffect } from 'react';
import { supabase } from '../lib/supabase';

interface ProductAvailability {
  id: string;
  name: string;
  stock: number;
  minStock: number;
  preparationTime: number;
  isActive: boolean;
}

interface AvailabilityNotification {
  id: string;
  productId: string;
  type: 'inactive' | 'out-of-stock' | 'low-stock' | 'preparation' | 'available';
  message: string;
  timestamp: Date;
}

export const useProductAvailability = () => {
  const [notifications, setNotifications] = useState<AvailabilityNotification[]>([]);
  const [subscribedProducts, setSubscribedProducts] = useState<Set<string>>(new Set());

  const checkProductAvailability = useCallback((product: ProductAvailability): AvailabilityNotification | null => {
    if (!product.isActive) {
      return {
        id: `${product.id}-inactive`,
        productId: product.id,
        type: 'inactive',
        message: 'Este produto não está disponível no momento',
        timestamp: new Date()
      };
    }

    if (product.stock <= 0) {
      return {
        id: `${product.id}-out-of-stock`,
        productId: product.id,
        type: 'out-of-stock',
        message: `Este produto está em produção. Tempo estimado: ${product.preparationTime}h`,
        timestamp: new Date()
      };
    }

    if (product.stock <= product.minStock) {
      return {
        id: `${product.id}-low-stock`,
        productId: product.id,
        type: 'low-stock',
        message: `Apenas ${product.stock} unidades disponíveis. Pedido pode levar ${product.preparationTime}h para preparo`,
        timestamp: new Date()
      };
    }

    if (product.preparationTime > 0) {
      return {
        id: `${product.id}-preparation`,
        productId: product.id,
        type: 'preparation',
        message: `Produto disponível! Tempo de preparo: ${product.preparationTime}h`,
        timestamp: new Date()
      };
    }

    return {
      id: `${product.id}-available`,
      productId: product.id,
      type: 'available',
      message: 'Produto em estoque e pronto para entrega',
      timestamp: new Date()
    };
  }, []);

  const showNotification = useCallback((product: ProductAvailability) => {
    const notification = checkProductAvailability(product);
    if (notification) {
      setNotifications(prev => {
        const filtered = prev.filter(n => n.productId !== product.id);
        return [...filtered, notification];
      });
    }
  }, [checkProductAvailability]);

  const removeNotification = useCallback((notificationId: string) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  }, []);

  const subscribeToProduct = useCallback((productId: string) => {
    setSubscribedProducts(prev => new Set([...prev, productId]));
  }, []);

  const unsubscribeFromProduct = useCallback((productId: string) => {
    setSubscribedProducts(prev => {
      const newSet = new Set(prev);
      newSet.delete(productId);
      return newSet;
    });
    setNotifications(prev => prev.filter(n => n.productId !== productId));
  }, []);

  // Monitorar mudanças em tempo real nos produtos inscritos
  useEffect(() => {
    if (subscribedProducts.size === 0) return;

    const subscription = supabase
      .channel('product-availability-changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'products',
        filter: `id=in.(${Array.from(subscribedProducts).join(',')})`
      }, (payload) => {
        const product = payload.new as ProductAvailability;
        if (product) {
          showNotification(product);
        }
      })
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [subscribedProducts, showNotification]);

  return {
    notifications,
    showNotification,
    removeNotification,
    subscribeToProduct,
    unsubscribeFromProduct
  };
};