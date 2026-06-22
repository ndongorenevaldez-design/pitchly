// Responsibility: Register new users with Supabase Auth.
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/useAuth'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { PasswordStrength } from '../../components/ui/PasswordStrength'
import { AuthScreen } from './Login'

export function SignUp() {
  const { signUp } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')

  async function handleSignUp() {
    setError('')
    if (password !== confirm) {
      setError('Passwords must match')
      return
    }
    const { error: authError } = await signUp({ fullName, email, password })
    if (authError) setError(authError.message)
    else navigate('/verify-email', { replace: true })
  }

  return (
    <AuthScreen title="Create your account" subtitle="Build a private practice history.">
      <Input label="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
      <Input label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <Input
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <PasswordStrength password={password} />
      <Input
        label="Confirm password"
        type="password"
        value={confirm}
        onChange={(e) => setConfirm(e.target.value)}
      />
      {error ? <p className="error">{error}</p> : null}
      <Button onClick={handleSignUp}>Sign up</Button>
      <p className="muted">
        Already registered? <Link to="/login">Login</Link>
      </p>
    </AuthScreen>
  )
}
