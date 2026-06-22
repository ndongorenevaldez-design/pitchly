// Responsibility: Display scores and personalized feedback.
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { FeedbackPanel } from '../components/feedback/FeedbackPanel'
import { RadarChart } from '../components/feedback/RadarChart'
import { ScoreCard } from '../components/feedback/ScoreCard'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Skeleton } from '../components/ui/Skeleton'
import { api } from '../services/api'

const demo = {
  score_clarity: 82,
  score_confidence: 76,
  score_structure: 79,
  score_relevance: 84,
  score_listening: 80,
  feedback_text: 'Demo feedback: add one concrete example and close with confidence.',
  posture_notes: 'Stable posture and good camera framing.',
}

type ResultData = typeof demo

function getInitialState(sessionId?: string) {
  if (sessionId === 'demo') return { status: 'success' as const, data: demo }
  return { status: 'loading' as const, data: demo }
}

export function Results() {
  const { sessionId } = useParams()
  const [state, setState] = useState<{
    status: 'loading' | 'success'
    data: ResultData
  }>(() => getInitialState(sessionId))

  useEffect(() => {
    if (sessionId === 'demo') return
    api
      .getResults(sessionId ?? '')
      .then(({ data }) => setState({ status: 'success', data: data.result }))
      .catch(() => setState({ status: 'success', data: demo }))
  }, [sessionId])

  const result = state.data
  const scores = {
    Clarity: result.score_clarity,
    Confidence: result.score_confidence,
    Structure: result.score_structure,
    Relevance: result.score_relevance,
    Listening: result.score_listening,
  }

  return (
    <PageWrapper>
      <main className="page">
        <h1>Session results</h1>
        {state.status === 'loading' ? <Skeleton className="skeleton-title" /> : null}
        <div className="results-grid">
          <RadarChart scores={scores} />
          <FeedbackPanel text={result.feedback_text} notes={result.posture_notes} />
        </div>
        <div className="score-grid">
          {Object.entries(scores).map(([label, value]) => (
            <ScoreCard key={label} label={label} value={value} />
          ))}
        </div>
      </main>
    </PageWrapper>
  )
}
