// Responsibility: Display the active MediaStream without unnecessary rerenders.
import { memo, useEffect, useRef } from 'react'

function WebcamViewComponent({ stream }: { stream: MediaStream | null }) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (videoRef.current) videoRef.current.srcObject = stream
  }, [stream])

  return (
    <div className="webcam-frame">
      <video ref={videoRef} autoPlay muted playsInline />
      {!stream ? <div className="camera-empty">Camera preview</div> : null}
    </div>
  )
}

export const WebcamView = memo(WebcamViewComponent)
