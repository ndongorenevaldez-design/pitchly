// Responsibility: Show an individual score with visual emphasis.
import { Card } from '../ui/Card'

export function ScoreCard({ label, value }: { label: string; value: number }) {
  return (
    <Card className="score-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </Card>
  )
}
