// 🧪 DIAGNÓSTICO DO DASHBOARD - PURPOSE FOOD
// Script para testar funcionalidades do Dashboard

console.log('🔍 INICIANDO DIAGNÓSTICO DO DASHBOARD...')
console.log('======================================')

// Verificar se elementos existem
console.log('📋 VERIFICANDO ELEMENTOS:')

// Verificar botões
checkButtons()

// Verificar conexão com API
checkAPIConnection()

// Verificar autenticação
checkAuthentication()

// Verificar dados do dashboard
checkDashboardData()

function checkButtons() {
  console.log('\n🎯 VERIFICANDO BOTÕES:')
  
  // Verificar se há listeners de eventos
  const buttons = document.querySelectorAll('button')
  console.log(`Total de botões encontrados: ${buttons.length}`)
  
  buttons.forEach((button, index) => {
    console.log(`Botão ${index + 1}: "${button.textContent.trim()}"`)
    
    // Verificar se tem onclick ou event listeners
    if (button.onclick) {
      console.log(`  ✅ Tem onclick direto`)
    } else {
      console.log(`  ⚠️ Sem onclick direto`)
    }
    
    // Verificar classe e estilo
    if (button.className) {
      console.log(`  📋 Classes: ${button.className}`)
    }
  })
}

async function checkAPIConnection() {
  console.log('\n🌐 VERIFICANDO CONEXÃO COM API:')
  
  try {
    // Testar conexão com backend
    const response = await fetch('http://localhost:3001/api/health')
    if (response.ok) {
      console.log('✅ Backend está respondendo')
    } else {
      console.log('❌ Backend retornou erro:', response.status)
    }
  } catch (error) {
    console.log('❌ Erro ao conectar com backend:', error.message)
  }
}

async function checkAuthentication() {
  console.log('\n🔐 VERIFICANDO AUTENTICAÇÃO:')
  
  try {
    // Verificar se há token no localStorage
    const token = localStorage.getItem('sb-xqsocdvvvbgdgrezoqlf-auth-token')
    if (token) {
      console.log('✅ Token de autenticação encontrado')
      
      // Verificar se token é válido
      const authData = JSON.parse(token)
      console.log('📊 Dados do token:', {
        email: authData.user?.email,
        role: authData.user?.role,
        expires_at: new Date(authData.expires_at * 1000).toLocaleString()
      })
    } else {
      console.log('ℹ️ Nenhum token de autenticação encontrado (usuário não logado)')
    }
  } catch (error) {
    console.log('❌ Erro ao verificar autenticação:', error.message)
  }
}

async function checkDashboardData() {
  console.log('\n📊 VERIFICANDO DADOS DO DASHBOARD:')
  
  try {
    // Testar conexão com Supabase
    const response = await fetch('http://localhost:3001/api/dashboard/stats')
    if (response.ok) {
      const data = await response.json()
      console.log('✅ Dados do dashboard carregados:', data)
    } else {
      console.log('❌ Erro ao carregar dados do dashboard:', response.status)
    }
  } catch (error) {
    console.log('❌ Erro ao buscar dados do dashboard:', error.message)
  }
}

// Função para adicionar listeners de teste
function addTestListeners() {
  console.log('\n🔧 ADICIONANDO LISTENERS DE TESTE:')
  
  // Adicionar listeners a todos os botões
  document.querySelectorAll('button').forEach((button, index) => {
    button.addEventListener('click', function(e) {
      console.log(`🖱️ Botão clicado: "${this.textContent.trim()}"`)
      console.log(`📍 Elemento:`, this)
      
      // Prevenir comportamento padrão para teste
      e.preventDefault()
      e.stopPropagation()
      
      // Mostrar alerta de teste
      alert(`Você clicou no botão: "${this.textContent.trim()}"`)
    })
    
    console.log(`✅ Listener adicionado ao botão ${index + 1}`)
  })
}

// Adicionar listeners após 2 segundos
setTimeout(addTestListeners, 2000)

console.log('\n🎉 DIAGNÓSTICO COMPLETO!')
console.log('Os botões agora devem responder com alertas de teste.')
console.log('Clique em qualquer botão para ver se está funcionando!')