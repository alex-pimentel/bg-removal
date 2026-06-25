const API_BASE = import.meta.env.VITE_API_URL || "/api"

export interface TaskResponse {
  task_id: string
}

export interface TaskStatusResponse {
  task_id: string
  status: string
  result: string | null
}

export async function uploadImage(file: File): Promise<TaskResponse> {
  const formData = new FormData()
  formData.append("file", file)

  const res = await fetch(`${API_BASE}/remove-bg/`, {
    method: "POST",
    body: formData,
  })

  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `Upload failed: ${res.statusText}`)
  }

  return res.json()
}

export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/status`)
  if (!res.ok) throw new Error("Failed to get task status")
  return res.json()
}
