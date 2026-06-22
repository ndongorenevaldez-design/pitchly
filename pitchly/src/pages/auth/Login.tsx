// Responsibility: Authenticate returning users.
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useAuth } from '../../auth/useAuth'

export function Login() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleLogin() {
    setLoading(true)
    setError('')
    const { error: authError } = await signIn(email, password)
    setLoading(false)
    if (authError) setError('Invalid email or password')
    else navigate('/dashboard', { replace: true })
  }

  return (
    <AuthScreen title="Welcome back" subtitle="Continue your practice history.">
      <Input label="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <Input
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error ? <p className="error">{error}</p> : null}
      <Button onClick={handleLogin} disabled={loading}>
        {loading ? 'Signing in' : 'Login'}
      </Button>
      <p className="muted">
        New here? <Link to="/signup">Create account</Link> ·{' '}
        <Link to="/forgot-password">Reset password</Link>
      </p>
    </AuthScreen>
  )
}

export function AuthScreen({
  title,
  subtitle,
  children,
}: {
  title: string
  subtitle: string
  children: React.ReactNode
}) {
  return (
    <main className="auth-page">
      <section className="auth-brand">
        <h1>Pitchly</h1>
        <p>Your AI coach to master communication.</p>
      </section>
      <section className="auth-panel">
        <h2>{title}</h2>
        <p>{subtitle}</p>
        <div className="stack">{children}</div>
      </section>
    </main>
  )
}
