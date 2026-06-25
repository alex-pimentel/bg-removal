import { useEffect, useState } from "react"
import { Loader2 } from "lucide-react"
import { getTaskStatus } from "../lib/api"

interface Props {
  taskId: string
  onComplete: (taskId: string) => void
}

type Phase = "uploading" | "queued" | "processing" | "done" | "error"

const STATUS_MAP: Record<string, Phase> = {
  PENDING: "queued",
  STARTED: "processing",
  SUCCESS: "done",
  FAILURE: "error",
}

const PHASE_LABELS: Record<Phase, { title: string; description: string }> = {
  uploading: { title: "Uploading...", description: "Sending image to server" },
  queued: { title: "In queue", description: "Waiting for a worker" },
  processing: { title: "Processing", description: "Removing background" },
  done: { title: "Complete!", description: "Your image is ready" },
  error: {
    title: "Processing failed",
    description: "Something went wrong. Try again.",
  },
}

export default function ProcessingStatus({ taskId, onComplete }: Props) {
  const [phase, setPhase] = useState<Phase>("uploading")

  useEffect(() => {
    let cancelled = false

    const poll = async () => {
      setPhase("uploading")
      await new Promise((r) => setTimeout(r, 500))

      while (!cancelled) {
        try {
          const data = await getTaskStatus(taskId)
          if (cancelled) break

          const newPhase = STATUS_MAP[data.status] ?? "queued"
          setPhase(newPhase)

          if (newPhase === "done") {
            onComplete(taskId)
            break
          }
          if (newPhase === "error") break
        } catch {
          if (!cancelled) setPhase("error")
        }

        await new Promise((r) => setTimeout(r, 1000))
      }
    }

    poll()
    return () => {
      cancelled = true
    }
  }, [taskId, onComplete])

  const current = PHASE_LABELS[phase]

  return (
    <div className="flex flex-col items-center justify-center p-16">
      {phase !== "error" && (
        <Loader2 className="mb-4 h-12 w-12 animate-spin text-blue-500" />
      )}
      <p className="text-lg font-medium text-slate-700">{current.title}</p>
      <p className="mt-1 text-sm text-slate-500">{current.description}</p>
    </div>
  )
}
