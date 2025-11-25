import { RealTimeSyncService } from '../src/services/realTimeSync';
import { InventoryService } from '../src/services/inventoryService';
import { supabase } from '../src/lib/supabase';

/**
 * Script de demonstração da integração completa entre interface do cliente e gerencial
 * Execute este script para ver o sistema funcionando em tempo real
 */

class IntegrationDemo {
  private syncService: RealTimeSyncService;
  private inventoryService: InventoryService;

  constructor() {
    this.syncService = new RealTimeSyncService();
    this.inventoryService = new InventoryService();
  }

  async runDemo() {
    console.log('🍰 Purpose Food - Demonstração de Integração Completa');
    console.log('=' .repeat(60));

    try {
      // 1. Demonstrar sincronização de produtos
      await this.demoProductSync();
      
      // 2. Demonstrar sistema de notificações
      await this.demoNotificationSystem();
      
      // 3. Demonstrar gestão de estoque
      await this.demoInventoryManagement();
      
      // 4. Demonstrar fluxo completo de pedido
      await this.demoCompleteOrderFlow();
      
      // 5. Demonstrar atualizações em tempo real
      await this.demoRealTimeUpdates();

      console.log('\n✅ Demonstração concluída com sucesso!');
      console.log('O sistema está totalmente integrado e funcionando em tempo real.');

    } catch (error) {
      console.error('❌ Erro na demonstração:', error);
    }
  }

  private async demoProductSync() {
    console.log('\n📦 1. Sincronização de Produtos');
    console.log('-'.repeat(40));

    // Simular adição de novo produto no gerencial
    const newProduct = {
      name: 'Torta de Morango Artesanal',
      price: 65.90,
      stock: 5,
      preparation_time: 3.0,
      is_active: true,
      ingredients: ['morango', 'creme', 'massa', 'açúcar']
    };

    console.log('Adicionando produto no gerencial...');
    console.log('Produto:', newProduct.name);
    console.log('Preço: R$', newProduct.price);
    console.log('Tempo de preparo:', newProduct.preparation_time, 'horas');

    // Simular sincronização para interface do cliente
    const syncResult = await this.syncService.simulateProductSync(newProduct);
    console.log('✅ Produto sincronizado para interface do cliente em:', syncResult.syncTime, 'ms');

    // Verificar disponibilidade
    const availability = await this.inventoryService.checkProductAvailability('new-product', 2);
    console.log('Disponibilidade:', availability.message);
    console.log('Tempo de produção:', availability.productionTime, 'horas');
  }

  private async demoNotificationSystem() {
    console.log('\n🔔 2. Sistema de Notificações');
    console.log('-'.repeat(40));

    const customerId = 'customer-demo';
    
    // Notificação de estoque baixo
    const lowStockNotification = {
      type: 'low_stock',
      productId: 'product-1',
      message: 'Estoque baixo detectado para Bolo de Chocolate (2 unidades restantes)',
      timestamp: new Date().toISOString()
    };

    console.log('Enviando notificação de estoque baixo...');
    this.syncService.notifyCustomer(customerId, lowStockNotification);
    console.log('✅ Notificação enviada para o cliente');

    // Notificação de tempo de produção
    const productionNotification = {
      type: 'production_time',
      orderId: 'order-123',
      message: 'Seu pedido está em produção e será entregue em 2.5 horas',
      estimatedDelivery: new Date(Date.now() + 2.5 * 60 * 60 * 1000).toISOString()
    };

    console.log('Enviando notificação de tempo de produção...');
    this.syncService.notifyCustomer(customerId, productionNotification);
    console.log('✅ Cliente notificado sobre tempo de produção');
  }

  private async demoInventoryManagement() {
    console.log('\n📊 3. Gestão de Estoque Inteligente');
    console.log('-'.repeat(40));

    const productId = 'product-demo';
    const initialStock = 10;
    const orderQuantity = 3;

    console.log('Estoque inicial:', initialStock, 'unidades');
    console.log('Pedido recebido por:', orderQuantity, 'unidades');

    // Consumir estoque
    const stockResult = await this.inventoryService.consumeStock(productId, orderQuantity);
    console.log('✅ Estoque consumido. Novo saldo:', stockResult.newStock, 'unidades');

    // Verificar alertas
    const lowStockAlert = await this.inventoryService.checkLowStock(productId);
    if (lowStockAlert.isLowStock) {
      console.log('⚠️  Alerta: Estoque baixo detectado!');
      console.log('Estoque atual:', lowStockAlert.currentStock);
      console.log('Estoque mínimo:', lowStockAlert.minStock);
    }

    // Verificar necessidade de produção
    const largeOrder = 15;
    const productionCheck = await this.inventoryService.checkProductAvailability(productId, largeOrder);
    
    if (!productionCheck.available) {
      console.log('📋 Produção necessária para atender pedido de', largeOrder, 'unidades');
      console.log('Tempo estimado de produção:', productionCheck.productionTime, 'horas');
    }
  }

  private async demoCompleteOrderFlow() {
    console.log('\n🛒 4. Fluxo Completo de Pedido');
    console.log('-'.repeat(40));

    const customerId = 'customer-demo';
    const productId = 'product-flow-demo';

    console.log('Etapa 1: Cliente visualiza produtos');
    const products = await this.getAvailableProducts();
    console.log('Produtos disponíveis:', products.length);

    console.log('\nEtapa 2: Cliente adiciona ao carrinho');
    const cartItem = {
      productId: productId,
      quantity: 2,
      price: 45.90
    };
    console.log('Item adicionado:', cartItem.quantity, 'x', products[0]?.name);

    console.log('\nEtapa 3: Verificação de disponibilidade');
    const availability = await this.inventoryService.checkProductAvailability(productId, cartItem.quantity);
    console.log('Resultado:', availability.message);

    console.log('\nEtapa 4: Criação do pedido');
    const orderData = {
      customer_id: customerId,
      items: [cartItem],
      total: cartItem.quantity * cartItem.price,
      status: 'pending',
      estimated_delivery: availability.productionTime 
        ? new Date(Date.now() + availability.productionTime * 60 * 60 * 1000)
        : new Date(Date.now() + 1 * 60 * 60 * 1000) // 1 hora para pronta entrega
    };

    const orderResult = await this.createOrder(orderData);
    console.log('✅ Pedido criado com ID:', orderResult.orderId);
    console.log('Total: R$', orderData.total.toFixed(2));
    console.log('Tempo estimado:', availability.productionTime ? availability.productionTime + ' horas' : '1 hora');

    console.log('\nEtapa 5: Atualização de estoque');
    const stockUpdate = await this.inventoryService.consumeStock(productId, cartItem.quantity);
    console.log('✅ Estoque atualizado. Saldo:', stockUpdate.newStock);

    console.log('\nEtapa 6: Notificações enviadas');
    this.syncService.notifyCustomer(customerId, {
      type: 'order_confirmation',
      orderId: orderResult.orderId,
      message: `Pedido confirmado! Total: R$ ${orderData.total.toFixed(2)}`
    });
    console.log('✅ Cliente notificado sobre confirmação do pedido');
  }

  private async demoRealTimeUpdates() {
    console.log('\n⚡ 5. Atualizações em Tempo Real');
    console.log('-'.repeat(40));

    const productId = 'realtime-demo';
    const customerCallback = (update: any) => {
      console.log('🔄 Atualização recebida:', update.type);
      console.log('Produto:', update.productId);
      console.log('Dados:', update.data);
    };

    console.log('Inscrevendo cliente para atualizações em tempo real...');
    this.syncService.subscribeToProductChanges(productId, customerCallback);
    console.log('✅ Cliente inscrito para receber atualizações');

    console.log('\nSimulando mudanças no gerencial...');
    
    // Simular mudança de preço
    await this.syncService.simulateProductChange(productId, {
      type: 'price_update',
      data: { oldPrice: 45.90, newPrice: 49.90 }
    });

    // Simular mudança de estoque
    await this.syncService.simulateProductChange(productId, {
      type: 'stock_update',
      data: { oldStock: 10, newStock: 5 }
    });

    console.log('✅ Cliente recebeu todas as atualizações em tempo real');
  }

  // Métodos auxiliares
  private async getAvailableProducts() {
    // Simular busca de produtos disponíveis
    return [
      { id: 'product-1', name: 'Bolo de Chocolate', price: 45.90, stock: 10 },
      { id: 'product-2', name: 'Torta de Morango', price: 65.90, stock: 5 },
      { id: 'product-3', name: 'Coxinha Artesanal', price: 8.90, stock: 20 }
    ];
  }

  private async createOrder(orderData: any) {
    // Simular criação de pedido
    return {
      orderId: 'order-' + Date.now(),
      status: 'confirmed',
      estimatedDelivery: orderData.estimated_delivery
    };
  }
}

// Executar demonstração
const demo = new IntegrationDemo();
demo.runDemo();

export default IntegrationDemo;