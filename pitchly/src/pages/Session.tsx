// Responsibility: Record webcam practice and start backend processing.
import { useCallback, useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { PageWrapper } from '../components/layout/PageWrapper'
import { RecordingControls } from '../components/webcam/RecordingControls'
import { WebcamView } from '../components/webcam/WebcamView'
import { MAX_RECORDING_SECONDS } from '../constants'
import { useRecorder } from '../hooks/useRecorder'
import { api } from '../services/api'

const SESSION_STORAGE_KEY = 'pitchly_session_config'

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function getPersistedConfig() {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

export function Session() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const recorder = useRecorder()
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [cameraReady, setCameraReady] = useState(false)
  const [cameraError, setCameraError] = useState('')
  const [questions, setQuestions] = useState<string[]>([])
  const [loadingQuestions, setLoadingQuestions] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const sessionConfig = state ?? getPersistedConfig() ?? { mode: 'interview', durationS: 120 }

  useEffect(() => {
    if (state) {
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(state))
    }
  }, [state])

  useEffect(() => {
    setLoadingQuestions(true)
    api.generateQuestions(sessionConfig)
      .then(({ data }) => setQuestions(data.questions || []))
      .catch(() => setQuestions([]))
      .finally(() => setLoadingQuestions(false))
  }, [sessionConfig.mode, sessionConfig.jobTitle, sessionConfig.scenario])

  useEffect(() => {
    let active = true
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      .then((s) => {
        if (active) {
          setCameraReady(true)
          recorder.setInitialStream(s)
        } else {
          s.getTracks().forEach(t => t.stop())
        }
      })
      .catch(() => {
        if (active) setCameraError('Camera access is required. Please allow camera and microphone permissions in your browser settings, then refresh this page.')
      })
    return () => { active = false }
  }, [])

  const handleUpload = useCallback(async (blob: Blob) => {
    setError('')
    setUploading(true)
    try {
      const { data } = await api.analyzeSession({ ...sessionConfig, questions })
      const formData = new FormData()
      formData.append('video', blob, 'pitchly-session.webm')
      await api.uploadVideo(data.session_id, formData)
      navigate('/processing', { state: { jobId: data.job_id } })
    } catch {
      setError('Upload failed. Please try again.')
      setUploading(false)
    }
  }, [sessionConfig, navigate, questions])

  useEffect(() => {
    if (recorder.status === 'recording') {
      timerRef.current = setInterval(() => {
        setElapsed((prev) => {
          const next = prev + 1
          if (next >= MAX_RECORDING_SECONDS) {
            if (timerRef.current) clearInterval(timerRef.current)
            recorder.stop().then(handleUpload)
          }
          return next
        })
      }, 1000)
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [recorder.status, handleUpload, recorder])

  async function stopAndUpload() {
    const blob = await recorder.stop()
    await handleUpload(blob)
  }

  return (
    <PageWrapper>
      <main className="session-page">
        <WebcamView stream={recorder.stream} />
        <section className="session-side">
          <h1>Practice room</h1>
          <p>{sessionConfig.jobTitle ?? sessionConfig.scenario ?? 'Speak naturally for two minutes.'}</p>

          <div className="timer-bar">
            <span className="timer">{formatTime(elapsed)}</span>
            <span className="timer-limit">/ {formatTime(MAX_RECORDING_SECONDS)}</span>
          </div>

          {questions.length > 0 && (
            <div className="questions-panel">
              <h3>Answer these questions:</h3>
              <ol>
                {questions.map((q, i) => (
                  <li key={i} className={i === 0 ? 'current-question' : ''}>{q}</li>
                ))}
              </ol>
            </div>
          )}
          {loadingQuestions && <p className="muted">Loading questions...</p>}

          {cameraError ? (
            <div className="camera-error-box">
              <p className="error">{cameraError}</p>
              <button className="btn btn-secondary" onClick={() => window.location.reload()}>Retry</button>
            </div>
          ) : (
            <RecordingControls
              status={recorder.status}
              onStart={() => recorder.start().catch(() => setError('Camera access failed. Please allow permissions and refresh.'))}
              onStop={() => stopAndUpload().catch(() => setError('Upload failed'))}
              disabled={uploading || (!cameraReady && !cameraError)}
            />
          )}
          {uploading ? <p className="muted">Uploading your recording...</p> : null}
          {error ? <p className="error">{error}</p> : null}
        </section>
      </main>
    </PageWrapper>
  )
}
