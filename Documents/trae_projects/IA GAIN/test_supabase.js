import { createClient } from '@supabase/supabase-js'

// Testar conexão com Supabase
const supabaseUrl = 'https://xqsocdvvvbgdgrezoqlf.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhxc29jZHZ2dmJnZGdyZXpvcWxmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzYwNjAsImV4cCI6MjA3ODY1MjA2MH0.ZY-Flx5BoBI3vnSS_PfuxaWHpQEOeLSL8By8QVtGtEw'

const supabase = createClient(supabaseUrl, supabaseAnonKey)

async function testConnection() {
  try {
    console.log('🔄 Testando conexão com Supabase...')
    
    // Testar conexão básica
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .limit(1)
    
    if (error) {
      console.error('❌ Erro na conexão:', error.message)
      return false
    }
    
    console.log('✅ Conexão bem-sucedida!')
    console.log('📊 Dados encontrados:', data)
    return true
    
  } catch (error) {
    console.error('❌ Erro geral:', error)
    return false
  }
}

// Testar autenticação
async function testAuth() {
  try {
    console.log('🔄 Testando autenticação...')
    
    const { data: { user }, error } = await supabase.auth.getUser()
    
    if (error) {
      console.log('ℹ️ Nenhum usuário logado (normal)')
      return true
    }
    
    console.log('✅ Usuário encontrado:', user?.email)
    return true
    
  } catch (error) {
    console.error('❌ Erro na autenticação:', error)
    return false
  }
}

// Executar testes
async function runTests() {
  console.log('🚀 INICIANDO TESTES DO SUPABASE...')
  console.log('=====================================')
  
  const connectionOk = await testConnection()
  const authOk = await testAuth()
  
  console.log('\n📋 RESULTADO DOS TESTES:')
  console.log(`Conexão: ${connectionOk ? '✅ OK' : '❌ FALHOU'}`)
  console.log(`Autenticação: ${authOk ? '✅ OK' : '❌ FALHOU'}`)
  
  if (connectionOk && authOk) {
    console.log('\n🎉 TUDO FUNCIONANDO CORRETAMENTE!')
    console.log('Você pode acessar: http://localhost:5173')
  } else {
    console.log('\n⚠️  ALGUM TESTE FALHOU - Verifique as configurações')
  }
}

runTests()