// Responsibility: Define the authentication context contract.
import { createContext } from 'react'
import type { User } from '@supabase/supabase-js'
import * as authService from './authService'

export type AuthContextValue = {
  user: User | null
  loading: boolean
  signIn: typeof authService.signIn
  signUp: typeof authService.signUp
  signOut: typeof authService.signOut
  resetPassword: typeof authService.resetPassword
  updatePassword: typeof authService.updatePassword
}

export const AuthContext = createContext<AuthContextValue | null>(null)
