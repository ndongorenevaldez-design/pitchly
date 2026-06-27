// Responsibility: Poll analysis job status until completion or failure.
import { useEffect, useRef } from 'react'
import { POLLING_INTERVAL_MS } from '../constants'
import { api } from '../services/api'

const MAX_CONSECUTIVE_ERRORS = 5

export function usePolling(
  jobId: string | null,
  onComplete: (sessionId: string | null, error?: string) => void,
) {
  const errorCountRef = useRef(0)

  useEffect(() => {
    if (!jobId) return
    errorCountRef.current = 0

    const interval = window.setInterval(async () => {
      try {
        const { data } = await api.getStatus(jobId)
        errorCountRef.current = 0

        if (data.status === 'complete') {
          window.clearInterval(interval)
          onComplete(data.session_id)
        } else if (data.status === 'error') {
          window.clearInterval(interval)
          onComplete(null, data.error ?? 'Analysis failed')
        }
      } catch {
        errorCountRef.current += 1
        if (errorCountRef.current >= MAX_CONSECUTIVE_ERRORS) {
          window.clearInterval(interval)
          onComplete(null, 'Lost connection to server. Please try again.')
        }
      }
    }, POLLING_INTERVAL_MS)
    return () => window.clearInterval(interval)
  }, [jobId, onComplete])
}
