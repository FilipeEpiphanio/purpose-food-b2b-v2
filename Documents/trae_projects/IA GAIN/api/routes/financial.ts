import express from 'express';
import { createClient } from '@supabase/supabase-js';

const router = express.Router();

// Initialize Supabase with static config for production
const supabaseUrl = 'https://xqsocdvvvbgdgrezoqlf.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhxc29jZHZ2dmJnZGdyZXpvcWxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzYwNjAsImV4cCI6MjA3ODY1MjA2MH0.ZY-Flx5BoBI3vnSS_PfuxaWHpQEOeLSL8By8QVtGtEw';

const supabase = createClient(supabaseUrl, supabaseKey);

// Get all financial records
router.get('/', async (req, res) => {
  try {
    const { data: records, error } = await supabase
      .from('financial_records')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Erro ao buscar registros financeiros:', error);
      return res.status(500).json({ error: 'Erro ao buscar dados financeiros' });
    }

    res.json({
      transactions: records || [],
      total: records?.length || 0
    });
  } catch (error) {
    console.error('Erro na rota financeira:', error);
    res.status(500).json({ error: 'Erro ao buscar dados financeiros' });
  }
});

// Get transactions (order-related)
router.get('/transactions', async (req, res) => {
  try {
    const { data: transactions, error } = await supabase
      .from('transactions')
      .select('*')
      .order('transaction_date', { ascending: false });

    if (error) {
      console.error('Erro ao buscar transações:', error);
      return res.status(500).json({ error: 'Erro ao buscar transações' });
    }

    res.json({
      transactions: transactions || [],
      total: transactions?.length || 0
    });
  } catch (error) {
    console.error('Erro na rota de transações:', error);
    res.status(500).json({ error: 'Erro ao buscar transações' });
  }
});

// Create financial record
router.post('/', async (req, res) => {
  try {
    const { type, category, description, amount, reference_month, reference_year } = req.body;

    if (!type || !category || !amount) {
      return res.status(400).json({ error: 'Campos obrigatórios: type, category, amount' });
    }

    const { data: record, error } = await supabase
      .from('financial_records')
      .insert([{
        type,
        category,
        description,
        amount: parseFloat(amount),
        reference_month: reference_month || new Date().getMonth() + 1,
        reference_year: reference_year || new Date().getFullYear()
      }])
      .select()
      .single();

    if (error) {
      console.error('Erro ao criar registro financeiro:', error);
      return res.status(500).json({ error: 'Erro ao criar registro financeiro' });
    }

    res.json({ 
      message: 'Registro financeiro criado com sucesso',
      data: record
    });
  } catch (error) {
    console.error('Erro ao criar registro financeiro:', error);
    res.status(500).json({ error: 'Erro ao criar registro financeiro' });
  }
});

// Create transaction (order-related)
router.post('/transactions', async (req, res) => {
  try {
    const { type, category, description, amount, payment_method, transaction_date, order_id } = req.body;

    if (!type || !category || !amount) {
      return res.status(400).json({ error: 'Campos obrigatórios: type, category, amount' });
    }

    const { data: transaction, error } = await supabase
      .from('transactions')
      .insert([{
        type,
        category,
        description,
        amount: parseFloat(amount),
        payment_method,
        transaction_date: transaction_date || new Date().toISOString().split('T')[0],
        order_id
      }])
      .select()
      .single();

    if (error) {
      console.error('Erro ao criar transação:', error);
      return res.status(500).json({ error: 'Erro ao criar transação' });
    }

    res.json({ 
      message: 'Transação criada com sucesso',
      data: transaction
    });
  } catch (error) {
    console.error('Erro ao criar transação:', error);
    res.status(500).json({ error: 'Erro ao criar transação' });
  }
});

// Get financial summary
router.get('/summary', async (req, res) => {
  try {
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();

    // Get monthly revenue
    const { data: revenueData } = await supabase
      .from('financial_records')
      .select('amount')
      .eq('type', 'revenue')
      .eq('reference_month', currentMonth)
      .eq('reference_year', currentYear);

    // Get monthly expenses
    const { data: expenseData } = await supabase
      .from('financial_records')
      .select('amount')
      .eq('type', 'expense')
      .eq('reference_month', currentMonth)
      .eq('reference_year', currentYear);

    const monthlyRevenue = revenueData?.reduce((sum, record) => sum + parseFloat(record.amount), 0) || 0;
    const monthlyExpenses = expenseData?.reduce((sum, record) => sum + parseFloat(record.amount), 0) || 0;
    const monthlyProfit = monthlyRevenue - monthlyExpenses;

    res.json({
      monthlyRevenue,
      monthlyExpenses,
      monthlyProfit,
      currentPeriod: `${currentMonth}/${currentYear}`
    });
  } catch (error) {
    console.error('Erro ao buscar resumo financeiro:', error);
    res.status(500).json({ error: 'Erro ao buscar resumo financeiro' });
  }
});

export default router;