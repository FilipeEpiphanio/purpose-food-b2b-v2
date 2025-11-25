import express from 'express';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase with static config for production
const supabaseUrl = 'https://xqsocdvvvbgdgrezoqlf.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhxc29jZHZ2dmJnZGdyZXpvcWxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzYwNjAsImV4cCI6MjA3ODY1MjA2MH0.ZY-Flx5BoBI3vnSS_PfuxaWHpQEOeLSL8By8QVtGtEw';

const supabase = createClient(supabaseUrl, supabaseKey);

const router = express.Router();

// Get all products
router.get('/', async (req, res) => {
  try {
    const { data: products, error } = await supabase
      .from('products')
      .select('*')
      .order('name', { ascending: true });

    if (error) {
      console.error('Error fetching products:', error);
      return res.status(500).json({ 
        success: false, 
        error: 'Erro ao buscar produtos',
        details: error.message 
      });
    }

    // Processar produtos para converter ingredients de string JSON para array quando necessário
    const processedProducts = (products || []).map(product => {
      if (product.ingredients && typeof product.ingredients === 'string') {
        try {
          product.ingredients = JSON.parse(product.ingredients);
        } catch (e) {
          console.warn('Erro ao fazer parse dos ingredients:', e);
          product.ingredients = [];
        }
      }
      return product;
    });

    res.json({
      success: true,
      products: processedProducts,
      count: processedProducts.length
    });
  } catch (error) {
    console.error('Exception fetching products:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Erro ao buscar produtos',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get single product
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const { data: product, error } = await supabase
      .from('products')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('Error fetching product:', error);
      return res.status(404).json({ 
        success: false, 
        error: 'Produto não encontrado',
        details: error.message 
      });
    }

    // Processar ingredients de string JSON para array quando necessário
    if (product.ingredients && typeof product.ingredients === 'string') {
      try {
        product.ingredients = JSON.parse(product.ingredients);
      } catch (e) {
        console.warn('Erro ao fazer parse dos ingredients:', e);
        product.ingredients = [];
      }
    }

    res.json({
      success: true,
      product
    });
  } catch (error) {
    console.error('Exception fetching product:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Erro ao buscar produto',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Create product
router.post('/', async (req, res) => {
  try {
    const productData = req.body;
    
    // Validate required fields
    if (!productData.name || !productData.category || !productData.price) {
      return res.status(400).json({ 
        success: false, 
        error: 'Nome, categoria e preço são obrigatórios' 
      });
    }

    // Preparar dados do produto
    const insertData = {
      ...productData,
      stock: productData.stock || 0,
      min_stock: productData.min_stock || 0,
      status: productData.status || 'active',
      unit: productData.unit || 'unidade'
    };

    const { data: product, error } = await supabase
      .from('products')
      .insert([insertData])
      .select()
      .single();

    if (error) {
      console.error('Error creating product:', error);
      return res.status(500).json({ 
        success: false, 
        error: 'Erro ao criar produto',
        details: error.message 
      });
    }

    res.json({ 
      success: true, 
      product,
      message: 'Produto criado com sucesso'
    });
  } catch (error) {
    console.error('Exception creating product:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Erro ao criar produto',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Update product
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;

    // Preparar dados para atualização
    const updateFields = {
      ...updateData,
      updated_at: new Date().toISOString()
    };

    const { data: product, error } = await supabase
      .from('products')
      .update(updateFields)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating product:', error);
      return res.status(500).json({ 
        success: false, 
        error: 'Erro ao atualizar produto',
        details: error.message 
      });
    }

    if (!product) {
      return res.status(404).json({ 
        success: false, 
        error: 'Produto não encontrado'
      });
    }

    res.json({ 
      success: true, 
      product,
      message: 'Produto atualizado com sucesso'
    });
  } catch (error) {
    console.error('Exception updating product:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Erro ao atualizar produto',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Delete product
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const { error } = await supabase
      .from('products')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting product:', error);
      return res.status(500).json({ 
        success: false, 
        error: 'Erro ao excluir produto',
        details: error.message 
      });
    }

    res.json({ 
      success: true, 
      message: 'Produto excluído com sucesso'
    });
  } catch (error) {
    console.error('Exception deleting product:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Erro ao excluir produto',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;