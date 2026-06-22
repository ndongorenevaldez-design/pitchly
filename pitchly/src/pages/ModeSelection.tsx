// Responsibility: Let users choose the communication practice mode.
import { Link } from 'react-router-dom'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Card } from '../components/ui/Card'

export function ModeSelection() {
  return (
    <PageWrapper>
      <main className="page">
        <h1>Choose practice mode</h1>
        <div className="two-grid">
          <Link to="/interview-setup">
            <Card className="mode-card">
              <h2>Interview Mode</h2>
              <p>Practice role-specific answers with clarity and structure scoring.</p>
            </Card>
          </Link>
          <Link to="/social-setup">
            <Card className="mode-card">
              <h2>Social Mode</h2>
              <p>Build confidence in everyday conversations and group speaking.</p>
            </Card>
          </Link>
        </div>
      </main>
    </PageWrapper>
  )
}
