// Responsibility: Poll analysis job status until completion or failure.
import { useEffect } from 'react'
import { POLLING_INTERVAL_MS } from '../constants'
import { api } from '../services/api'

export function usePolling(
  jobId: string | null,
  onComplete: (sessionId: string | null, error?: string) => void,
) {
  useEffect(() => {
    if (!jobId) return
    const interval = window.setInterval(async () => {
      const { data } = await api.getStatus(jobId)
      if (data.status === 'complete') {
        window.clearInterval(interval)
        onComplete(data.session_id)
      }
      if (data.status === 'error') {
        window.clearInterval(interval)
        onComplete(null, data.error)
      }
    }, POLLING_INTERVAL_MS)
    return () => window.clearInterval(interval)
  }, [jobId, onComplete])
}
