const API_BASE = import.meta.env.VITE_API_URL || "/api"

export interface TaskResponse {
  task_id: string
}

export interface TaskStatusResponse {
  task_id: string
  status: string
  result: string | null
}

function authHeaders(token?: string | null): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function uploadImage(
  file: File,
  token?: string | null,
): Promise<TaskResponse> {
  const formData = new FormData()
  formData.append("file", file)

  const res = await fetch(`${API_BASE}/remove-bg/`, {
    method: "POST",
    headers: authHeaders(token),
    body: formData,
  })

  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || `Upload failed: ${res.statusText}`)
  }

  return res.json()
}

export async function getTaskStatus(
  taskId: string,
  token?: string | null,
): Promise<TaskStatusResponse> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/status`, {
    headers: authHeaders(token),
  })
  if (!res.ok) throw new Error("Failed to get task status")
  return res.json()
}

export function getResultUrl(taskId: string): string {
  return `${API_BASE}/tasks/${taskId}/result`
}
