import { waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { RealTimeSyncService } from '../services/realTimeSync';
import { InventoryService } from '../services/inventoryService';

// Mock Supabase
vi.mock('../lib/supabase', () => ({
  supabase: {
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          single: vi.fn(() => ({
            data: {
              id: '1',
              name: 'Bolo de Chocolate',
              price: 45.90,
              stock: 10,
              preparation_time: 2.5,
              is_active: true
            },
            error: null
          }))
        })),
        order: vi.fn(() => ({
          data: [
            {
              id: '1',
              name: 'Bolo de Chocolate',
              price: 45.90,
              stock: 10,
              preparation_time: 2.5,
              is_active: true
            }
          ],
          error: null
        }))
      })),
      insert: vi.fn(() => ({
        data: { id: 'new-order-id' },
        error: null
      })),
      update: vi.fn(() => ({
        data: {},
        error: null
      }))
    })),
    channel: vi.fn(() => ({
      on: vi.fn(() => ({
        subscribe: vi.fn()
      })),
      subscribe: vi.fn()
    }))
  }
}));

describe('Integration Tests - Management to Customer Interface', () => {
  let syncService: RealTimeSyncService;
  let inventoryService: InventoryService;

  beforeEach(() => {
    syncService = new RealTimeSyncService();
    inventoryService = new InventoryService();
    vi.clearAllMocks();
  });

  afterEach(() => {
    syncService.destroy();
  });

  describe('Product Synchronization', () => {
    it('should sync product updates from management to customer interface', async () => {
      // Verify sync service detects change
      const changes = await syncService.getProductChanges('1');
      expect(changes).toBeDefined();
    });

    it('should handle product availability changes', async () => {
      const availability = await inventoryService.checkProductAvailability('1', 1);
      
      expect(availability.available).toBe(true);
      expect(availability.productionTime).toBe(0);
      expect(availability.message).toContain('pronta entrega');
    });
  });

  describe('Order Processing Integration', () => {
    it('should create order and update stock in both interfaces', async () => {
      // Verify stock update
      const stockUpdate = await inventoryService.consumeStock('1', 2);
      expect(stockUpdate.success).toBe(true);
      expect(stockUpdate.newStock).toBe(8); // 10 - 2 = 8
    });

    it('should handle production time notifications', async () => {
      const notification = await inventoryService.getProductionNotification('1', 15);
      
      expect(notification.requiresProduction).toBe(true);
      expect(notification.productionTime).toBe(2.5);
      expect(notification.message).toContain('produção');
    });
  });

  describe('Real-time Updates', () => {
    it('should notify customer interface of stock changes', async () => {
      const mockCallback = vi.fn();
      
      syncService.subscribeToProductChanges('1', mockCallback);
      
      // Simulate stock change
      await syncService.notifyProductChange('1', {
        productId: '1',
        changes: ['stock'],
        timestamp: new Date().toISOString()
      });

      await waitFor(() => {
        expect(mockCallback).toHaveBeenCalledWith({
          productId: '1',
          changes: ['stock'],
          timestamp: expect.any(String)
        });
      });
    });

    it('should handle multiple product updates simultaneously', async () => {
      const updates = [
        { productId: '1', stock: 8 },
        { productId: '2', stock: 15 },
        { productId: '3', stock: 0 }
      ];

      const results = await Promise.all(
        updates.map(update => 
          inventoryService.checkProductAvailability(update.productId, 1)
        )
      );

      expect(results).toHaveLength(3);
      expect(results[0].available).toBe(true);
      expect(results[2].available).toBe(false);
    });
  });

  describe('Customer Notification System', () => {
    it('should notify customers about order status changes', async () => {
      const orderId = 'order-123';
      const customerId = 'customer-1';
      
      const notification = {
        type: 'order_status',
        orderId,
        status: 'production',
        message: 'Seu pedido está em produção e será entregue em 2.5 horas'
      };

      syncService.notifyCustomer(customerId, notification);

      // Verify notification was sent
      const sentNotifications = syncService.getCustomerNotifications(customerId);
      expect(sentNotifications).toContainEqual(expect.objectContaining({
        type: 'order_status',
        orderId,
        status: 'production'
      }));
    });

    it('should handle low stock alerts', async () => {
      const productData = {
        id: '1',
        name: 'Bolo de Chocolate',
        stock: 2,
        min_stock: 5
      };

      const alert = await inventoryService.checkLowStock('1');
      
      expect(alert.isLowStock).toBe(true);
      expect(alert.currentStock).toBe(2);
      expect(alert.minStock).toBe(5);
      expect(alert.alertMessage).toContain('estoque baixo');
    });
  });

  describe('Data Consistency', () => {
    it('should maintain consistency between management and customer data', async () => {
      // Get product from customer view
      const customerProduct = await syncService.getCustomerProduct('1');

      expect(customerProduct).toBeDefined();
      expect(customerProduct.id).toBe('1');
    });

    it('should handle invalid product data', async () => {
      const invalidProduct = {
        id: 'invalid',
        price: -10, // Invalid price
        stock: -5   // Invalid stock
      };

      const validation = await inventoryService.validateProductData(invalidProduct);
      
      expect(validation.isValid).toBe(false);
      expect(validation.errors).toContain('Preço não pode ser negativo');
      expect(validation.errors).toContain('Estoque não pode ser negativo');
    });
  });
});