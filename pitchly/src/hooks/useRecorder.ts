// Responsibility: Isolate MediaRecorder webcam and microphone logic.
import { useRef, useState } from 'react'

export function useRecorder() {
  const [status, setStatus] = useState<'idle' | 'recording' | 'stopped'>('idle')
  const [stream, setStream] = useState<MediaStream | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])

  async function start() {
    const nextStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    })
    chunksRef.current = []
    const recorder = new MediaRecorder(nextStream)
    recorder.ondataavailable = (event) => chunksRef.current.push(event.data)
    recorder.start()
    recorderRef.current = recorder
    setStream(nextStream)
    setStatus('recording')
  }

  function stop() {
    return new Promise<Blob>((resolve) => {
      const recorder = recorderRef.current
      if (!recorder) resolve(new Blob([], { type: 'video/webm' }))
      recorder!.onstop = () => {
        stream?.getTracks().forEach((track) => track.stop())
        setStatus('stopped')
        resolve(new Blob(chunksRef.current, { type: 'video/webm' }))
      }
      recorder!.stop()
    })
  }

  return { status, stream, start, stop }
}
