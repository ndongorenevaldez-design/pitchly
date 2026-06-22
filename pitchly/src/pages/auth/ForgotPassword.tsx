// Responsibility: Request Supabase password reset email.
import { useState } from 'react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useAuth } from '../../auth/useAuth'
import { AuthScreen } from './Login'

export function ForgotPassword() {
  const { resetPassword } = useAuth()
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)

  async function handleReset() {
    await resetPassword(email)
    setSent(true)
  }

  return (
    <AuthScreen title="Reset password" subtitle="We will send a secure reset link.">
      <Input label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <Button onClick={handleReset}>Send reset link</Button>
      {sent ? <p className="success">Check your inbox for the reset link.</p> : null}
    </AuthScreen>
  )
}
