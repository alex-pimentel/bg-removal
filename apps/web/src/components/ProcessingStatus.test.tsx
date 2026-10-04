import { render, screen, waitFor } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import ProcessingStatus from "./ProcessingStatus"

vi.mock("../lib/api", () => ({
  getTaskStatus: vi.fn().mockResolvedValue({
    task_id: "abc",
    status: "SUCCESS",
    result: "completed",
  }),
}))

describe("ProcessingStatus", () => {
  it("shows the initial uploading phase", () => {
    render(<ProcessingStatus taskId="abc" onComplete={() => {}} />)

    expect(screen.getByText("Uploading...")).toBeDefined()
  })

  it("calls onComplete once the task succeeds", async () => {
    const onComplete = vi.fn()

    render(<ProcessingStatus taskId="abc" onComplete={onComplete} />)

    await waitFor(() => expect(onComplete).toHaveBeenCalledWith("abc"), {
      timeout: 3000,
    })
  })
})
