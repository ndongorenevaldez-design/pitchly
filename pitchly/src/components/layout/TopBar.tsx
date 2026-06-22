// Responsibility: Show account controls for authenticated pages.
import { useNavigate } from 'react-router-dom'
import { Button } from '../ui/Button'
import { useAuth } from '../../auth/useAuth'

export function TopBar() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  async function handleSignOut() {
    await signOut()
    navigate('/login', { replace: true })
  }

  return (
    <header className="topbar">
      <span>{user?.email}</span>
      <Button variant="ghost" onClick={handleSignOut}>
        Logout
      </Button>
    </header>
  )
}
