import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { ShoppingCart, User, Search, Heart, Package, LogOut } from 'lucide-react';
import { useCustomerStore } from '@/stores/customerStore';

interface CustomerLayoutProps {
  children?: React.ReactNode;
}

const CustomerLayout: React.FC<CustomerLayoutProps> = () => {
  const location = useLocation();
  const { cartItems, customer, signOut } = useCustomerStore();
  
  const cartItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  const handleLogout = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center">
              <div className="text-2xl font-bold text-orange-600">Purpose Food</div>
              <span className="ml-2 text-sm text-gray-500">pra alegrar o coração</span>
            </Link>

            {/* Search Bar */}
            <div className="flex-1 max-w-lg mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Buscar produtos..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
            </div>

            {/* User Menu & Cart */}
            <div className="flex items-center space-x-4">
              <Link to="/favoritos" className="p-2 text-gray-600 hover:text-orange-600">
                <Heart className="w-6 h-6" />
              </Link>
              
              <Link to="/carrinho" className="relative p-2 text-gray-600 hover:text-orange-600">
                <ShoppingCart className="w-6 h-6" />
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {cartItemCount}
                  </span>
                )}
              </Link>

              {customer ? (
                <div className="relative group">
                  <button className="flex items-center space-x-2 p-2 text-gray-600 hover:text-orange-600">
                    <User className="w-6 h-6" />
                    <span className="hidden md:block text-sm">{customer.name}</span>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <Link to="/perfil" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      Meu Perfil
                    </Link>
                    <Link to="/pedidos" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      Meus Pedidos
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 border-t border-gray-200"
                    >
                      <LogOut className="w-4 h-4 inline mr-2" />
                      Sair
                    </button>
                  </div>
                </div>
              ) : (
                <Link
                  to="/login"
                  className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
                >
                  Entrar
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <Link
              to="/"
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                location.pathname === '/'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Início
            </Link>
            <Link
              to="/produtos"
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                location.pathname === '/produtos'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Produtos
            </Link>
            <Link
              to="/categorias"
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                location.pathname === '/categorias'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Categorias
            </Link>
            <Link
              to="/sobre"
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                location.pathname === '/sobre'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Sobre Nós
            </Link>
            <Link
              to="/contato"
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                location.pathname === '/contato'
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Contato
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Purpose Food</h3>
              <p className="text-gray-300 text-sm">
                Alimentos artesanais feitos com amor para alegrar seu coração.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Produtos</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li><Link to="/produtos/salgados">Salgados</Link></li>
                <li><Link to="/produtos/doces">Doces</Link></li>
                <li><Link to="/produtos/festas">Para Festas</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Atendimento</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li><Link to="/contato">Fale Conosco</Link></li>
                <li><Link to="/duvidas">Dúvidas Frequentes</Link></li>
                <li><Link to="/entrega">Política de Entrega</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Redes Sociais</h4>
              <div className="flex space-x-4">
                <a href="https://instagram.com/purposefood" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-white">
                  Instagram
                </a>
                <a href="https://facebook.com/purposefood" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-white">
                  Facebook
                </a>
                <a href="https://wa.me/5511987654321" target="_blank" rel="noopener noreferrer" className="text-gray-300 hover:text-white">
                  WhatsApp
                </a>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-sm text-gray-300">
            <p>&copy; 2024 Purpose Food. Todos os direitos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default CustomerLayout;