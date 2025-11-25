import express from 'express';
import Stripe from 'stripe';

const router = express.Router();
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {
  apiVersion: '2023-10-16',
});

// Criar sessão de checkout Stripe
router.post('/create-checkout-session', async (req, res) => {
  try {
    const { orderId, items, deliveryFee, customerEmail, deliveryOption, deliveryAddress } = req.body;

    // Transformar items para o formato do Stripe
    const lineItems = items.map((item: any) => ({
      price_data: {
        currency: 'brl',
        product_data: {
          name: item.name,
          images: item.image ? [item.image] : [],
        },
        unit_amount: Math.round(item.price * 100), // Converter para centavos
      },
      quantity: item.quantity,
    }));

    // Adicionar taxa de entrega se houver
    if (deliveryFee > 0) {
      lineItems.push({
        price_data: {
          currency: 'brl',
          product_data: {
            name: 'Taxa de Entrega',
          },
        },
        unit_amount: Math.round(deliveryFee * 100),
        quantity: 1,
      });
    }

    // Criar sessão de checkout
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: lineItems,
      mode: 'payment',
      success_url: `${process.env.FRONTEND_URL}/confirmacao-pedido?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.FRONTEND_URL}/carrinho`,
      customer_email: customerEmail,
      metadata: {
        orderId,
        deliveryOption,
        deliveryAddress: deliveryAddress || '',
      },
      payment_intent_data: {
        metadata: {
          orderId,
          deliveryOption,
          deliveryAddress: deliveryAddress || '',
        },
      },
    });

    res.json({ sessionId: session.id });
  } catch (error) {
    console.error('Erro ao criar sessão de checkout:', error);
    res.status(500).json({ error: 'Erro ao criar sessão de checkout' });
  }
});

// Webhook para confirmar pagamento
router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!sig || !endpointSecret) {
    return res.status(400).json({ error: 'Assinatura ou segredo do webhook não configurado' });
  }

  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
  } catch (err: any) {
    console.error('Erro na verificação do webhook:', err.message);
    return res.status(400).json({ error: `Webhook Error: ${err.message}` });
  }

  // Processar o evento
  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object;
      console.log('Checkout session completed:', session.id);
      
      // Aqui você pode atualizar o status do pedido no banco de dados
      // e notificar o cliente sobre a confirmação do pagamento
      break;
      
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      console.log('Payment succeeded:', paymentIntent.id);
      
      // Atualizar status do pagamento no banco de dados
      break;
      
    default:
      console.log(`Evento não tratado: ${event.type}`);
  }

  res.json({ received: true });
});

export default router;