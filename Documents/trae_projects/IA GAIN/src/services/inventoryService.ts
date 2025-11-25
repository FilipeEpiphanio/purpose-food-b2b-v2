/**
 * Serviço de gestão de estoque e disponibilidade de produtos
 */
export class InventoryService {
  private stockCache: Map<string, number> = new Map();
  private minStockCache: Map<string, number> = new Map();

  constructor() {
    this.initializeInventory();
  }

  private initializeInventory() {
    // Inicializar com dados simulados
    this.stockCache.set('product-1', 10);
    this.stockCache.set('product-2', 5);
    this.stockCache.set('product-3', 20);
    
    this.minStockCache.set('product-1', 3);
    this.minStockCache.set('product-2', 2);
    this.minStockCache.set('product-3', 5);
  }

  /**
   * Verifica disponibilidade de produto considerando estoque e tempo de produção
   */
  async checkProductAvailability(
    productId: string, 
    requestedQuantity: number
  ): Promise<{
    available: boolean;
    currentStock: number;
    productionTime: number;
    message: string;
  }> {
    const currentStock = this.stockCache.get(productId) || 0;
    const productData = await this.getProductData(productId);
    
    if (currentStock >= requestedQuantity) {
      return {
        available: true,
        currentStock,
        productionTime: 0,
        message: 'Disponível para pronta entrega'
      };
    } else {
      const productionTime = productData?.preparation_time || 2.5;
      return {
        available: false,
        currentStock,
        productionTime,
        message: `Aguardar ${productionTime}h de produção`
      };
    }
  }

  /**
   * Consome estoque após confirmação de pedido
   */
  async consumeStock(
    productId: string, 
    quantity: number
  ): Promise<{
    success: boolean;
    newStock: number;
    message: string;
  }> {
    const currentStock = this.stockCache.get(productId) || 0;
    
    if (currentStock >= quantity) {
      const newStock = currentStock - quantity;
      this.stockCache.set(productId, newStock);
      
      // Verificar se precisa de alerta de reposição
      const minStock = this.minStockCache.get(productId) || 0;
      if (newStock <= minStock) {
        this.notifyLowStock(productId, newStock, minStock);
      }
      
      return {
        success: true,
        newStock,
        message: 'Estoque consumido com sucesso'
      };
    } else {
      return {
        success: false,
        newStock: currentStock,
        message: 'Estoque insuficiente'
      };
    }
  }

  /**
   * Verifica necessidade de produção para pedido grande
   */
  async getProductionNotification(
    productId: string, 
    requestedQuantity: number
  ): Promise<{
    requiresProduction: boolean;
    productionTime: number;
    message: string;
  }> {
    const availability = await this.checkProductAvailability(productId, requestedQuantity);
    
    if (!availability.available) {
      return {
        requiresProduction: true,
        productionTime: availability.productionTime,
        message: `Necessário produzir por ${availability.productionTime} horas`
      };
    }
    
    return {
      requiresProduction: false,
      productionTime: 0,
      message: 'Disponível em estoque'
    };
  }

  /**
   * Verifica alertas de estoque baixo
   */
  async checkLowStock(productId: string): Promise<{
    isLowStock: boolean;
    currentStock: number;
    minStock: number;
    alertMessage: string;
  }> {
    const currentStock = this.stockCache.get(productId) || 0;
    const minStock = this.minStockCache.get(productId) || 0;
    
    const isLowStock = currentStock <= minStock;
    
    return {
      isLowStock,
      currentStock,
      minStock,
      alertMessage: isLowStock 
        ? `Estoque baixo: ${currentStock} unidades (mínimo: ${minStock})`
        : 'Estoque normal'
    };
  }

  /**
   * Valida dados do produto
   */
  async validateProductData(productData: any): Promise<{
    isValid: boolean;
    errors: string[];
  }> {
    const errors: string[] = [];
    
    if (!productData.name || productData.name.trim().length === 0) {
      errors.push('Nome do produto é obrigatório');
    }
    
    if (productData.price < 0) {
      errors.push('Preço não pode ser negativo');
    }
    
    if (productData.stock < 0) {
      errors.push('Estoque não pode ser negativo');
    }
    
    if (productData.preparation_time < 0) {
      errors.push('Tempo de preparo não pode ser negativo');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Obtém dados do produto (simulado)
   */
  private async getProductData(productId: string): Promise<any> {
    // Em produção, buscaria do banco de dados
    return {
      id: productId,
      name: 'Produto Exemplo',
      preparation_time: 2.5,
      is_active: true
    };
  }

  /**
   * Notifica sobre estoque baixo
   */
  private notifyLowStock(productId: string, currentStock: number, minStock: number) {
    console.log(`⚠️ ALERTA: Estoque baixo para ${productId}`);
    console.log(`Estoque atual: ${currentStock}, Mínimo: ${minStock}`);
    
    // Aqui integraria com sistema de notificações do gerencial
  }

  /**
   * Atualiza estoque manualmente (para testes)
   */
  updateStock(productId: string, newStock: number) {
    this.stockCache.set(productId, newStock);
    console.log(`Estoque atualizado: ${productId} = ${newStock}`);
  }

  /**
   * Define estoque mínimo
   */
  setMinStock(productId: string, minStock: number) {
    this.minStockCache.set(productId, minStock);
    console.log(`Estoque mínimo definido: ${productId} = ${minStock}`);
  }
}

export const inventoryService = new InventoryService();