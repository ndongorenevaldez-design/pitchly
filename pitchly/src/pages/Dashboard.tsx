// Responsibility: Show user progress and recent sessions.
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Skeleton } from '../components/ui/Skeleton'
import { api } from '../services/api'

type DashboardSession = {
  id: string
  mode: string
  job_title?: string | null
  scenario?: string | null
  status: string
  created_at?: string
}

type DashboardData = {
  profile?: {
    total_sessions?: number
    avg_global_score?: number
    extraversion_score?: number
    best_score?: number
    avg_clarity?: number
    avg_confidence?: number
  } | null
  sessions: DashboardSession[]
}

export function Dashboard() {
  const [state, setState] = useState<{
    status: 'loading' | 'success' | 'error'
    data: DashboardData | null
  }>({ status: 'loading', data: null })

  function fetchData() {
    setState({ status: 'loading', data: null })
    api
      .getDashboard()
      .then(({ data }) => setState({ status: 'success', data }))
      .catch(() => setState({ status: 'error', data: null }))
  }

  useEffect(() => { fetchData() }, [])

  const sessions = state.data?.sessions ?? []
  const profile = state.data?.profile

  return (
    <PageWrapper>
      <main className="page">
        <h1 style={{ marginBottom: 8 }}>Dashboard</h1>
        <p className="muted" style={{ marginBottom: 32 }}>Your communication coaching overview</p>

        {state.status === 'loading' ? (
          <div style={{ display: 'grid', gap: 16 }}>
            <Skeleton className="skeleton-title" />
            <Skeleton className="skeleton-line" />
          </div>
        ) : (
          <>
            <motion.div
              className="score-grid"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <Card>
                <span>Total Sessions</span>
                <strong>{profile?.total_sessions ?? 0}</strong>
              </Card>
              <Card>
                <span>Average Score</span>
                <strong>{profile?.avg_global_score ?? 0}</strong>
              </Card>
              <Card>
                <span>Best Score</span>
                <strong style={{ color: 'var(--amber)' }}>{profile?.best_score ?? 0}</strong>
              </Card>
              <Card>
                <span>Clarity Avg</span>
                <strong>{profile?.avg_clarity ?? 0}</strong>
              </Card>
              <Card>
                <span>Confidence Avg</span>
                <strong>{profile?.avg_confidence ?? 0}</strong>
              </Card>
            </motion.div>

            <section className="history" style={{ marginTop: 32 }}>
              <h2 style={{ marginBottom: 16 }}>Recent Sessions</h2>
              {sessions.length === 0 && state.status === 'success' ? (
                <div className="empty-state">
                  <p style={{ fontSize: '1.1rem', color: 'var(--text-2)' }}>No sessions yet</p>
                  <p>Start your first practice session to see results here.</p>
                  <Link to="/modes"><Button>Start Practice</Button></Link>
                </div>
              ) : (
                sessions.map((session) => {
                  const card = (
                    <Card key={session.id} className={session.status === 'complete' ? 'clickable' : ''}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                        <Badge>{session.mode}</Badge>
                        <strong className={session.status === 'complete' ? 'success' : session.status === 'error' ? 'error' : 'muted'} style={{ fontSize: '0.85rem' }}>
                          {session.status === 'complete' ? 'Completed' : session.status === 'error' ? 'Failed' : 'Processing'}
                        </strong>
                      </div>
                      <span>{session.job_title ?? session.scenario ?? 'Practice session'}</span>
                      {session.created_at && (
                        <span style={{ fontSize: '0.78rem', marginTop: 4, display: 'block' }}>
                          {new Date(session.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </Card>
                  )
                  return session.status === 'complete' ? (
                    <Link to={`/results/${session.id}`} key={session.id}>{card}</Link>
                  ) : (
                    <div key={session.id}>{card}</div>
                  )
                })
              )}
            </section>

            {state.status === 'error' ? (
              <div className="empty-state">
                <p>Failed to load dashboard data.</p>
                <Button variant="secondary" onClick={fetchData}>Retry</Button>
              </div>
            ) : null}
          </>
        )}
      </main>
    </PageWrapper>
  )
}
