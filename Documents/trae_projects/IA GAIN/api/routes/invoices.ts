import express from 'express';
import { supabase } from '../server';

const router = express.Router();

// Get all invoices
router.get('/', async (req, res) => {
  try {
    const { data: invoices, error } = await supabase
      .from('invoices')
      .select(`
        *,
        customers!inner(
          id,
          name,
          cpf_cnpj,
          email,
          address,
          city,
          state
        )
      `)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Erro ao buscar notas fiscais:', error);
      return res.status(500).json({ error: 'Erro ao buscar notas fiscais' });
    }

    // Transform data to match frontend interface
    const transformedInvoices = invoices.map(invoice => ({
      id: invoice.id,
      number: invoice.invoice_number,
      series: invoice.series,
      customer: {
        name: invoice.customers?.name || 'Cliente não encontrado',
        cpfCnpj: invoice.customers?.cpf_cnpj || '',
        email: invoice.customers?.email || '',
        address: `${invoice.customers?.address || ''}, ${invoice.customers?.city || ''} - ${invoice.customers?.state || ''}`.replace(',  - ', '')
      },
      items: [], // Items would be fetched separately if needed
      totalAmount: parseFloat(invoice.total_amount) || 0,
      taxAmount: parseFloat(invoice.tax_amount) || 0,
      netAmount: (parseFloat(invoice.total_amount) || 0) - (parseFloat(invoice.tax_amount) || 0),
      status: invoice.status || 'draft',
      issueDate: invoice.issue_date,
      dueDate: invoice.due_date,
      paymentMethod: invoice.payment_method || '',
      notes: invoice.notes,
      xmlUrl: null, // Would be generated/stored separately
      pdfUrl: invoice.pdf_url
    }));

    res.json({ invoices: transformedInvoices });
  } catch (error) {
    console.error('Erro ao buscar notas fiscais:', error);
    res.status(500).json({ error: 'Erro ao buscar notas fiscais' });
  }
});

// Get invoice by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const { data: invoice, error } = await supabase
      .from('invoices')
      .select(`
        *,
        customers!inner(
          id,
          name,
          cpf_cnpj,
          email,
          address,
          city,
          state
        )
      `)
      .eq('id', id)
      .single();

    if (error) {
      console.error('Erro ao buscar nota fiscal:', error);
      return res.status(500).json({ error: 'Erro ao buscar nota fiscal' });
    }

    if (!invoice) {
      return res.status(404).json({ error: 'Nota fiscal não encontrada' });
    }

    // Transform data to match frontend interface
    const transformedInvoice = {
      id: invoice.id,
      number: invoice.invoice_number,
      series: invoice.series,
      customer: {
        name: invoice.customers?.name || 'Cliente não encontrado',
        cpfCnpj: invoice.customers?.cpf_cnpj || '',
        email: invoice.customers?.email || '',
        address: `${invoice.customers?.address || ''}, ${invoice.customers?.city || ''} - ${invoice.customers?.state || ''}`.replace(',  - ', '')
      },
      items: [], // Items would be fetched separately if needed
      totalAmount: parseFloat(invoice.total_amount) || 0,
      taxAmount: parseFloat(invoice.tax_amount) || 0,
      netAmount: (parseFloat(invoice.total_amount) || 0) - (parseFloat(invoice.tax_amount) || 0),
      status: invoice.status || 'pending',
      issueDate: invoice.issue_date,
      dueDate: invoice.due_date,
      paymentMethod: invoice.payment_method || '',
      notes: invoice.notes,
      xmlUrl: null, // Would be generated/stored separately
      pdfUrl: invoice.pdf_url
    };

    res.json(transformedInvoice);
  } catch (error) {
    console.error('Erro ao buscar nota fiscal:', error);
    res.status(500).json({ error: 'Erro ao buscar nota fiscal' });
  }
});

// Create invoice
router.post('/', async (req, res) => {
  try {
    const {
      customerId,
      series = '1',
      totalAmount,
      taxAmount = 0,
      status = 'pending',
      issueDate,
      dueDate,
      paymentMethod,
      notes
    } = req.body;

    // Generate invoice number
    const { data: lastInvoice, error: lastError } = await supabase
      .from('invoices')
      .select('invoice_number')
      .order('invoice_number', { ascending: false })
      .limit(1)
      .single();

    let nextNumber = '0001';
    if (lastInvoice && lastInvoice.invoice_number) {
      const lastNum = parseInt(lastInvoice.invoice_number);
      nextNumber = String(lastNum + 1).padStart(4, '0');
    }

    const invoiceData = {
      customer_id: customerId,
      invoice_number: nextNumber,
      series,
      total_amount: totalAmount,
      tax_amount: taxAmount,
      status,
      issue_date: issueDate,
      due_date: dueDate,
      payment_method: paymentMethod,
      notes
    };

    const { data: invoice, error } = await supabase
      .from('invoices')
      .insert([invoiceData])
      .select(`
        *,
        customers!inner(
          id,
          name,
          cpf_cnpj,
          email,
          address,
          city,
          state
        )
      `)
      .single();

    if (error) {
      console.error('Erro ao criar nota fiscal:', error);
      return res.status(500).json({ error: 'Erro ao criar nota fiscal' });
    }

    // Transform data to match frontend interface
    const transformedInvoice = {
      id: invoice.id,
      number: invoice.invoice_number,
      series: invoice.series,
      customer: {
        name: invoice.customers?.name || 'Cliente não encontrado',
        cpfCnpj: invoice.customers?.cpf_cnpj || '',
        email: invoice.customers?.email || '',
        address: `${invoice.customers?.address || ''}, ${invoice.customers?.city || ''} - ${invoice.customers?.state || ''}`.replace(',  - ', '')
      },
      items: [],
      totalAmount: parseFloat(invoice.total_amount) || 0,
      taxAmount: parseFloat(invoice.tax_amount) || 0,
      netAmount: (parseFloat(invoice.total_amount) || 0) - (parseFloat(invoice.tax_amount) || 0),
      status: invoice.status || 'pending',
      issueDate: invoice.issue_date,
      dueDate: invoice.due_date,
      paymentMethod: invoice.payment_method || '',
      notes: invoice.notes,
      xmlUrl: null,
      pdfUrl: invoice.pdf_url
    };

    res.json({ 
      message: 'Nota fiscal criada com sucesso',
      invoice: transformedInvoice
    });
  } catch (error) {
    console.error('Erro ao criar nota fiscal:', error);
    res.status(500).json({ error: 'Erro ao criar nota fiscal' });
  }
});

// Update invoice
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const {
      series,
      totalAmount,
      taxAmount,
      status,
      issueDate,
      dueDate,
      paymentMethod,
      notes
    } = req.body;

    const invoiceData = {
      series,
      total_amount: totalAmount,
      tax_amount: taxAmount,
      status,
      issue_date: issueDate,
      due_date: dueDate,
      payment_method: paymentMethod,
      notes,
      updated_at: new Date().toISOString()
    };

    const { data: invoice, error } = await supabase
      .from('invoices')
      .update(invoiceData)
      .eq('id', id)
      .select(`
        *,
        customers!inner(
          id,
          name,
          cpf_cnpj,
          email,
          address,
          city,
          state
        )
      `)
      .single();

    if (error) {
      console.error('Erro ao atualizar nota fiscal:', error);
      return res.status(500).json({ error: 'Erro ao atualizar nota fiscal' });
    }

    if (!invoice) {
      return res.status(404).json({ error: 'Nota fiscal não encontrada' });
    }

    // Transform data to match frontend interface
    const transformedInvoice = {
      id: invoice.id,
      number: invoice.invoice_number,
      series: invoice.series,
      customer: {
        name: invoice.customers?.name || 'Cliente não encontrado',
        cpfCnpj: invoice.customers?.cpf_cnpj || '',
        email: invoice.customers?.email || '',
        address: `${invoice.customers?.address || ''}, ${invoice.customers?.city || ''} - ${invoice.customers?.state || ''}`.replace(',  - ', '')
      },
      items: [],
      totalAmount: parseFloat(invoice.total_amount) || 0,
      taxAmount: parseFloat(invoice.tax_amount) || 0,
      netAmount: (parseFloat(invoice.total_amount) || 0) - (parseFloat(invoice.tax_amount) || 0),
      status: invoice.status || 'pending',
      issueDate: invoice.issue_date,
      dueDate: invoice.due_date,
      paymentMethod: invoice.payment_method || '',
      notes: invoice.notes,
      xmlUrl: null,
      pdfUrl: invoice.pdf_url
    };

    res.json({ 
      message: 'Nota fiscal atualizada com sucesso',
      invoice: transformedInvoice
    });
  } catch (error) {
    console.error('Erro ao atualizar nota fiscal:', error);
    res.status(500).json({ error: 'Erro ao atualizar nota fiscal' });
  }
});

// Delete invoice
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Check if invoice can be deleted (only drafts)
    const { data: invoice, error: checkError } = await supabase
      .from('invoices')
      .select('status')
      .eq('id', id)
      .single();

    if (checkError) {
      console.error('Erro ao verificar nota fiscal:', checkError);
      return res.status(500).json({ error: 'Erro ao verificar nota fiscal' });
    }

    if (!invoice) {
      return res.status(404).json({ error: 'Nota fiscal não encontrada' });
    }

    if (invoice.status !== 'pending' && invoice.status !== 'draft') {
      return res.status(400).json({ 
        error: 'Só é possível excluir notas fiscais com status rascunho ou pendente' 
      });
    }

    const { error } = await supabase
      .from('invoices')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Erro ao excluir nota fiscal:', error);
      return res.status(500).json({ error: 'Erro ao excluir nota fiscal' });
    }

    res.json({ message: 'Nota fiscal excluída com sucesso' });
  } catch (error) {
    console.error('Erro ao excluir nota fiscal:', error);
    res.status(500).json({ error: 'Erro ao excluir nota fiscal' });
  }
});

export default router;