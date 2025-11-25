import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ShoppingCart, Search, User, Menu, X, LogOut, Package, Clock } from 'lucide-react';
import PurposeFoodLogo from './PurposeFoodLogo';
import { useCustomerStore } from '../../stores/customerStore';
import NotificationBell from './NotificationBell';

interface CustomerLayoutProps {
  children: React.ReactNode;
}

const CustomerLayout: React.FC<CustomerLayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const { cartItems, customer, signOut } = useCustomerStore();
  
  const cartItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  const handleSearch = (term: string) => {
    if (term.trim()) {
      navigate(`/cardapio?search=${encodeURIComponent(term)}`);
    }
  };

  const handleLogout = () => {
    signOut();
    setIsProfileOpen(false);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center">
              <PurposeFoodLogo size="small" />
              <span className="ml-2 text-xl font-bold text-gray-900">Purpose Food</span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <Link
                to="/"
                className={`text-gray-700 hover:text-orange-600 transition-colors ${
                  isActive('/') ? 'text-orange-600 font-medium' : ''
                }`}
              >
                Início
              </Link>
              <Link
                to="/cardapio"
                className={`text-gray-700 hover:text-orange-600 transition-colors ${
                  isActive('/cardapio') ? 'text-orange-600 font-medium' : ''
                }`}
              >
                Cardápio
              </Link>
            </nav>

            {/* Search Bar */}
            <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Buscar produtos..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSearch((e.target as HTMLInputElement).value);
                    }
                  }}
                />
              </div>
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              {customer && (
                <NotificationBell 
                  customerId={customer.id}
                  className="hidden md:block"
                />
              )}

              {/* Cart */}
              <Link
                to="/carrinho"
                className="relative p-2 text-gray-700 hover:text-orange-600 transition-colors"
              >
                <ShoppingCart className="w-6 h-6" />
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {cartItemCount > 99 ? '99+' : cartItemCount}
                  </span>
                )}
              </Link>

              {/* Profile Menu */}
              <div className="relative">
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center p-2 text-gray-700 hover:text-orange-600 transition-colors"
                >
                  <User className="w-6 h-6" />
                </button>

                {isProfileOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50">
                    {customer ? (
                      <>
                        <div className="px-4 py-2 border-b border-gray-100">
                          <p className="text-sm font-medium text-gray-900">{customer.name}</p>
                          <p className="text-xs text-gray-500">{customer.email}</p>
                        </div>
                        <Link
                          to="/pedidos"
                          className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => {setIsProfileOpen(false); setIsMenuOpen(false);}}
                        >
                          <Package className="w-4 h-4 mr-2" />
                          Meus Pedidos
                        </Link>
                        <button
                          onClick={handleLogout}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <LogOut className="w-4 h-4 mr-2" />
                          Sair
                        </button>
                      </>
                    ) : (
                      <>
                        <Link
                          to="/login"
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setIsProfileOpen(false)}
                        >
                          Entrar
                        </Link>
                        <Link
                          to="/cadastro"
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setIsProfileOpen(false)}
                        >
                          Cadastrar
                        </Link>
                      </>
                    )}
                  </div>
                )}
              </div>

              {/* Mobile Menu Toggle */}
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden p-2 text-gray-700 hover:text-orange-600"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-4 py-2">
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Buscar produtos..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSearch((e.target as HTMLInputElement).value);
                      setIsMenuOpen(false);
                    }
                  }}
                />
              </div>
            </div>
            <nav className="px-4 pb-4">
              <Link
                to="/"
                className={`block py-2 text-gray-700 hover:text-orange-600 ${
                  isActive('/') ? 'text-orange-600 font-medium' : ''
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Início
              </Link>
              <Link
                to="/cardapio"
                className={`block py-2 text-gray-700 hover:text-orange-600 ${
                  isActive('/cardapio') ? 'text-orange-600 font-medium' : ''
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Cardápio
              </Link>
              {customer && (
                <Link
                  to="/pedidos"
                  className="block py-2 text-gray-700 hover:text-orange-600"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Meus Pedidos
                </Link>
              )}
            </nav>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Company Info */}
            <div>
              <div className="flex items-center mb-4">
                <PurposeFoodLogo size="small" variant="light" />
                <span className="ml-2 text-lg font-bold">Purpose Food</span>
              </div>
              <p className="text-gray-400 text-sm">
                Deliciosos produtos artesanais feitos com amor para alegrar seu coração.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Links Rápidos</h3>
              <ul className="space-y-2 text-sm">
                <li><Link to="/" className="text-gray-400 hover:text-white">Início</Link></li>
                <li><Link to="/cardapio" className="text-gray-400 hover:text-white">Cardápio</Link></li>
                <li><Link to="/carrinho" className="text-gray-400 hover:text-white">Carrinho</Link></li>
              </ul>
            </div>

            {/* Contact Info */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Contato</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>WhatsApp: (11) 99999-9999</li>
                <li>Email: contato@purposefood.com.br</li>
                <li>Horário: Seg-Sex 8h-18h</li>
              </ul>
            </div>

            {/* Social Media */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Redes Sociais</h3>
              <p className="text-gray-400 text-sm mb-4">
                Siga-nos para novidades e promoções!
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white">
                  Instagram
                </a>
                <a href="#" className="text-gray-400 hover:text-white">
                  WhatsApp
                </a>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2024 Purpose Food. Todos os direitos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default CustomerLayout;