import { useState } from "react"
import ImageUploader from "../components/ImageUploader"
import ImagePreview from "../components/ImagePreview"
import ProcessingStatus from "../components/ProcessingStatus"

export default function Home() {
  const [taskId, setTaskId] = useState<string | null>(null)
  const [image, setImage] = useState<string | null>(null)
  const [resultUrl, setResultUrl] = useState<string | null>(null)

  const handleUpload = async (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => setImage(e.target?.result as string)
    reader.readAsDataURL(file)

    const { uploadImage } = await import("../lib/api")
    const response = await uploadImage(file)
    setTaskId(response.task_id)
  }

  const handleComplete = (completedTaskId: string) => {
    const base = import.meta.env.VITE_API_URL || "/api"
    setResultUrl(`${base}/tasks/${completedTaskId}/result`)
  }

  const handleReset = () => {
    setTaskId(null)
    setImage(null)
    setResultUrl(null)
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        {!image && !taskId && !resultUrl && (
          <ImageUploader onUpload={handleUpload} />
        )}

        {taskId && !resultUrl && (
          <ProcessingStatus taskId={taskId} onComplete={handleComplete} />
        )}

        {resultUrl && image && (
          <ImagePreview
            original={image}
            resultUrl={resultUrl}
            onReset={handleReset}
          />
        )}
      </div>
    </div>
  )
}
