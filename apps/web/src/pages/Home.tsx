import { useState } from "react"
import ImageUploader from "../components/ImageUploader"
import ImagePreview from "../components/ImagePreview"
import ProcessingStatus from "../components/ProcessingStatus"
import { getResultUrl, uploadImage } from "../lib/api"
import { useApiToken } from "../lib/apiToken"

export default function Home() {
  const [taskId, setTaskId] = useState<string | null>(null)
  const [image, setImage] = useState<string | null>(null)
  const [resultUrl, setResultUrl] = useState<string | null>(null)
  const getToken = useApiToken()

  const handleUpload = async (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => setImage(e.target?.result as string)
    reader.readAsDataURL(file)

    const token = await getToken()
    const response = await uploadImage(file, token)
    setTaskId(response.task_id)
  }

  const handleComplete = (completedTaskId: string) => {
    setResultUrl(getResultUrl(completedTaskId))
  }

  const handleReset = () => {
    setTaskId(null)
    setImage(null)
    setResultUrl(null)
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        {!image && !taskId && !resultUrl && <ImageUploader onUpload={handleUpload} />}

        {taskId && !resultUrl && (
          <ProcessingStatus taskId={taskId} onComplete={handleComplete} />
        )}

        {resultUrl && image && (
          <ImagePreview original={image} resultUrl={resultUrl} onReset={handleReset} />
        )}
      </div>
    </div>
  )
}
