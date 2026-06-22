// Responsibility: Provide primary authenticated navigation.
import { NavLink } from 'react-router-dom'

export function Sidebar() {
  return (
    <aside className="sidebar">
      <strong>Pitchly</strong>
      <nav>
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/modes">Practice</NavLink>
        <NavLink to="/results/demo">Results</NavLink>
      </nav>
    </aside>
  )
}
