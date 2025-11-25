import React, { useState, useEffect } from 'react';
import { Instagram, Facebook, MessageCircle, Share2, Camera, Send, Heart, MessageSquare, Eye, TrendingUp, Calendar, Clock } from 'lucide-react';
import DataTable from '../components/ui/DataTable';
import FormModal, { FormField } from '../components/ui/FormModal';
import MetricCard from '../components/ui/MetricCard';

interface SocialPost {
  id: string;
  platform: 'instagram' | 'facebook' | 'whatsapp';
  content: string;
  image?: string;
  scheduledDate?: string;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  likes: number;
  comments: number;
  shares: number;
  reach: number;
  publishedAt?: string;
}

interface WhatsAppMessage {
  id: string;
  customerName: string;
  phone: string;
  message: string;
  status: 'sent' | 'delivered' | 'read';
  sentAt: string;
}

export function SocialMedia() {
  const [activeTab, setActiveTab] = useState<'posts' | 'whatsapp' | 'analytics'>('posts');
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [messages, setMessages] = useState<WhatsAppMessage[]>([]);
  const [showPostModal, setShowPostModal] = useState(false);
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [showReplyModal, setShowReplyModal] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState<WhatsAppMessage | null>(null);
  const [replyMessage, setReplyMessage] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch real data from API
  useEffect(() => {
    const fetchSocialData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch social posts
        const postsResponse = await fetch('/api/social-posts');
        if (!postsResponse.ok) {
          throw new Error('Erro ao buscar postagens');
        }
        const postsData = await postsResponse.json();
        setPosts(postsData);

        // Fetch WhatsApp messages
        const messagesResponse = await fetch('/api/whatsapp-messages');
        if (!messagesResponse.ok) {
          throw new Error('Erro ao buscar mensagens');
        }
        const messagesData = await messagesResponse.json();
        setMessages(messagesData);

      } catch (error) {
        console.error('Erro ao buscar dados de redes sociais:', error);
        setError('Erro ao carregar dados. Usando dados de exemplo.');
        
        // Fallback to mock data
        setPosts([
          {
            id: '1',
            platform: 'instagram',
            content: '🍰 Nosso delicioso bolo de chocolate está disponível hoje! Feito com ingredientes frescos e muito amor. Peça já! #PurposeFood #BoloDeChocolate #Artesanal',
            status: 'published',
            likes: 45,
            comments: 12,
            shares: 8,
            reach: 320,
            publishedAt: '2024-01-15T10:30:00Z'
          },
          {
            id: '2',
            platform: 'facebook',
            content: '🎉 Promoção especial da semana! Coxinha por apenas R$7,50 cada. Válido até sexta-feira. Não perca! #Promoção #Coxinha #PurposeFood',
            status: 'scheduled',
            scheduledDate: '2024-01-16T14:00:00Z',
            likes: 0,
            comments: 0,
            shares: 0,
            reach: 0
          },
          {
            id: '3',
            platform: 'whatsapp',
            content: 'Olá! Temos novidades fresquinhas no forno hoje. Quer receber nosso cardápio?',
            status: 'draft',
            likes: 0,
            comments: 0,
            shares: 0,
            reach: 0
          }
        ]);

        setMessages([
          {
            id: '1',
            customerName: 'Maria Silva',
            phone: '(11) 98765-4321',
            message: 'Olá, gostaria de fazer um pedido de 20 coxinhas para sexta-feira',
            status: 'read',
            sentAt: '2024-01-15T09:15:00Z'
          },
          {
            id: '2',
            customerName: 'João Santos',
            phone: '(11) 99876-5432',
            message: 'Bom dia! Vocês fazem entrega em domicílio?',
            status: 'delivered',
            sentAt: '2024-01-15T08:45:00Z'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchSocialData();
  }, []);

  // Funções de interação com postagens
  const handleLikePost = (postId: string) => {
    setPosts(prev => prev.map(post => 
      post.id === postId 
        ? { ...post, likes: post.likes + 1 }
        : post
    ));
    
    // Abrir link do Instagram ou Facebook
    const post = posts.find(p => p.id === postId);
    if (post?.platform === 'instagram') {
      window.open(`https://www.instagram.com/p/CODIGO_DO_POST/`, '_blank');
    } else if (post?.platform === 'facebook') {
      window.open(`https://www.facebook.com/purposefood/posts/CODIGO_DO_POST/`, '_blank');
    }
  };

  const handleCommentPost = (postId: string) => {
    const post = posts.find(p => p.id === postId);
    if (post?.platform === 'instagram') {
      window.open(`https://www.instagram.com/p/CODIGO_DO_POST/comments`, '_blank');
    } else if (post?.platform === 'facebook') {
      window.open(`https://www.facebook.com/purposefood/posts/CODIGO_DO_POST/`, '_blank');
    }
  };

  const handleSharePost = (postId: string) => {
    const post = posts.find(p => p.id === postId);
    if (post) {
      if (navigator.share) {
        navigator.share({
          title: 'Purpose Food',
          text: post.content,
          url: post.platform === 'instagram' 
            ? 'https://www.instagram.com/purposefood'
            : 'https://www.facebook.com/purposefood'
        });
      } else {
        // Fallback para copiar link
        const url = post.platform === 'instagram' 
          ? 'https://www.instagram.com/purposefood'
          : 'https://www.facebook.com/purposefood';
        navigator.clipboard.writeText(url);
        alert('Link copiado para a área de transferência!');
      }
    }
  };

  // Funções de interação com WhatsApp
  const handleReplyWhatsApp = (message: WhatsAppMessage) => {
    setSelectedMessage(message);
    setReplyMessage('');
    setShowReplyModal(true);
  };

  const handleSendWhatsAppReply = () => {
    if (!selectedMessage || !replyMessage.trim()) return;
    
    // Criar link do WhatsApp Web
    const phoneNumber = selectedMessage.phone.replace(/\D/g, '');
    const whatsappUrl = `https://web.whatsapp.com/send?phone=${phoneNumber}&text=${encodeURIComponent(replyMessage)}`;
    
    window.open(whatsappUrl, '_blank');
    
    // Adicionar resposta ao histórico (simulação)
    const newReply = {
      id: `REPLY-${Date.now()}`,
      customerName: selectedMessage.customerName,
      phone: selectedMessage.phone,
      message: replyMessage,
      status: 'sent' as const,
      sentAt: new Date().toISOString(),
      isReply: true
    };
    
    setMessages(prev => [...prev, newReply]);
    setShowReplyModal(false);
    setReplyMessage('');
    setSelectedMessage(null);
  };

  const handleDirectWhatsApp = (phone: string) => {
    const cleanPhone = phone.replace(/\D/g, '');
    window.open(`https://web.whatsapp.com/send?phone=${cleanPhone}`, '_blank');
  };

  const platformIcons = {
    instagram: <Instagram className="w-5 h-5 text-pink-500" />,
    facebook: <Facebook className="w-5 h-5 text-blue-600" />,
    whatsapp: <MessageCircle className="w-5 h-5 text-green-500" />
  };

  const statusColors = {
    draft: 'bg-gray-100 text-gray-800',
    scheduled: 'bg-blue-100 text-blue-800',
    published: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800'
  };

  const postFormFields: FormField[] = [
    {
      name: 'platform',
      label: 'Plataforma',
      type: 'select',
      required: true,
      options: [
        { value: 'instagram', label: 'Instagram' },
        { value: 'facebook', label: 'Facebook' },
        { value: 'whatsapp', label: 'WhatsApp' }
      ]
    },
    {
      name: 'content',
      label: 'Conteúdo',
      type: 'textarea',
      required: true
    },
    {
      name: 'image',
      label: 'Imagem (URL)',
      type: 'text'
    },
    {
      name: 'scheduledDate',
      label: 'Data de Agendamento',
      type: 'text'
    }
  ];

  const messageFormFields: FormField[] = [
    {
      name: 'customerName',
      label: 'Nome do Cliente',
      type: 'text',
      required: true
    },
    {
      name: 'phone',
      label: 'Telefone',
      type: 'tel',
      required: true
    },
    {
      name: 'message',
      label: 'Mensagem',
      type: 'textarea',
      required: true
    }
  ];

  const handleCreatePost = async (data: any) => {
    try {
      const response = await fetch('/api/social-posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platform: data.platform,
          content: data.content,
          image: data.image,
          scheduledDate: data.scheduledDate,
          status: data.scheduledDate ? 'scheduled' : 'draft',
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao criar postagem');
      }

      const newPost = await response.json();
      setPosts([newPost, ...posts]);
      setShowPostModal(false);
    } catch (error) {
      console.error('Erro ao criar postagem:', error);
      alert('Erro ao criar postagem. Tente novamente.');
    }
  };

  const handleSendMessage = async (data: any) => {
    try {
      const response = await fetch('/api/whatsapp-messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customerName: data.customerName,
          phone: data.phone,
          message: data.message,
        }),
      });

      if (!response.ok) {
        throw new Error('Erro ao enviar mensagem');
      }

      const newMessage = await response.json();
      setMessages([newMessage, ...messages]);
      setShowMessageModal(false);
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      alert('Erro ao enviar mensagem. Tente novamente.');
    }
  };

  const filteredPosts = posts.filter(post => {
    const platformMatch = selectedPlatform === 'all' || post.platform === selectedPlatform;
    const statusMatch = selectedStatus === 'all' || post.status === selectedStatus;
    return platformMatch && statusMatch;
  });

  const totalEngagement = posts.reduce((sum, post) => sum + post.likes + post.comments + post.shares, 0);
  const totalReach = posts.reduce((sum, post) => sum + post.reach, 0);
  const publishedPosts = posts.filter(post => post.status === 'published').length;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Redes Sociais</h1>
          <p className="text-gray-600">Gerencie suas postagens e interações sociais</p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            <span className="ml-3 text-gray-600">Carregando dados...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && posts.length === 0 && messages.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Share2 className="w-16 h-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma atividade social</h3>
            <p className="text-gray-600 mb-6">Comece criando sua primeira postagem ou enviando uma mensagem no WhatsApp.</p>
            <div className="space-x-4">
              <button
                onClick={() => setShowPostModal(true)}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 inline-flex items-center"
              >
                <Camera className="w-4 h-4 mr-2" />
                Criar Postagem
              </button>
              <button
                onClick={() => setShowMessageModal(true)}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 inline-flex items-center"
              >
                <Send className="w-4 h-4 mr-2" />
                Enviar Mensagem
              </button>
            </div>
          </div>
        )}

        {/* Content - only show if not loading and has data */}
        {!loading && (posts.length > 0 || messages.length > 0) && (
          <>
            {/* Métricas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total de Posts"
            value={posts.length.toString()}
            icon={<Share2 className="w-6 h-6" />}
            color="purple"
          />
          <MetricCard
            title="Engajamento Total"
            value={totalEngagement.toString()}
            icon={<Heart className="w-6 h-6" />}
            color="pink"
          />
          <MetricCard
            title="Alcance Total"
            value={totalReach.toString()}
            icon={<Eye className="w-6 h-6" />}
            color="blue"
          />
          <MetricCard
            title="Posts Publicados"
            value={publishedPosts.toString()}
            icon={<TrendingUp className="w-6 h-6" />}
            color="green"
          />
        </div>

        {/* Abas de Navegação */}
        <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('posts')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === 'posts'
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Postagens
          </button>
          <button
            onClick={() => setActiveTab('whatsapp')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === 'whatsapp'
                ? 'bg-white text-green-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            WhatsApp
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              activeTab === 'analytics'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Analytics
          </button>
        </div>

        {/* Conteúdo das Abas */}
        {activeTab === 'posts' && (
          <div>
            {/* Filtros e Ações */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="flex gap-2">
                <select
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="all">Todas Plataformas</option>
                  <option value="instagram">Instagram</option>
                  <option value="facebook">Facebook</option>
                  <option value="whatsapp">WhatsApp</option>
                </select>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="all">Todos Status</option>
                  <option value="draft">Rascunho</option>
                  <option value="scheduled">Agendado</option>
                  <option value="published">Publicado</option>
                </select>
              </div>
              <button
                onClick={() => setShowPostModal(true)}
                className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 flex items-center"
              >
                <Camera className="w-4 h-4 mr-2" />
                Nova Postagem
              </button>
            </div>

            {/* Lista de Postagens */}
            <div className="space-y-4">
              {filteredPosts.map(post => (
                <div key={post.id} className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center">
                      {platformIcons[post.platform]}
                      <span className="ml-2 font-medium capitalize">{post.platform}</span>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[post.status]}`}>
                      {post.status === 'draft' ? 'Rascunho' : 
                       post.status === 'scheduled' ? 'Agendado' : 
                       post.status === 'published' ? 'Publicado' : 'Falhou'}
                    </span>
                  </div>
                  
                  <p className="text-gray-800 mb-4 leading-relaxed">{post.content}</p>
                  
                  {post.image && (
                    <div className="w-full h-48 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                      <span className="text-gray-500 text-sm">Imagem: {post.image}</span>
                    </div>
                  )}

                  {post.scheduledDate && (
                    <div className="flex items-center text-sm text-gray-600 mb-4">
                      <Calendar className="w-4 h-4 mr-2" />
                      Agendado para: {new Date(post.scheduledDate).toLocaleString('pt-BR')}
                    </div>
                  )}

                  {post.status === 'published' && (
                    <div className="pt-4 border-t border-gray-200">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-6">
                          <button 
                            onClick={() => handleLikePost(post.id)}
                            className="flex items-center hover:bg-red-50 px-2 py-1 rounded transition-colors group"
                            title="Curtir/Curtidas"
                          >
                            <Heart className="w-4 h-4 text-red-500 mr-1 group-hover:text-red-600" />
                            <span className="text-sm text-gray-600 group-hover:text-red-600">{post.likes}</span>
                          </button>
                          <button 
                            onClick={() => handleCommentPost(post.id)}
                            className="flex items-center hover:bg-blue-50 px-2 py-1 rounded transition-colors group"
                            title="Ver/Adicionar Comentários"
                          >
                            <MessageSquare className="w-4 h-4 text-blue-500 mr-1 group-hover:text-blue-600" />
                            <span className="text-sm text-gray-600 group-hover:text-blue-600">{post.comments}</span>
                          </button>
                          <button 
                            onClick={() => handleSharePost(post.id)}
                            className="flex items-center hover:bg-green-50 px-2 py-1 rounded transition-colors group"
                            title="Compartilhar"
                          >
                            <Share2 className="w-4 h-4 text-green-500 mr-1 group-hover:text-green-600" />
                            <span className="text-sm text-gray-600 group-hover:text-green-600">{post.shares}</span>
                          </button>
                          <div className="flex items-center">
                            <Eye className="w-4 h-4 text-purple-500 mr-1" />
                            <span className="text-sm text-gray-600">{post.reach}</span>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          {post.platform === 'instagram' && (
                            <button
                              onClick={() => window.open('https://www.instagram.com/purposefood', '_blank')}
                              className="bg-pink-500 text-white px-3 py-1 rounded text-xs hover:bg-pink-600 transition-colors"
                            >
                              Ver no Instagram
                            </button>
                          )}
                          {post.platform === 'facebook' && (
                            <button
                              onClick={() => window.open('https://www.facebook.com/purposefood', '_blank')}
                              className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 transition-colors"
                            >
                              Ver no Facebook
                            </button>
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        Clique nos ícones para interagir diretamente na rede social
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'whatsapp' && (
          <div>
            {/* Ações */}
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Mensagens WhatsApp</h2>
              <button
                onClick={() => setShowMessageModal(true)}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 flex items-center"
              >
                <Send className="w-4 h-4 mr-2" />
                Enviar Mensagem
              </button>
            </div>

            {/* Lista de Mensagens */}
            <div className="space-y-4">
              {messages.map(message => (
                <div key={message.id} className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-medium text-gray-900">{message.customerName}</h4>
                      <p className="text-sm text-gray-600">{message.phone}</p>
                    </div>
                    <div className="flex items-center">
                      <span className={`w-2 h-2 rounded-full mr-2 ${
                        message.status === 'read' ? 'bg-green-500' :
                        message.status === 'delivered' ? 'bg-blue-500' :
                        'bg-gray-400'
                      }`}></span>
                      <span className="text-xs text-gray-500">
                        {message.status === 'read' ? 'Lida' :
                         message.status === 'delivered' ? 'Entregue' :
                         'Enviada'}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-gray-800 mb-3 bg-gray-50 p-3 rounded-lg">{message.message}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-xs text-gray-500">
                      <Clock className="w-3 h-3 mr-1" />
                      {new Date(message.sentAt).toLocaleString('pt-BR')}
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleReplyWhatsApp(message)}
                        className="bg-green-500 text-white px-3 py-1 rounded text-xs hover:bg-green-600 transition-colors flex items-center"
                      >
                        <MessageCircle className="w-3 h-3 mr-1" />
                        Responder
                      </button>
                      <button
                        onClick={() => handleDirectWhatsApp(message.phone)}
                        className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700 transition-colors flex items-center"
                      >
                        <Send className="w-3 h-3 mr-1" />
                        WhatsApp Web
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div>
            <h2 className="text-xl font-semibold mb-6">Analytics de Redes Sociais</h2>
            
            {/* Gráficos de Desempenho */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-medium mb-4">Engajamento por Plataforma</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {platformIcons.instagram}
                      <span className="ml-2">Instagram</span>
                    </div>
                    <span className="font-semibold">{posts.filter(p => p.platform === 'instagram').reduce((sum, p) => sum + p.likes + p.comments + p.shares, 0)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {platformIcons.facebook}
                      <span className="ml-2">Facebook</span>
                    </div>
                    <span className="font-semibold">{posts.filter(p => p.platform === 'facebook').reduce((sum, p) => sum + p.likes + p.comments + p.shares, 0)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {platformIcons.whatsapp}
                      <span className="ml-2">WhatsApp</span>
                    </div>
                    <span className="font-semibold">{messages.length}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-medium mb-4">Alcance por Plataforma</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {platformIcons.instagram}
                      <span className="ml-2">Instagram</span>
                    </div>
                    <span className="font-semibold">{posts.filter(p => p.platform === 'instagram').reduce((sum, p) => sum + p.reach, 0)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      {platformIcons.facebook}
                      <span className="ml-2">Facebook</span>
                    </div>
                    <span className="font-semibold">{posts.filter(p => p.platform === 'facebook').reduce((sum, p) => sum + p.reach, 0)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Posts Mais Bem Avaliados */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-medium mb-4">Posts Mais Engajados</h3>
              <div className="space-y-3">
                {posts
                  .filter(p => p.status === 'published')
                  .sort((a, b) => (b.likes + b.comments + b.shares) - (a.likes + a.comments + a.shares))
                  .slice(0, 3)
                  .map(post => (
                    <div key={post.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        {platformIcons[post.platform]}
                        <div className="ml-3">
                          <p className="text-sm font-medium text-gray-900 truncate max-w-md">{post.content}</p>
                          <p className="text-xs text-gray-500">
                            {post.likes + post.comments + post.shares} engajamentos
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-gray-900">{post.reach}</p>
                        <p className="text-xs text-gray-500">alcance</p>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* Modais */}
        <FormModal
          isOpen={showPostModal}
          onClose={() => setShowPostModal(false)}
          title="Criar Postagem"
          fields={postFormFields}
          onSubmit={handleCreatePost}
        />

        <FormModal
          isOpen={showMessageModal}
          onClose={() => setShowMessageModal(false)}
          title="Enviar Mensagem WhatsApp"
          fields={messageFormFields}
          onSubmit={handleSendMessage}
        />

        {/* Modal de Resposta WhatsApp */}
        {showReplyModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Responder Mensagem
                  </h3>
                  <button
                    onClick={() => setShowReplyModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                {selectedMessage && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-900">{selectedMessage.customerName}</p>
                    <p className="text-sm text-gray-600 mt-1">{selectedMessage.message}</p>
                  </div>
                )}
              </div>

              <div className="p-6">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sua Resposta
                  </label>
                  <textarea
                    value={replyMessage}
                    onChange={(e) => setReplyMessage(e.target.value)}
                    placeholder="Digite sua resposta..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 h-32 resize-none"
                  />
                </div>
                <div className="text-xs text-gray-500 mb-4">
                  💡 A resposta será enviada através do WhatsApp Web
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
                <button
                  onClick={() => setShowReplyModal(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSendWhatsAppReply}
                  disabled={!replyMessage.trim()}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Enviar Resposta
                </button>
              </div>
            </div>
          </div>
        )}
          </>
        )}

        {/* Modais */}
        <FormModal
          isOpen={showPostModal}
          onClose={() => setShowPostModal(false)}
          title="Criar Postagem"
          fields={postFormFields}
          onSubmit={handleCreatePost}
        />

        <FormModal
          isOpen={showMessageModal}
          onClose={() => setShowMessageModal(false)}
          title="Enviar Mensagem WhatsApp"
          fields={messageFormFields}
          onSubmit={handleSendMessage}
        />

        {/* Modal de Resposta WhatsApp */}
        {showReplyModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Responder Mensagem
                  </h3>
                  <button
                    onClick={() => setShowReplyModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                {selectedMessage && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-900">{selectedMessage.customerName}</p>
                    <p className="text-sm text-gray-600 mt-1">{selectedMessage.message}</p>
                  </div>
                )}
              </div>

              <div className="p-6">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sua Resposta
                  </label>
                  <textarea
                    value={replyMessage}
                    onChange={(e) => setReplyMessage(e.target.value)}
                    placeholder="Digite sua resposta..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 h-32 resize-none"
                  />
                </div>
                <div className="text-xs text-gray-500 mb-4">
                  💡 A resposta será enviada através do WhatsApp Web
                </div>
              </div>

              <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
                <button
                  onClick={() => setShowReplyModal(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSendWhatsAppReply}
                  disabled={!replyMessage.trim()}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Enviar Resposta
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}