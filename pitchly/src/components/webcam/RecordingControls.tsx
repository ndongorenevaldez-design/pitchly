// Responsibility: Render start and stop controls for recording.
import { Button } from '../ui/Button'

export function RecordingControls({
  status,
  onStart,
  onStop,
  disabled,
}: {
  status: string
  onStart: () => void
  onStop: () => void
  disabled?: boolean
}) {
  return (
    <div className="recording-controls">
      {status !== 'recording' ? (
        <Button onClick={onStart} disabled={disabled} icon={<span className="rec-dot" />}>
          Start
        </Button>
      ) : (
        <Button variant="danger" onClick={onStop} disabled={disabled} icon={<span className="stop-icon" />}>
          Stop
        </Button>
      )}
      <div className={`waveform ${status}`}>
        <i />
        <i />
        <i />
        <i />
      </div>
    </div>
  )
}
