// Responsibility: Show analysis progress while polling backend job status.
import { useCallback, useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { PageWrapper } from '../components/layout/PageWrapper'
import { usePolling } from '../hooks/usePolling'

const STEPS = [
  'Extracting audio from recording',
  'Transcribing speech with AI',
  'Analyzing posture and expressions',
  'Generating coaching feedback',
]

export function Processing() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [elapsed, setElapsed] = useState(0)
  const startTimeRef = useRef(Date.now())

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTimeRef.current) / 1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const complete = useCallback(
    (sessionId: string | null, jobError?: string) => {
      if (!sessionId) setError(jobError ?? 'Analysis failed')
      else navigate(`/results/${sessionId}`, { replace: true })
    },
    [navigate],
  )

  usePolling(state?.jobId ?? null, complete)

  const activeStep = elapsed < 8 ? 0 : elapsed < 20 ? 1 : elapsed < 40 ? 2 : 3

  return (
    <PageWrapper>
      <main className="page narrow">
        <h1>Analyzing your session</h1>
        <p className="muted">Elapsed: {elapsed}s</p>
        <ol className="steps">
          {STEPS.map((step, i) => (
            <li key={step} className={i <= activeStep ? 'step-active' : 'step-pending'}>
              <span className={`step-dot ${i < activeStep ? 'done' : i === activeStep ? 'active' : ''}`} />
              {step}
            </li>
          ))}
        </ol>
        {error ? (
          <div className="empty-state">
            <p className="error">{error}</p>
            <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
          </div>
        ) : null}
      </main>
    </PageWrapper>
  )
}
