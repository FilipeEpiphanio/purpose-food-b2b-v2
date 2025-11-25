// Script de debug para identificar problemas no sistema
console.log('=== SISTEMA DE DEBUG PURPOSE FOOD B2B ===');

// Função para testar navegação
function testNavigation() {
  console.log('🔍 Testando navegação do menu lateral...');
  
  // Verificar se os links estão funcionando
  const menuLinks = document.querySelectorAll('a[href^="/"]');
  console.log(`Encontrados ${menuLinks.length} links de navegação:`);
  
  menuLinks.forEach((link, index) => {
    console.log(`${index + 1}. ${link.href} - Texto: ${link.textContent.trim()}`);
  });
}

// Função para testar formulários
function testForms() {
  console.log('🔍 Testando formulários do sistema...');
  
  // Verificar todos os botões de submit
  const submitButtons = document.querySelectorAll('button[type="submit"], button[onclick*="save"], button[onclick*="submit"]');
  console.log(`Encontrados ${submitButtons.length} botões de submit:`);
  
  submitButtons.forEach((button, index) => {
    console.log(`${index + 1}. Texto: ${button.textContent.trim()}`);
    console.log(`   Classe: ${button.className}`);
    console.log(`   Onclick: ${button.getAttribute('onclick')}`);
  });
}

// Função para testar modais
function testModals() {
  console.log('🔍 Testando modais do sistema...');
  
  // Verificar se há modais abertos
  const modals = document.querySelectorAll('.fixed.inset-0');
  console.log(`Encontrados ${modals.length} modais/modais de fundo:`);
  
  modals.forEach((modal, index) => {
    console.log(`${index + 1}. Classe: ${modal.className}`);
    console.log(`   Z-index: ${window.getComputedStyle(modal).zIndex}`);
    console.log(`   Background: ${window.getComputedStyle(modal).backgroundColor}`);
  });
}

// Função para testar erros de console
function setupErrorCapture() {
  console.log('🔍 Configurando captura de erros...');
  
  // Capturar erros globais
  window.addEventListener('error', (event) => {
    console.error('❌ ERRO CAPTURADO:', event.error);
    console.error('   Mensagem:', event.message);
    console.error('   Arquivo:', event.filename);
    console.error('   Linha:', event.lineno);
  });
  
  // Capturar promessas rejeitadas
  window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ PROMESSA REJEITADA:', event.reason);
  });
}

// Função para testar API
async function testAPIEndpoints() {
  console.log('🔍 Testando endpoints da API...');
  
  const endpoints = [
    '/api/calendar/events',
    '/api/products',
    '/api/orders',
    '/api/financial/transactions'
  ];
  
  for (const endpoint of endpoints) {
    try {
      console.log(`Testando: ${endpoint}`);
      const response = await fetch(endpoint, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer test-user-id'
        }
      });
      
      if (response.ok) {
        console.log(`✅ ${endpoint} - OK (${response.status})`);
      } else {
        console.error(`❌ ${endpoint} - Erro (${response.status}): ${response.statusText}`);
      }
    } catch (error) {
      console.error(`❌ ${endpoint} - Erro de rede:`, error);
    }
  }
}

// Executar todas as funções de teste
function runAllTests() {
  console.log('🚀 Iniciando testes completos do sistema...\n');
  
  testNavigation();
  console.log('');
  
  testForms();
  console.log('');
  
  testModals();
  console.log('');
  
  setupErrorCapture();
  console.log('');
  
  // Aguardar um pouco antes de testar APIs
  setTimeout(() => {
    testAPIEndpoints();
  }, 2000);
  
  console.log('\n✅ Testes iniciados! Verifique os resultados acima.');
  console.log('💡 Dica: Tente executar as ações que não estão funcionando e observe os erros no console.');
}

// Adicionar ao console para fácil acesso
console.log('📋 Comandos disponíveis:');
console.log('  - testNavigation() : Testa navegação');
console.log('  - testForms() : Testa formulários');
console.log('  - testModals() : Testa modais');
console.log('  - testAPIEndpoints() : Testa APIs');
console.log('  - runAllTests() : Executa todos os testes');

// Executar automaticamente
runAllTests();