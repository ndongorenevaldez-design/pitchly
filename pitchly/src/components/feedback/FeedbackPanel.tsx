// Responsibility: Present personalized coaching feedback.
import { Card } from '../ui/Card'

export function FeedbackPanel({ text, notes }: { text: string; notes?: string }) {
  return (
    <Card className="feedback-panel">
      <h2>Coach feedback</h2>
      <p>{text}</p>
      {notes ? <p className="muted">{notes}</p> : null}
    </Card>
  )
}
