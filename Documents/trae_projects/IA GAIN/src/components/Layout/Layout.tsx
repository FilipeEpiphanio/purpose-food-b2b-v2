import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import { useSplitScreen } from '@/hooks/useSplitScreen';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { isSplitScreen, screenWidth } = useSplitScreen();

  // Detectar quando a tela está dividida ou em tamanho específico
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      // APENAS fechar se a tela for muito pequena (mobile), não em split screen
      if (width < 768) {
        setIsSidebarOpen(false);
      }
    };

    // Executar no mount e adicionar listener
    handleResize();
    window.addEventListener('resize', handleResize);
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Adicionar listener para mudanças de visibilidade da aba (quando usuário alterna entre abas)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Quando a aba fica invisível, fechar o sidebar
        setIsSidebarOpen(false);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
      />
      
      {/* Main content */}
      <div className={`flex-1 min-w-0 transition-all duration-300 ${
        isSidebarOpen && (screenWidth < 1024 || isSplitScreen) ? 'ml-64' : ''
      }`}>
        {/* Header */}
        <Header onMenuClick={() => setIsSidebarOpen(true)} />
        
        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>

    
    </div>
  );
};

export default Layout;