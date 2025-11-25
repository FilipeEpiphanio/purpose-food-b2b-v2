import { create } from 'zustand'
import { supabase } from '../lib/supabase'

interface User {
  id: string
  email: string
  role: string
  created_at: string
}

interface AuthState {
  user: User | null
  loading: boolean
  error: string | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, userData?: any) => Promise<void>
  signOut: () => Promise<void>
  checkAuth: () => Promise<void>
  clearError: () => void
  initializeAuthListener: () => void
}

let authListener: (() => void) | null = null

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  error: null,

  signIn: async (email: string, password: string) => {
    set({ loading: true, error: null })
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error

      if (data.user) {
        const user: User = {
          id: data.user.id,
          email: data.user.email!,
          role: data.user.user_metadata?.role || 'user',
          created_at: data.user.created_at,
        }
        set({ user, loading: false })
      }
    } catch (error: any) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  signUp: async (email: string, password: string, userData?: any) => {
    set({ loading: true, error: null })
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: userData,
        },
      })

      if (error) throw error

      if (data.user) {
        const user: User = {
          id: data.user.id,
          email: data.user.email!,
          role: data.user.user_metadata?.role || 'user',
          created_at: data.user.created_at,
        }
        set({ user, loading: false })
      }
    } catch (error: any) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  signOut: async () => {
    set({ loading: true })
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      set({ user: null, loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  checkAuth: async () => {
    set({ loading: true })
    try {
      const { data: { user } } = await supabase.auth.getUser()
      
      if (user) {
        const userData: User = {
          id: user.id,
          email: user.email!,
          role: user.user_metadata?.role || 'user',
          created_at: user.created_at,
        }
        set({ user: userData, loading: false })
      } else {
        set({ user: null, loading: false })
      }
    } catch (error: any) {
      set({ user: null, loading: false, error: error.message })
    }
  },

  clearError: () => set({ error: null }),

  initializeAuthListener: () => {
    // Limpar listener anterior se existir
    if (authListener) {
      authListener()
      authListener = null
    }

    // Adicionar listener de mudanças de autenticação
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('Auth event:', event)
      
      switch (event) {
        case 'SIGNED_IN':
          if (session?.user) {
            const user: User = {
              id: session.user.id,
              email: session.user.email!,
              role: session.user.user_metadata?.role || 'user',
              created_at: session.user.created_at,
            }
            set({ user, loading: false })
          }
          break
          
        case 'SIGNED_OUT':
        case 'TOKEN_REFRESHED':
        case 'USER_UPDATED':
          // Não fazer nada - manter sessão ativa
          break
          
        case 'PASSWORD_RECOVERY':
        // case 'USER_DELETED': // Removido - n�o � um evento v�lido
          // Apenas limpar usuário em casos extremos
          set({ user: null, loading: false })
          break
          
        default:
          // Manter estado atual para outros eventos
          break
      }
    })

    authListener = subscription.unsubscribe.bind(subscription)
  },
}))
