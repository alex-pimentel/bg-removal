export interface TaskResponse {
  task_id: string
}

export interface TaskStatusResponse {
  task_id: string
  status: "PENDING" | "STARTED" | "SUCCESS" | "FAILURE"
  result: string | null
}
