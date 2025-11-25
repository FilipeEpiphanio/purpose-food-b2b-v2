import express from 'express';

const router = express.Router();

// Get social media posts
router.get('/posts', async (req, res) => {
  try {
    res.json({
      posts: [
        {
          id: '1',
          platform: 'instagram',
          content: 'Novo produto disponível!',
          status: 'published',
          scheduledDate: new Date().toISOString()
        }
      ]
    });
  } catch (error) {
    res.status(500).json({ error: 'Erro ao buscar posts' });
  }
});

// Create social media post
router.post('/posts', async (req, res) => {
  try {
    res.json({ message: 'Post criado com sucesso' });
  } catch (error) {
    res.status(500).json({ error: 'Erro ao criar post' });
  }
});

// Send WhatsApp message
router.post('/whatsapp/send', async (req, res) => {
  try {
    res.json({ message: 'Mensagem enviada com sucesso' });
  } catch (error) {
    res.status(500).json({ error: 'Erro ao enviar mensagem' });
  }
});

export default router;