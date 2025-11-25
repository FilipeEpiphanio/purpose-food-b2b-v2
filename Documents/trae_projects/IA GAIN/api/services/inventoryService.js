import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

/**
 * Atualiza o estoque após um pedido
 * @param {string} orderId - ID do pedido
 * @param {Array} items - Itens do pedido
 * @returns {Promise<Object>} Resultado da atualização
 */
export const updateInventoryAfterOrder = async (orderId, items) => {
  try {
    const updates = [];
    const notifications = [];

    for (const item of items) {
      // Buscar produto atual
      const { data: product, error: productError } = await supabase
        .from('products')
        .select('id, name, stock_current, stock_minimum, preparation_time, is_active')
        .eq('id', item.product_id)
        .single();

      if (productError) {
        console.error(`Erro ao buscar produto ${item.product_id}:`, productError);
        continue;
      }

      if (!product) {
        console.error(`Produto ${item.product_id} não encontrado`);
        continue;
      }

      // Calcular novo estoque
      const newStock = product.stock_current - item.quantity;
      
      // Atualizar estoque
      const { error: updateError } = await supabase
        .from('products')
        .update({ 
          stock_current: newStock,
          updated_at: new Date().toISOString()
        })
        .eq('id', item.product_id);

      if (updateError) {
        console.error(`Erro ao atualizar estoque do produto ${item.product_id}:`, updateError);
        continue;
      }

      // Verificar se precisa de notificação de produção
      if (newStock <= 0) {
        notifications.push({
          type: 'production_needed',
          product_id: product.id,
          product_name: product.name,
          current_stock: newStock,
          preparation_time: product.preparation_time,
          message: `Produto ${product.name} esgotado. Tempo de produção: ${product.preparation_time}h`
        });
      } else if (newStock <= product.stock_minimum) {
        notifications.push({
          type: 'low_stock',
          product_id: product.id,
          product_name: product.name,
          current_stock: newStock,
          minimum_stock: product.stock_minimum,
          message: `Estoque baixo para ${product.name}: ${newStock} unidades restantes`
        });
      }

      updates.push({
        product_id: item.product_id,
        previous_stock: product.stock_current,
        new_stock: newStock,
        quantity_ordered: item.quantity
      });
    }

    // Criar notificações no banco
    if (notifications.length > 0) {
      const { error: notificationError } = await supabase
        .from('notifications')
        .insert(notifications.map(notif => ({
          type: notif.type,
          title: notif.type === 'production_needed' ? 'Produção Necessária' : 'Estoque Baixo',
          message: notif.message,
          data: {
            product_id: notif.product_id,
            product_name: notif.product_name,
            current_stock: notif.current_stock,
            preparation_time: notif.preparation_time
          },
          is_read: false,
          created_at: new Date().toISOString()
        })));

      if (notificationError) {
        console.error('Erro ao criar notificações:', notificationError);
      }
    }

    return {
      success: true,
      updates,
      notifications,
      orderId
    };

  } catch (error) {
    console.error('Erro ao atualizar inventário:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * Verifica disponibilidade de produtos para pedido
 * @param {Array} items - Itens do pedido
 * @returns {Promise<Object>} Disponibilidade e tempos de produção
 */
export const checkProductAvailability = async (items) => {
  try {
    const availability = [];
    let totalProductionTime = 0;
    let hasOutOfStock = false;
    let hasLowStock = false;

    for (const item of items) {
      const { data: product, error } = await supabase
        .from('products')
        .select('id, name, stock_current, stock_minimum, preparation_time, is_active')
        .eq('id', item.product_id)
        .single();

      if (error) {
        availability.push({
          product_id: item.product_id,
          available: false,
          message: 'Erro ao verificar produto',
          error: error.message
        });
        continue;
      }

      if (!product || !product.is_active) {
        availability.push({
          product_id: item.product_id,
          product_name: product?.name || 'Produto não encontrado',
          available: false,
          message: 'Produto indisponível',
          stock_current: 0,
          preparation_time: product?.preparation_time || 0
        });
        hasOutOfStock = true;
        continue;
      }

      const availableStock = product.stock_current;
      const requestedQuantity = item.quantity;

      if (availableStock >= requestedQuantity) {
        // Estoque suficiente - pronta entrega
        availability.push({
          product_id: product.id,
          product_name: product.name,
          available: true,
          message: 'Pronta entrega',
          stock_current: availableStock,
          preparation_time: 0,
          delivery_type: 'immediate'
        });
      } else if (availableStock > 0) {
        // Estoque parcial - parte pronta, parte precisa produzir
        const immediateQuantity = availableStock;
        const productionQuantity = requestedQuantity - availableStock;
        
        availability.push({
          product_id: product.id,
          product_name: product.name,
          available: true,
          message: `${immediateQuantity} unidade(s) pronta(s), ${productionQuantity} precisa(em) produção`,
          stock_current: availableStock,
          preparation_time: product.preparation_time,
          delivery_type: 'partial',
          immediate_quantity: immediateQuantity,
          production_quantity: productionQuantity
        });
        
        if (product.preparation_time > totalProductionTime) {
          totalProductionTime = product.preparation_time;
        }
        hasLowStock = true;
      } else {
        // Sem estoque - precisa produzir tudo
        availability.push({
          product_id: product.id,
          product_name: product.name,
          available: true,
          message: `Sem estoque. Tempo de produção: ${product.preparation_time}h`,
          stock_current: 0,
          preparation_time: product.preparation_time,
          delivery_type: 'production'
        });
        
        if (product.preparation_time > totalProductionTime) {
          totalProductionTime = product.preparation_time;
        }
        hasOutOfStock = true;
      }
    }

    // Calcular tempo total estimado
    let deliveryEstimate = '30-60 minutos'; // Padrão para pronta entrega
    
    if (hasOutOfStock || hasLowStock) {
      if (totalProductionTime <= 2) {
        deliveryEstimate = `${totalProductionTime}h - ${totalProductionTime + 1}h`;
      } else if (totalProductionTime <= 4) {
        deliveryEstimate = `${totalProductionTime}h - ${totalProductionTime + 2}h`;
      } else {
        deliveryEstimate = `${totalProductionTime}h - ${totalProductionTime + 4}h`;
      }
    }

    return {
      success: true,
      availability,
      delivery_estimate: deliveryEstimate,
      total_production_time: totalProductionTime,
      has_out_of_stock: hasOutOfStock,
      has_low_stock: hasLowStock,
      can_proceed: !hasOutOfStock // Só impede se tiver produto inativo
    };

  } catch (error) {
    console.error('Erro ao verificar disponibilidade:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * Atualiza produto no gerencial e notifica mudanças
 * @param {string} productId - ID do produto
 * @param {Object} updates - Campos a atualizar
 * @returns {Promise<Object>} Resultado da atualização
 */
export const updateProductAndNotify = async (productId, updates) => {
  try {
    // Atualizar produto
    const { data, error } = await supabase
      .from('products')
      .update({
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', productId)
      .select()
      .single();

    if (error) throw error;

    // Criar notificação de mudança
    const changes = Object.keys(updates).filter(key => key !== 'updated_at');
    
    if (changes.length > 0) {
      await supabase.from('notifications').insert([{
        type: 'product_updated',
        title: 'Produto Atualizado',
        message: `O produto ${data.name} foi atualizado: ${changes.join(', ')}`,
        data: {
          product_id: productId,
          product_name: data.name,
          changes: changes,
          updates: updates
        },
        is_read: false,
        created_at: new Date().toISOString()
      }]);
    }

    return {
      success: true,
      product: data
    };

  } catch (error) {
    console.error('Erro ao atualizar produto:', error);
    return {
      success: false,
      error: error.message
    };
  }
};