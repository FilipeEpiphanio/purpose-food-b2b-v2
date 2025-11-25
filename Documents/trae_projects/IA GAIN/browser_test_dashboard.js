// SCRIPT DE TESTE PARA EXECUTAR NO CONSOLE DO NAVEGADOR
// Copie e cole este código no console do navegador (F12)

console.log('🚀 INICIANDO TESTE DE FUNCIONALIDADE DO DASHBOARD...');
console.log('='.repeat(50));

// Função para adicionar event listeners temporários aos botões
function testDashboardButtons() {
  console.log('📋 VERIFICANDO BOTÕES DO DASHBOARD...');
  
  // Encontrar todos os botões da página
  const buttons = document.querySelectorAll('button');
  console.log(`✅ Encontrados ${buttons.length} botões na página`);
  
  // Testar cada botão
  buttons.forEach((button, index) => {
    const buttonText = button.textContent?.trim() || 'Sem texto';
    const buttonId = button.id || 'Sem ID';
    const buttonClass = button.className || 'Sem classe';
    
    console.log(`\n🔍 Botão ${index + 1}:`);
    console.log(`   Texto: "${buttonText}"`);
    console.log(`   ID: "${buttonId}"`);
    console.log(`   Classe: "${buttonClass}"`);
    console.log(`   Event listeners atuais: ${button.onclick ? 'Tem onclick' : 'Sem onclick'}`);
    
    // Adicionar event listener de teste
    button.addEventListener('click', function testClick(event) {
      console.log(`✅ BOTÃO CLICADO: "${buttonText}"`);
      console.log(`   ID: ${buttonId}`);
      console.log(`   Classes: ${buttonClass}`);
      
      // Mostrar notificação visual
      showNotification(`Botão clicado: ${buttonText}`);
      
      // Prevenir ação padrão apenas para teste
      event.preventDefault();
    });
    
    console.log(`✅ Event listener de teste adicionado ao botão "${buttonText}"`);
  });
  
  // Testar links de navegação
  console.log('\n🔗 VERIFICANDO LINKS DE NAVEGAÇÃO...');
  const links = document.querySelectorAll('a[href^="/"]');
  console.log(`✅ Encontrados ${links.length} links de navegação`);
  
  links.forEach((link, index) => {
    const linkText = link.textContent?.trim() || 'Sem texto';
    const linkHref = link.getAttribute('href') || 'Sem href';
    
    console.log(`\n🔍 Link ${index + 1}:`);
    console.log(`   Texto: "${linkText}"`);
    console.log(`   Href: "${linkHref}"`);
    
    // Adicionar event listener de teste
    link.addEventListener('click', function testLinkClick(event) {
      console.log(`✅ LINK CLICADO: "${linkText}" -> "${linkHref}"`);
      showNotification(`Link clicado: ${linkText} -> ${linkHref}`);
      
      // Prevenir navegação apenas para teste
      event.preventDefault();
    });
  });
  
  // Testar cards de métricas
  console.log('\n📊 VERIFICANDO CARDS DE MÉTRICAS...');
  const metricCards = document.querySelectorAll('[class*="metric"], [class*="card"]');
  console.log(`✅ Encontrados ${metricCards.length} cards de métricas`);
  
  metricCards.forEach((card, index) => {
    const cardText = card.textContent?.trim().substring(0, 50) + '...' || 'Sem texto';
    console.log(`\n📋 Card ${index + 1}: "${cardText}"`);
    
    // Tornar cards clicáveis para teste
    card.style.cursor = 'pointer';
    card.addEventListener('click', function testCardClick() {
      console.log(`✅ CARD CLICADO: "${cardText}"`);
      showNotification(`Card clicado: ${cardText}`);
    });
  });
  
  console.log('\n✅ TESTES CONCLUÍDOS!');
  console.log('📝 Todos os botões, links e cards agora têm event listeners de teste.');
  console.log('💡 Clique em qualquer elemento para ver a ação no console.');
}

// Função para mostrar notificações visuais
function showNotification(message) {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    font-family: Arial, sans-serif;
    font-size: 14px;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: slideIn 0.3s ease-out;
  `;
  
  // Adicionar animação CSS
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  notification.textContent = message;
  document.body.appendChild(notification);
  
  // Remover notificação após 3 segundos
  setTimeout(() => {
    notification.style.animation = 'slideIn 0.3s ease-out reverse';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 3000);
}

// Função para verificar estado do sistema
function checkSystemStatus() {
  console.log('\n🔍 VERIFICANDO ESTADO DO SISTEMA...');
  
  // Verificar se está logado
  const authToken = localStorage.getItem('sb-xqsocdvvvbgdgrezoqlf-auth-token');
  console.log(`🔐 Token de autenticação: ${authToken ? '✅ Encontrado' : '❌ Não encontrado'}`);
  
  // Verificar URL atual
  console.log(`📍 URL atual: ${window.location.href}`);
  
  // Verificar se há erros no console
  console.log('📋 Verifique abaixo por mensagens de erro...');
  
  // Testar conexão com Supabase
  if (window.supabase) {
    console.log('✅ Supabase está disponível globalmente');
  } else {
    console.log('⚠️  Supabase não encontrado globalmente');
  }
}

// Executar testes
console.log('🎯 Para executar os testes, cole estas funções no console:');
console.log('');
console.log('// Executar todos os testes:');
console.log('testDashboardButtons();');
console.log('');
console.log('// Verificar estado do sistema:');
console.log('checkSystemStatus();');
console.log('');
console.log('// Executar ambos:');
console.log('testDashboardButtons(); checkSystemStatus();');

// Mensagem final
console.log('');
console.log('✅ SCRIPT DE TESTE CARREGADO COM SUCESSO!');
console.log('📋 Copie e cole as funções acima no console do navegador.');
console.log('🔧 Isso adicionará event listeners de teste aos botões e elementos.');