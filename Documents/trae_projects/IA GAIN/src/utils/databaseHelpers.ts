/**
 * Helpers para verificação de estrutura do banco de dados
 */
import { supabase } from '../lib/supabase';

/**
 * Verifica se uma coluna existe em uma tabela antes de usar em queries
 * Retorna true se a coluna existir ou se não conseguir verificar
 */
export const checkColumnExists = async (tableName: string, columnName: string): Promise<boolean> => {
  try {
    // Verificar se a coluna existe na tabela
    const { data, error } = await supabase
      .from(tableName)
      .select(columnName)
      .limit(1);

    if (error) {
      // Se o erro for relacionado à coluna não existir
      if (error.message.includes('column') && error.message.includes('does not exist')) {
        return false;
      }
      // Para outros erros, assumimos que a coluna existe para não quebrar a aplicação
      return true;
    }

    return true;
  } catch (error) {
    console.warn(`Não foi possível verificar se a coluna ${columnName} existe na tabela ${tableName}:`, error);
    return true; // Assume que existe para não quebrar a aplicação
  }
};

/**
 * Carrega produtos com fallback para quando a coluna is_active não existe
 */
export const loadProductsWithFallback = async (supabase: any, options: any = {}) => {
  try {
    // Primeiro tentar com a coluna is_active
    let query = supabase
      .from('products')
      .select('*');

    // Verificar se is_active existe antes de aplicar o filtro
    const hasActiveColumn = await checkColumnExists('products', 'is_active');
    
    if (hasActiveColumn && options.onlyActive !== false) {
      query = query.eq('is_active', true);
    }

    // Aplicar ordenação
    if (options.orderBy) {
      query = query.order(options.orderBy, { ascending: options.ascending !== false });
    }

    // Aplicar limite
    if (options.limit) {
      query = query.limit(options.limit);
    }

    const { data, error } = await query;

    if (error) throw error;
    return { data: data || [], error: null };
    
  } catch (error: any) {
    // Se o erro for relacionado à coluna is_active não existir
    if (error.message?.includes('is_active') && error.message?.includes('does not exist')) {
      console.warn('Coluna is_active não encontrada, carregando todos os produtos...');
      
      // Fallback: carregar todos os produtos sem filtro de ativo
      let fallbackQuery = supabase
        .from('products')
        .select('*');

      if (options.orderBy) {
        fallbackQuery = fallbackQuery.order(options.orderBy, { ascending: options.ascending !== false });
      }

      if (options.limit) {
        fallbackQuery = fallbackQuery.limit(options.limit);
      }

      const { data, error: fallbackError } = await fallbackQuery;
      
      if (fallbackError) throw fallbackError;
      return { data: data || [], error: null };
    }
    
    throw error;
  }
};