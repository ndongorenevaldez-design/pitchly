// Responsibility: Save a new password after a Supabase reset link.
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { PasswordStrength } from '../../components/ui/PasswordStrength'
import { useAuth } from '../../auth/useAuth'
import { AuthScreen } from './Login'

export function ResetPassword() {
  const { updatePassword } = useAuth()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')

  async function handleUpdate() {
    await updatePassword(password)
    navigate('/login', { replace: true })
  }

  return (
    <AuthScreen title="Choose a new password" subtitle="Use a strong password.">
      <Input
        label="New password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <PasswordStrength password={password} />
      <Button onClick={handleUpdate}>Update password</Button>
    </AuthScreen>
  )
}
