// Responsibility: Provide primary authenticated navigation.
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../auth/useAuth'

export function Sidebar() {
  const { user } = useAuth()
  const isAdmin = user?.email === 'admin@gmail.com'

  return (
    <aside className="sidebar">
      <strong>Pitchly</strong>
      <nav>
        <NavLink to="/dashboard">
          <span style={{ marginRight: 8 }}>&#x1F4CA;</span>Dashboard
        </NavLink>
        <NavLink to="/modes">
          <span style={{ marginRight: 8 }}>&#x1F3A4;</span>Practice
        </NavLink>
        <NavLink to="/results/demo">
          <span style={{ marginRight: 8 }}>&#x1F4CB;</span>Demo Results
        </NavLink>
        {isAdmin && (
          <NavLink to="/admin">
            <span style={{ marginRight: 8 }}>&#x2699;</span>Admin
          </NavLink>
        )}
      </nav>
    </aside>
  )
}
