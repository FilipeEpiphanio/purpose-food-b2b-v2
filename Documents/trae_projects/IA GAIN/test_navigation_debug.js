// SCRIPT DE TESTE PARA VERIFICAR NAVEGAÇÃO E ERROS
// Execute no console do navegador (F12)

console.log('🧪 TESTANDO NAVEGAÇÃO DO DASHBOARD...');
console.log('='.repeat(50));

// Função para testar navegação com proteção
function testNavigationSafely() {
  console.log('🔍 Verificando rotas e navegação...');
  
  // Verificar se React Router está disponível
  if (typeof window.reactRouter === 'undefined') {
    console.log('⚠️ React Router não encontrado globalmente');
  }
  
  // Testar navegação com try-catch
  window.testNavigate = function(path) {
    try {
      console.log(`🧭 Testando navegação para: ${path}`);
      
      // Verificar se a rota existe antes de navegar
      const routes = [
        '/dashboard', '/produtos', '/pedidos', '/clientes', 
        '/financeiro', '/relatorios', '/vendas', '/redes-sociais', '/notas-fiscais'
      ];
      
      if (routes.includes(path)) {
        console.log(`✅ Rota ${path} existe na configuração`);
        
        // Tentar navegar
        if (window.reactRouter && window.reactRouter.navigate) {
          window.reactRouter.navigate(path);
          console.log(`✅ Navegação iniciada para: ${path}`);
        } else if (window.location) {
          window.location.href = path;
          console.log(`✅ Navegação por location.href para: ${path}`);
        } else {
          console.log('❌ Método de navegação não disponível');
        }
      } else {
        console.log(`❌ Rota ${path} não encontrada na configuração`);
      }
      
    } catch (error) {
      console.error('❌ Erro durante navegação:', error);
      console.error('Stack:', error.stack);
    }
  };
  
  // Adicionar event listeners de teste aos botões
  console.log('🎯 Adicionando event listeners de teste...');
  
  setTimeout(() => {
    const buttons = document.querySelectorAll('button');
    console.log(`✅ Encontrados ${buttons.length} botões`);
    
    buttons.forEach((button, index) => {
      const buttonText = button.textContent?.trim() || 'Sem texto';
      
      // Adicionar event listener de teste
      button.addEventListener('click', function testClick(event) {
        console.log(`🖱️ Botão clicado: "${buttonText}"`);
        console.log(`   Classes: ${button.className}`);
        console.log(`   ID: ${button.id || 'Sem ID'}`);
        
        // Mostrar notificação visual
        showTestNotification(`Botão testado: ${buttonText}`);
        
        // Prevenir navegação para teste
        event.preventDefault();
        event.stopPropagation();
        
        console.log(`✅ Evento capturado - navegação prevenida para teste`);
      });
      
      console.log(`✅ Event listener adicionado ao botão ${index + 1}: "${buttonText}"`);
    });
    
    console.log('\n🧪 TESTE CONFIGURADO!');
    console.log('💡 Clique em qualquer botão para testar sem navegação');
    console.log('📝 Use window.testNavigate(\'/caminho\') para testar navegação manual');
    
  }, 1000); // Aguardar 1 segundo para a página carregar completamente
}

// Função para notificações visuais de teste
function showTestNotification(message) {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #2196F3;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: slideInTest 0.3s ease-out;
  `;
  
  // Adicionar animação CSS
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideInTest {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  notification.textContent = message;
  document.body.appendChild(notification);
  
  // Remover notificação após 3 segundos
  setTimeout(() => {
    notification.style.animation = 'slideInTest 0.3s ease-out reverse';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 3000);
}

// Função para verificar erros globais
window.addEventListener('error', function(event) {
  console.error('❌ ERRO GLOBAL DETECTADO:');
  console.error('Mensagem:', event.message);
  console.error('Arquivo:', event.filename);
  console.error('Linha:', event.lineno);
  console.error('Coluna:', event.colno);
  console.error('Stack:', event.error?.stack);
  
  showTestNotification(`ERRO: ${event.message}`);
});

// Função para verificar erros de navegação
window.addEventListener('unhandledrejection', function(event) {
  console.error('❌ PROMESSA REJEITADA NÃO TRATADA:');
  console.error('Razão:', event.reason);
  showTestNotification(`ERRO: ${event.reason}`);
});

// Executar teste
testNavigationSafely();

console.log('\n✅ SCRIPT DE TESTE CARREGADO!');
console.log('🔍 Monitorando erros e navegação...');
console.log('💡 Clique nos botões para testar sem risco de tela preta');