import express from 'express';
import { supabase } from '../server';

const router = express.Router();

// Get all customers
router.get('/', async (req, res) => {
  try {
    const { data: customers, error } = await supabase
      .from('customers')
      .select('*')
      .order('name', { ascending: true });

    if (error) {
      console.error('Erro ao buscar clientes:', error);
      return res.status(500).json({ error: 'Erro ao buscar clientes' });
    }

    // Calculate customer statistics from orders
    const customersWithStats = await Promise.all(
      customers.map(async (customer) => {
        const { data: orders, error: ordersError } = await supabase
          .from('orders')
          .select('total_amount, created_at')
          .eq('customer_id', customer.id);

        if (ordersError) {
          console.error(`Erro ao buscar pedidos do cliente ${customer.id}:`, ordersError);
          return {
            ...customer,
            totalOrders: 0,
            totalSpent: 0,
            lastOrderDate: null
          };
        }

        const totalOrders = orders.length;
        const totalSpent = orders.reduce((sum, order) => sum + (order.total_amount || 0), 0);
        const lastOrderDate = orders.length > 0 
          ? orders.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0].created_at
          : null;

        return {
          ...customer,
          totalOrders,
          totalSpent,
          lastOrderDate,
          cpf: customer.cpf_cnpj, // Map cpf_cnpj to cpf for compatibility
          registrationDate: customer.created_at?.split('T')[0] || new Date().toISOString().split('T')[0]
        };
      })
    );

    res.json({ customers: customersWithStats });
  } catch (error) {
    console.error('Erro ao buscar clientes:', error);
    res.status(500).json({ error: 'Erro ao buscar clientes' });
  }
});

// Get customer by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const { data: customer, error } = await supabase
      .from('customers')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('Erro ao buscar cliente:', error);
      return res.status(500).json({ error: 'Erro ao buscar cliente' });
    }

    if (!customer) {
      return res.status(404).json({ error: 'Cliente não encontrado' });
    }

    // Get customer statistics from orders
    const { data: orders, error: ordersError } = await supabase
      .from('orders')
      .select('total_amount, created_at')
      .eq('customer_id', id);

    if (ordersError) {
      console.error(`Erro ao buscar pedidos do cliente ${id}:`, ordersError);
    }

    const totalOrders = orders?.length || 0;
    const totalSpent = orders?.reduce((sum, order) => sum + (order.total_amount || 0), 0) || 0;
    const lastOrderDate = orders?.length > 0 
      ? orders.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0].created_at
      : null;

    const customerWithStats = {
      ...customer,
      totalOrders,
      totalSpent,
      lastOrderDate,
      cpf: customer.cpf_cnpj, // Map cpf_cnpj to cpf for compatibility
      registrationDate: customer.created_at?.split('T')[0] || new Date().toISOString().split('T')[0]
    };

    res.json(customerWithStats);
  } catch (error) {
    console.error('Erro ao buscar cliente:', error);
    res.status(500).json({ error: 'Erro ao buscar cliente' });
  }
});

// Create customer
router.post('/', async (req, res) => {
  try {
    const {
      name,
      email,
      phone,
      cpf,
      address,
      neighborhood,
      city,
      state,
      zipCode,
      birthDate,
      status = 'active',
      notes
    } = req.body;

    const customerData = {
      name,
      email,
      phone,
      cpf_cnpj: cpf, // Map cpf to cpf_cnpj for database
      address,
      neighborhood,
      city,
      state,
      zipcode: zipCode, // Map zipCode to zipcode (lowercase)
      birthdate: birthDate, // Map birthDate to birthdate (lowercase)
      status,
      notes
    };

    const { data: customer, error } = await supabase
      .from('customers')
      .insert([customerData])
      .select()
      .single();

    if (error) {
      console.error('Erro ao criar cliente:', error);
      return res.status(500).json({ error: 'Erro ao criar cliente' });
    }

    res.json({ 
      message: 'Cliente criado com sucesso',
      customer: {
        ...customer,
        cpf: customer.cpf_cnpj, // Map back to cpf for frontend compatibility
        totalOrders: 0,
        totalSpent: 0,
        lastOrderDate: null,
        registrationDate: customer.created_at?.split('T')[0] || new Date().toISOString().split('T')[0]
      }
    });
  } catch (error) {
    console.error('Erro ao criar cliente:', error);
    res.status(500).json({ error: 'Erro ao criar cliente' });
  }
});

// Update customer
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const {
      name,
      email,
      phone,
      cpf,
      address,
      neighborhood,
      city,
      state,
      zipCode,
      birthDate,
      status,
      notes
    } = req.body;

    const customerData = {
      name,
      email,
      phone,
      cpf_cnpj: cpf, // Map cpf to cpf_cnpj for database
      address,
      neighborhood,
      city,
      state,
      zipcode: zipCode, // Map zipCode to zipcode (lowercase)
      birthdate: birthDate, // Map birthDate to birthdate (lowercase)
      status,
      notes,
      updated_at: new Date().toISOString()
    };

    const { data: customer, error } = await supabase
      .from('customers')
      .update(customerData)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Erro ao atualizar cliente:', error);
      return res.status(500).json({ error: 'Erro ao atualizar cliente' });
    }

    if (!customer) {
      return res.status(404).json({ error: 'Cliente não encontrado' });
    }

    // Get updated customer statistics
    const { data: orders, error: ordersError } = await supabase
      .from('orders')
      .select('total, created_at')
      .eq('customer_id', id);

    const totalOrders = orders?.length || 0;
    const totalSpent = orders?.reduce((sum, order) => sum + (order.total || 0), 0) || 0;
    const lastOrderDate = orders?.length > 0 
      ? orders.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0].created_at
      : null;

    const customerWithStats = {
      ...customer,
      totalOrders,
      totalSpent,
      lastOrderDate,
      cpf: customer.cpf_cnpj, // Map back to cpf for frontend compatibility
      registrationDate: customer.created_at?.split('T')[0] || new Date().toISOString().split('T')[0]
    };

    res.json({ 
      message: 'Cliente atualizado com sucesso',
      customer: customerWithStats
    });
  } catch (error) {
    console.error('Erro ao atualizar cliente:', error);
    res.status(500).json({ error: 'Erro ao atualizar cliente' });
  }
});

// Delete customer
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Check if customer has orders
    const { data: orders, error: ordersError } = await supabase
      .from('orders')
      .select('id')
      .eq('customer_id', id)
      .limit(1);

    if (ordersError) {
      console.error('Erro ao verificar pedidos do cliente:', ordersError);
      return res.status(500).json({ error: 'Erro ao verificar pedidos do cliente' });
    }

    if (orders && orders.length > 0) {
      return res.status(400).json({ 
        error: 'Não é possível excluir este cliente pois ele possui pedidos vinculados' 
      });
    }

    const { error } = await supabase
      .from('customers')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Erro ao excluir cliente:', error);
      return res.status(500).json({ error: 'Erro ao excluir cliente' });
    }

    res.json({ message: 'Cliente excluído com sucesso' });
  } catch (error) {
    console.error('Erro ao excluir cliente:', error);
    res.status(500).json({ error: 'Erro ao excluir cliente' });
  }
});

export default router;