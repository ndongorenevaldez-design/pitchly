// Responsibility: Show user progress and recent sessions.
import { useEffect, useState } from 'react'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { Skeleton } from '../components/ui/Skeleton'
import { api } from '../services/api'

type DashboardSession = {
  id: string
  mode: string
  job_title?: string | null
  scenario?: string | null
  status: string
}

type DashboardData = {
  profile?: {
    total_sessions?: number
    avg_global_score?: number
    extraversion_score?: number
  } | null
  sessions: DashboardSession[]
}

export function Dashboard() {
  const [state, setState] = useState<{
    status: 'loading' | 'success' | 'error'
    data: DashboardData | null
  }>({ status: 'loading', data: null })

  useEffect(() => {
    api
      .getDashboard()
      .then(({ data }) => setState({ status: 'success', data }))
      .catch(() => setState({ status: 'error', data: null }))
  }, [])

  return (
    <PageWrapper>
      <main className="page">
        <h1>Dashboard</h1>
        {state.status === 'loading' ? <Skeleton className="skeleton-title" /> : null}
        <div className="score-grid">
          <Card>
            <span>Total sessions</span>
            <strong>{state.data?.profile?.total_sessions ?? 0}</strong>
          </Card>
          <Card>
            <span>Average score</span>
            <strong>{state.data?.profile?.avg_global_score ?? 0}</strong>
          </Card>
          <Card>
            <span>Extraversion</span>
            <strong>{state.data?.profile?.extraversion_score ?? 0}</strong>
          </Card>
        </div>
        <section className="history">
          <h2>Recent sessions</h2>
          {(state.data?.sessions ?? []).map((session) => (
            <Card key={session.id}>
              <Badge>{session.mode}</Badge>
              <span>{session.job_title ?? session.scenario}</span>
              <strong>{session.status}</strong>
            </Card>
          ))}
          {state.status === 'error' ? <p className="muted">Connect Supabase to load history.</p> : null}
        </section>
      </main>
    </PageWrapper>
  )
}
