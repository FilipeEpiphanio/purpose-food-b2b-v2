import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import PurposeFoodLogo from '@/components/ui/PurposeFoodLogo';
import { useSplitScreen } from '@/hooks/useSplitScreen';
import { 
  Home, 
  Package, 
  ShoppingCart, 
  Users, 
  DollarSign, 
  FileText,
  CreditCard,
  Share2,
  FileSpreadsheet,
  TrendingUp,
  Eye,
  Calendar
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { isSplitScreen, screenWidth } = useSplitScreen();

  // Lock body scroll when sidebar is open on mobile (but not in split screen)
  useEffect(() => {
    if (isOpen && !isSplitScreen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, isSplitScreen]);

  // NÃO forçar fechamento automático - deixar o usuário controlar

  const menuItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/produtos', icon: Package, label: 'Produtos' },
    { path: '/pedidos', icon: ShoppingCart, label: 'Pedidos' },
    { path: '/clientes', icon: Users, label: 'Clientes' },
    { path: '/financeiro', icon: DollarSign, label: 'Financeiro' },
    { path: '/calendario', icon: Calendar, label: 'Calendário' },
    { path: '/relatorios', icon: FileText, label: 'Relatórios' },
    { path: '/vendas', icon: CreditCard, label: 'Vendas' },
    { path: '/redes-sociais', icon: Share2, label: 'Redes Sociais' },
    { path: '/notas-fiscais', icon: FileSpreadsheet, label: 'Notas Fiscais' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <>
      {/* Mobile backdrop - show when sidebar is open on mobile/split screen */}
      {isOpen && (screenWidth < 1024 || isSplitScreen) && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-30 z-40 lg:hidden cursor-pointer"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onClose();
          }}
          onTouchEnd={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onClose();
          }}
        />
      )}

      {/* Sidebar - with higher z-index than backdrop */}
      <div className={'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out ' + 
        (isOpen || (screenWidth >= 1024 && !isSplitScreen) ? 'translate-x-0' : '-translate-x-full') + ' ' + 
        (screenWidth >= 1024 && !isSplitScreen ? 'lg:translate-x-0 lg:static lg:inset-0' : '') + ' flex-shrink-0'}>
        {/* Logo and Branding */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex flex-col items-center">
            <PurposeFoodLogo size="medium" variant="default" className="mb-3" />
            <h1 className="text-xl font-bold text-gray-800 mb-1">PURPOSE</h1>
            <h2 className="text-xl font-bold text-gray-800 mb-2">FOOD</h2>
            <p className="text-sm text-orange-500 font-medium">pra alegrar o coração</p>
          </div>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <div className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => {
                    // Fechar menu lateral imediatamente após clicar
                    if (window.innerWidth < 1024) { // Apenas em telas pequenas
                      onClose();
                    }
                  }}
                  className={'flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors ' + (
                    isActive(item.path)
                      ? 'bg-orange-100 text-orange-700 border-r-2 border-orange-500'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
                  )}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.label}
                </Link>
              );
            })}
          </div>

          {/* Quick Stats */}
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h4 className="text-sm font-semibold text-gray-800 mb-3">Resumo Rápido</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Vendas Hoje</span>
                <span className="text-sm font-semibold text-green-600">R$ 1.245</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Pedidos</span>
                <span className="text-sm font-semibold text-blue-600">23</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Clientes</span>
                <span className="text-sm font-semibold text-purple-600">89</span>
              </div>
            </div>
          </div>

          {/* Public Catalog */}
          <div className="mt-6">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Catálogo Público</h3>
            <div className="space-y-2">
              <button className="flex items-center px-4 py-3 rounded-lg text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 w-full transition-colors">
                <Eye className="w-5 h-5 mr-3" />
                Ver Catálogo
              </button>
            </div>
          </div>
        </nav>
      </div>
    </>
  );
};

export default Sidebar;