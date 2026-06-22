// Responsibility: Show analysis progress while polling backend job status.
import { useCallback, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Skeleton } from '../components/ui/Skeleton'
import { usePolling } from '../hooks/usePolling'

export function Processing() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [error, setError] = useState('')

  const complete = useCallback(
    (sessionId: string | null, jobError?: string) => {
      if (!sessionId) setError(jobError ?? 'Analysis failed')
      else navigate(`/results/${sessionId}`, { replace: true })
    },
    [navigate],
  )

  usePolling(state?.jobId ?? null, complete)

  return (
    <PageWrapper>
      <main className="page narrow">
        <h1>Analyzing your session</h1>
        <Skeleton className="skeleton-title" />
        <ol className="steps">
          <li>Extracting audio</li>
          <li>Reading posture and expression signals</li>
          <li>Generating coaching feedback</li>
        </ol>
        {error ? <p className="error">{error}</p> : null}
      </main>
    </PageWrapper>
  )
}
