// Responsibility: Admin dashboard — view all users, sessions, results, stats.
import { useEffect, useState } from 'react'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { Skeleton } from '../components/ui/Skeleton'
import { api } from '../services/api'

type AdminStats = {
  total_users: number
  total_sessions: number
  completed_sessions: number
  error_sessions: number
  processing_sessions: number
  average_score: number
  total_analyses: number
}

type AdminUser = {
  id: string
  full_name: string
  email: string
  total_sessions: number
  avg_global_score: number
  best_score: number
  interview_sessions: number
  social_sessions: number
  streak_days: number
  created_at: string
  last_session_at: string | null
}

type AdminSession = {
  id: string
  user_id: string
  mode: string
  job_title: string | null
  scenario: string | null
  status: string
  processing_stage: string
  completion_pct: number
  created_at: string
  completed_at: string | null
}

type Tab = 'overview' | 'users' | 'sessions'

export function Admin() {
  const [tab, setTab] = useState<Tab>('overview')
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [users, setUsers] = useState<AdminUser[]>([])
  const [sessions, setSessions] = useState<AdminSession[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    Promise.all([
      api.getAdminStats().then(r => setStats(r.data)),
      api.getAdminUsers().then(r => setUsers(r.data.users)),
      api.getAdminSessions(100).then(r => setSessions(r.data.sessions)),
    ])
      .catch(() => setError('Failed to load admin data. Make sure you are logged in as admin.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <PageWrapper>
      <main className="page">
        <h1 style={{ marginBottom: 4 }}>Admin Dashboard</h1>
        <p className="muted" style={{ marginBottom: 24 }}>Pitchly system overview</p>

        <div className="admin-tabs">
          <button className={`admin-tab ${tab === 'overview' ? 'active' : ''}`} onClick={() => setTab('overview')}>Overview</button>
          <button className={`admin-tab ${tab === 'users' ? 'active' : ''}`} onClick={() => setTab('users')}>Users ({users.length})</button>
          <button className={`admin-tab ${tab === 'sessions' ? 'active' : ''}`} onClick={() => setTab('sessions')}>Sessions ({sessions.length})</button>
        </div>

        {error ? <p className="error" style={{ margin: '16px 0' }}>{error}</p> : null}

        {loading ? (
          <div style={{ display: 'grid', gap: 16 }}>
            <Skeleton className="skeleton-title" />
            <Skeleton className="skeleton-line" />
          </div>
        ) : tab === 'overview' ? (
          <div>
            {stats && (
              <div className="score-grid" style={{ gridTemplateColumns: 'repeat(4, minmax(140px, 1fr))' }}>
                <Card><span>Total Users</span><strong>{stats.total_users}</strong></Card>
                <Card><span>Total Sessions</span><strong>{stats.total_sessions}</strong></Card>
                <Card><span>Completed</span><strong style={{ color: 'var(--green)' }}>{stats.completed_sessions}</strong></Card>
                <Card><span>Errors</span><strong style={{ color: 'var(--red)' }}>{stats.error_sessions}</strong></Card>
                <Card><span>Avg Score</span><strong>{stats.average_score}</strong></Card>
                <Card><span>Total Analyses</span><strong>{stats.total_analyses}</strong></Card>
                <Card><span>Processing</span><strong style={{ color: 'var(--amber)' }}>{stats.processing_sessions}</strong></Card>
              </div>
            )}
          </div>
        ) : tab === 'users' ? (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Sessions</th>
                  <th>Avg Score</th>
                  <th>Best</th>
                  <th>Streak</th>
                  <th>Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td><strong>{u.full_name}</strong></td>
                    <td className="muted">{u.email}</td>
                    <td>{u.total_sessions}</td>
                    <td><strong style={{ color: 'var(--green)' }}>{u.avg_global_score}</strong></td>
                    <td>{u.best_score}</td>
                    <td>{u.streak_days}d</td>
                    <td className="muted">{new Date(u.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
                {users.length === 0 && <tr><td colSpan={7} className="muted" style={{ textAlign: 'center', padding: 24 }}>No users yet</td></tr>}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Mode</th>
                  <th>Context</th>
                  <th>Stage</th>
                  <th>Progress</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map(s => (
                  <tr key={s.id}>
                    <td>
                      <Badge>{s.status}</Badge>
                    </td>
                    <td>{s.mode}</td>
                    <td className="muted">{s.job_title ?? s.scenario ?? '-'}</td>
                    <td className="muted">{s.processing_stage}</td>
                    <td>
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${s.completion_pct}%` }} />
                      </div>
                      <span className="muted" style={{ fontSize: '0.75rem' }}>{s.completion_pct}%</span>
                    </td>
                    <td className="muted">{new Date(s.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
                {sessions.length === 0 && <tr><td colSpan={6} className="muted" style={{ textAlign: 'center', padding: 24 }}>No sessions yet</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </PageWrapper>
  )
}
