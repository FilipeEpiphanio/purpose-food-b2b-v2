import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useEffect, useState } from 'react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuthStore()
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false)

  useEffect(() => {
    // Marcar que a autenticação foi verificada após o loading terminar
    if (!loading) {
      setHasCheckedAuth(true)
    }
  }, [loading])

  // Adicionar listener para beforeunload para prevenir perda de dados
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      // Apenas alertar se houver mudanças não salvas
      // Não causar logout
      e.preventDefault()
      e.returnValue = ''
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [])

  if (loading || !hasCheckedAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    )
  }

  // Só redirecionar se tivermos certeza de que não há usuário
  if (!user && hasCheckedAuth) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}