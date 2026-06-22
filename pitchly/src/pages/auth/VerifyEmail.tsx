// Responsibility: Explain email verification after signup.
import { Link } from 'react-router-dom'
import { AuthScreen } from './Login'

export function VerifyEmail() {
  return (
    <AuthScreen title="Check your inbox" subtitle="Supabase sent a verification email.">
      <div className="checkmark">✓</div>
      <p className="muted">After verification, return here and sign in.</p>
      <Link to="/login">Go to login</Link>
    </AuthScreen>
  )
}
