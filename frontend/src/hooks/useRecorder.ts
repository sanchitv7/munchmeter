import { useState, useRef, useCallback } from 'react'

export function useRecorder() {
  const [isRecording, setIsRecording] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const mediaRecorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])
  const timer = useRef<number | null>(null)

  const start = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    chunks.current = []

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.current.push(e.data)
    }

    mediaRecorder.current = recorder
    recorder.start()
    setIsRecording(true)
    setElapsed(0)

    const startTime = Date.now()
    timer.current = window.setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)
  }, [])

  const stop = useCallback((): Promise<Blob> => {
    return new Promise((resolve) => {
      const recorder = mediaRecorder.current
      if (!recorder) return

      recorder.onstop = () => {
        const blob = new Blob(chunks.current, { type: 'audio/webm' })
        // Stop all tracks to release microphone
        recorder.stream.getTracks().forEach(t => t.stop())
        resolve(blob)
      }

      recorder.stop()
      setIsRecording(false)
      if (timer.current) {
        clearInterval(timer.current)
        timer.current = null
      }
    })
  }, [])

  return { isRecording, elapsed, start, stop }
}
