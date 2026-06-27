// Responsibility: Display comprehensive AI coaching report.
import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { FeedbackPanel } from '../components/feedback/FeedbackPanel'
import { RadarChart } from '../components/feedback/RadarChart'
import { ScoreCard } from '../components/feedback/ScoreCard'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Skeleton } from '../components/ui/Skeleton'
import { api } from '../services/api'

type ResultData = {
  score_clarity: number
  score_confidence: number
  score_structure: number
  score_relevance: number
  score_listening: number
  score_global: number
  feedback_text: string
  posture_notes: string
  transcript: string
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  practice_exercises: string[]
  filler_words_detected: string
  speech_pace: string
  opening_quality: string
  closing_quality: string
  vocabulary_assessment: string
  body_language: {
    posture_score: number
    gesture_frequency: number
    shoulder_stability: number
    centered_score: number
  }
  facial_expression: {
    engagement_score: number
    confidence_score: number
    stress_level: number
    smile_ratio: number
    dominant_emotion: string
    emotion_distribution: { positive: number; neutral: number; negative: number }
    emotion_timeline: Array<{ start_pct: number; end_pct: number; emotion: string }>
  }
  audio_quality: {
    duration_s: number
    avg_volume_db: number
    silence_ratio: number
    dynamic_range_db: number
    volume_assessment: string
    silence_assessment: string
  }
  transcript_metadata: {
    words_per_minute: number
    filler_count: number
    filler_percentage: number
    pace_assessment: string
    language: string
  }
}

const emotionColors: Record<string, string> = {
  happy: '#00e5a0', neutral: '#4f8ef7', sad: '#6b8bbd',
  angry: '#ff5c7a', fear: '#f7a84f', surprise: '#c084fc',
  disgust: '#a3a3a3',
}

const emptyResult: ResultData = {
  score_clarity: 0, score_confidence: 0, score_structure: 0,
  score_relevance: 0, score_listening: 0, score_global: 0,
  feedback_text: '', posture_notes: '', transcript: '',
  strengths: [], weaknesses: [], recommendations: [], practice_exercises: [],
  filler_words_detected: '', speech_pace: '', opening_quality: '',
  closing_quality: '', vocabulary_assessment: '',
  body_language: { posture_score: 0, gesture_frequency: 0, shoulder_stability: 0, centered_score: 0 },
  facial_expression: { engagement_score: 0, confidence_score: 0, stress_level: 0,
    smile_ratio: 0, dominant_emotion: 'neutral',
    emotion_distribution: { positive: 0, neutral: 0, negative: 0 }, emotion_timeline: [] },
  audio_quality: { duration_s: 0, avg_volume_db: 0, silence_ratio: 0,
    dynamic_range_db: 0, volume_assessment: '', silence_assessment: '' },
  transcript_metadata: { words_per_minute: 0, filler_count: 0, filler_percentage: 0,
    pace_assessment: '', language: '' },
}

export function Results() {
  const { sessionId } = useParams()
  const [state, setState] = useState<{
    status: 'loading' | 'success' | 'error' | 'retrying'
    data: ResultData
    retries: number
  }>({ status: 'loading', data: emptyResult, retries: 0 })
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  function fetchData() {
    if (sessionId === 'demo') return
    setState((prev) => ({ ...prev, status: prev.retries === 0 ? 'loading' : 'retrying' }))
    api
      .getResults(sessionId ?? '')
      .then(({ data }) => {
        if (intervalRef.current) clearInterval(intervalRef.current)
        setState({ status: 'success', data: data.result, retries: 0 })
      })
      .catch(() => {
        setState((prev) => {
          const next = prev.retries + 1
          if (next >= 20) {
            if (intervalRef.current) clearInterval(intervalRef.current)
            return { status: 'error', data: emptyResult, retries: 0 }
          }
          return { ...prev, status: 'retrying', retries: next }
        })
      })
  }

  useEffect(() => {
    fetchData()
    intervalRef.current = setInterval(fetchData, 3000)
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [sessionId])

  const result = state.data
  const scores = {
    Clarity: result.score_clarity,
    Confidence: result.score_confidence,
    Structure: result.score_structure,
    Relevance: result.score_relevance,
    Listening: result.score_listening,
  }

  const bl = result.body_language
  const fe = result.facial_expression

  function getGrade(score: number) {
    if (score >= 90) return { grade: 'A+', color: 'var(--green)' }
    if (score >= 80) return { grade: 'A', color: 'var(--green)' }
    if (score >= 70) return { grade: 'B', color: 'var(--blue)' }
    if (score >= 60) return { grade: 'C', color: 'var(--amber)' }
    if (score >= 50) return { grade: 'D', color: 'var(--amber)' }
    return { grade: 'F', color: 'var(--red)' }
  }

  const overall = getGrade(result.score_global)

  return (
    <PageWrapper>
      <main className="page">
        <h1>Session Results</h1>
        {state.status === 'loading' ? (
          <div className="results-loading">
            <Skeleton className="skeleton-title" />
            <Skeleton className="skeleton-line" />
            <Skeleton className="skeleton-line short" />
          </div>
        ) : state.status === 'retrying' ? (
          <div className="results-loading">
            <p className="muted">Results not ready yet. Retrying... ({state.retries}/5)</p>
            <Skeleton className="skeleton-title" />
            <Skeleton className="skeleton-line" />
          </div>
        ) : state.status === 'error' ? (
          <div className="empty-state">
            <p>Could not load results. The analysis may still be processing.</p>
            <Button variant="secondary" onClick={fetchData}>Retry</Button>
            <Link to="/dashboard"><Button variant="ghost">Back to Dashboard</Button></Link>
          </div>
        ) : (
          <>
            <div className="global-score-card">
              <span>Overall AI Score</span>
              <strong>{result.score_global}</strong>
              <span className="grade-badge" style={{ color: overall.color }}>{overall.grade}</span>
            </div>

            <Card className="summary-card">
              <h2>Interview Summary</h2>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Clarity</span>
                  <div className="summary-bar"><div className="summary-fill" style={{ width: `${result.score_clarity}%`, background: 'var(--blue)' }} /></div>
                  <span className="summary-score">{result.score_clarity}/100</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Confidence</span>
                  <div className="summary-bar"><div className="summary-fill" style={{ width: `${result.score_confidence}%`, background: 'var(--green)' }} /></div>
                  <span className="summary-score">{result.score_confidence}/100</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Structure</span>
                  <div className="summary-bar"><div className="summary-fill" style={{ width: `${result.score_structure}%`, background: 'var(--purple)' }} /></div>
                  <span className="summary-score">{result.score_structure}/100</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Relevance</span>
                  <div className="summary-bar"><div className="summary-fill" style={{ width: `${result.score_relevance}%`, background: 'var(--amber)' }} /></div>
                  <span className="summary-score">{result.score_relevance}/100</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Communication</span>
                  <div className="summary-bar"><div className="summary-fill" style={{ width: `${result.score_listening}%`, background: 'var(--green)' }} /></div>
                  <span className="summary-score">{result.score_listening}/100</span>
                </div>
              </div>
              {result.feedback_text && (
                <div className="summary-feedback">
                  <p>{result.feedback_text.split('\n').filter(Boolean).map((line, i) => <span key={i}>{line}<br/></span>)}</p>
                </div>
              )}
            </Card>

            <div className="results-grid">
              <RadarChart scores={scores} />
              <FeedbackPanel text={result.feedback_text} notes={result.posture_notes} />
            </div>

            <div className="score-grid">
              {Object.entries(scores).map(([label, value]) => (
                <ScoreCard key={label} label={label} value={value} />
              ))}
            </div>

            {(result.strengths.length > 0 || result.weaknesses.length > 0) && (
              <div className="two-grid coaching-section">
                {result.strengths.length > 0 && (
                  <Card>
                    <h2>Strengths</h2>
                    <ul className="coaching-list strengths-list">
                      {result.strengths.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </Card>
                )}
                {result.weaknesses.length > 0 && (
                  <Card>
                    <h2>Areas to Improve</h2>
                    <ul className="coaching-list weaknesses-list">
                      {result.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
                    </ul>
                  </Card>
                )}
              </div>
            )}

            {result.recommendations.length > 0 && (
              <Card className="coaching-section">
                <h2>Personalized Recommendations</h2>
                <ul className="coaching-list recommendations-list">
                  {result.recommendations.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </Card>
            )}

            {result.practice_exercises.length > 0 && (
              <Card className="coaching-section">
                <h2>Practice Exercises</h2>
                <ol className="coaching-list exercises-list">
                  {result.practice_exercises.map((e, i) => <li key={i}>{e}</li>)}
                </ol>
              </Card>
            )}

            <div className="two-grid coaching-section">
              <Card>
                <h2>Body Language</h2>
                <div className="metric-grid">
                  <div className="metric"><span>Posture</span><strong>{bl.posture_score}/100</strong></div>
                  <div className="metric"><span>Gestures</span><strong>{bl.gesture_frequency}/min</strong></div>
                  <div className="metric"><span>Stability</span><strong>{bl.shoulder_stability}/100</strong></div>
                  <div className="metric"><span>Centering</span><strong>{bl.centered_score}/100</strong></div>
                </div>
              </Card>
              <Card>
                <h2>Facial Expressions</h2>
                <div className="metric-grid">
                  <div className="metric"><span>Engagement</span><strong>{fe.engagement_score}/100</strong></div>
                  <div className="metric"><span>Confidence</span><strong>{fe.confidence_score}/100</strong></div>
                  <div className="metric"><span>Stress</span><strong>{fe.stress_level}/100</strong></div>
                  <div className="metric"><span>Smile</span><strong>{fe.smile_ratio}%</strong></div>
                </div>
                {fe.dominant_emotion && (
                  <p className="muted" style={{ marginTop: 12 }}>Dominant emotion: {fe.dominant_emotion}</p>
                )}
              </Card>
            </div>

            {fe.emotion_timeline && fe.emotion_timeline.length > 0 && (
              <Card className="coaching-section">
                <h2>Emotion Timeline</h2>
                <div className="emotion-timeline">
                  {fe.emotion_timeline.map((seg, i) => (
                    <div
                      key={i}
                      className="timeline-segment"
                      style={{
                        width: `${seg.end_pct - seg.start_pct}%`,
                        backgroundColor: emotionColors[seg.emotion] || '#4f8ef7',
                      }}
                      title={`${seg.emotion} (${seg.start_pct}%-${seg.end_pct}%)`}
                    >
                      <span className="timeline-label">{seg.emotion}</span>
                    </div>
                  ))}
                </div>
                <div className="emotion-distribution">
                  {fe.emotion_distribution.positive > 0 && (
                    <span className="dist-bar" style={{ width: `${fe.emotion_distribution.positive}%`, backgroundColor: '#00e5a0' }}>
                      {fe.emotion_distribution.positive}% positive
                    </span>
                  )}
                  {fe.emotion_distribution.neutral > 0 && (
                    <span className="dist-bar" style={{ width: `${fe.emotion_distribution.neutral}%`, backgroundColor: '#4f8ef7' }}>
                      {fe.emotion_distribution.neutral}% neutral
                    </span>
                  )}
                  {fe.emotion_distribution.negative > 0 && (
                    <span className="dist-bar" style={{ width: `${fe.emotion_distribution.negative}%`, backgroundColor: '#ff5c7a' }}>
                      {fe.emotion_distribution.negative}% negative
                    </span>
                  )}
                </div>
              </Card>
            )}

            <Card className="coaching-section">
              <h2>Audio Quality</h2>
              <div className="metric-grid">
                {result.audio_quality.duration_s > 0 && <div className="metric"><span>Duration</span><strong>{result.audio_quality.duration_s}s</strong></div>}
                {result.audio_quality.avg_volume_db !== 0 && <div className="metric"><span>Volume</span><strong>{result.audio_quality.avg_volume_db} dB ({result.audio_quality.volume_assessment})</strong></div>}
                {result.audio_quality.silence_ratio > 0 && <div className="metric"><span>Silence</span><strong>{result.audio_quality.silence_ratio}% ({result.audio_quality.silence_assessment})</strong></div>}
                {result.audio_quality.dynamic_range_db > 0 && <div className="metric"><span>Dynamic Range</span><strong>{result.audio_quality.dynamic_range_db} dB</strong></div>}
              </div>
            </Card>

            <Card className="coaching-section">
              <h2>Speech Analysis</h2>
              <div className="metric-grid">
                {result.transcript_metadata.words_per_minute > 0 && <div className="metric"><span>Pace</span><strong>{result.transcript_metadata.words_per_minute} wpm ({result.transcript_metadata.pace_assessment})</strong></div>}
                {result.transcript_metadata.filler_count > 0 && <div className="metric"><span>Fillers</span><strong>{result.transcript_metadata.filler_count} ({result.transcript_metadata.filler_percentage}%)</strong></div>}
                {result.transcript_metadata.language && <div className="metric"><span>Language</span><strong>{result.transcript_metadata.language}</strong></div>}
                {result.opening_quality && <div className="metric"><span>Opening</span><strong>{result.opening_quality}</strong></div>}
                {result.closing_quality && <div className="metric"><span>Closing</span><strong>{result.closing_quality}</strong></div>}
                {result.vocabulary_assessment && <div className="metric"><span>Vocabulary</span><strong>{result.vocabulary_assessment}</strong></div>}
              </div>
            </Card>

            {result.transcript && (
              <Card className="coaching-section">
                <h2>Transcript</h2>
                <p className="transcript-text">{result.transcript}</p>
              </Card>
            )}

            <div className="results-actions">
              <Link to="/modes"><Button>Practice Again</Button></Link>
              <Link to="/dashboard"><Button variant="ghost">Back to Dashboard</Button></Link>
            </div>
          </>
        )}
      </main>
    </PageWrapper>
  )
}
