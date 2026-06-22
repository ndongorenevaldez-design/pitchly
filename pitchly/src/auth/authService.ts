// Responsibility: Encapsulate every Supabase Auth call used by the app.
import { supabase } from '../lib/supabase'

export type SignUpInput = {
  fullName: string
  email: string
  password: string
}

export async function signUp({ fullName, email, password }: SignUpInput) {
  return supabase.auth.signUp({
    email,
    password,
    options: { data: { full_name: fullName } },
  })
}

export async function signIn(email: string, password: string) {
  return supabase.auth.signInWithPassword({ email, password })
}

export async function signOut() {
  return supabase.auth.signOut()
}

export async function resetPassword(email: string) {
  return supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/reset-password`,
  })
}

export async function updatePassword(password: string) {
  return supabase.auth.updateUser({ password })
}
