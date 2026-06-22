// Responsibility: Record webcam practice and start backend processing.
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { PageWrapper } from '../components/layout/PageWrapper'
import { RecordingControls } from '../components/webcam/RecordingControls'
import { WebcamView } from '../components/webcam/WebcamView'
import { useRecorder } from '../hooks/useRecorder'
import { api } from '../services/api'

export function Session() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const recorder = useRecorder()
  const [error, setError] = useState('')

  async function stopAndUpload() {
    setError('')
    const blob = await recorder.stop()
    const { data } = await api.analyzeSession(state ?? { mode: 'interview', durationS: 120 })
    const formData = new FormData()
    formData.append('video', blob, 'pitchly-session.webm')
    await api.uploadVideo(data.session_id, formData)
    navigate('/processing', { state: { jobId: data.job_id } })
  }

  return (
    <PageWrapper>
      <main className="session-page">
        <WebcamView stream={recorder.stream} />
        <section className="session-side">
          <h1>Practice room</h1>
          <p>{state?.jobTitle ?? state?.scenario ?? 'Speak naturally for two minutes.'}</p>
          <RecordingControls
            status={recorder.status}
            onStart={() => recorder.start().catch(() => setError('Camera access failed'))}
            onStop={() => stopAndUpload().catch(() => setError('Upload failed'))}
          />
          {error ? <p className="error">{error}</p> : null}
        </section>
      </main>
    </PageWrapper>
  )
}
