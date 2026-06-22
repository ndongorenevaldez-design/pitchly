// Responsibility: Guard authenticated pages from anonymous access.
import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { FullPageSkeleton } from '../components/ui/Skeleton'
import { useAuth } from './useAuth'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <FullPageSkeleton />
  if (!user) return <Navigate to="/login" replace />
  return children
}
