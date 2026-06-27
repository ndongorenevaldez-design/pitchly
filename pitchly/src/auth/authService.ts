// Responsibility: Encapsulate every Supabase Auth call used by the app.
import { getSupabase } from '../lib/supabase'

export type SignUpInput = {
  fullName: string
  email: string
  password: string
}

export async function signUp({ fullName, email, password }: SignUpInput) {
  return getSupabase().auth.signUp({
    email,
    password,
    options: { data: { full_name: fullName } },
  })
}

export async function signIn(email: string, password: string) {
  return getSupabase().auth.signInWithPassword({ email, password })
}

export async function signOut() {
  return getSupabase().auth.signOut()
}

export async function resetPassword(email: string) {
  return getSupabase().auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/reset-password`,
  })
}

export async function updatePassword(password: string) {
  return getSupabase().auth.updateUser({ password })
}
