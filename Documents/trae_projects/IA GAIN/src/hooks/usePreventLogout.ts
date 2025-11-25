import { useEffect, useRef } from 'react'
import { useAuthStore } from '@/stores/authStore'

/**
 * Hook para prevenir logout durante ações importantes
 * Mantém a sessão ativa mesmo durante operações longas
 */
export const usePreventLogout = () => {
  const { user } = useAuthStore()
  const isActive = useRef(false)

  const preventLogout = () => {
    isActive.current = true
    
    // Prevenir que o navegador descarte a sessão
    if (typeof window !== 'undefined') {
      // Manter localStorage ativo
      const keepAlive = () => {
        if (isActive.current && user) {
          localStorage.setItem('lastActivity', Date.now().toString())
          setTimeout(keepAlive, 30000) // Atualizar a cada 30 segundos
        }
      }
      keepAlive()
    }
  }

  const allowLogout = () => {
    isActive.current = false
  }

  useEffect(() => {
    return () => {
      allowLogout() // Limpar ao desmontar componente
    }
  }, [])

  return {
    preventLogout,
    allowLogout,
    isPreventing: isActive.current
  }
}

/**
 * Hook para monitorar atividade do usuário
 */
export const useActivityMonitor = () => {
  useEffect(() => {
    const updateActivity = () => {
      localStorage.setItem('lastActivity', Date.now().toString())
    }

    // Monitorar vários tipos de atividade
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click']
    events.forEach(event => {
      window.addEventListener(event, updateActivity, { passive: true })
    })

    updateActivity() // Setar atividade inicial

    return () => {
      events.forEach(event => {
        window.removeEventListener(event, updateActivity)
      })
    }
  }, [])
}