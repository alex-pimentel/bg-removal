import { afterEach, describe, expect, it, vi } from "vitest"
import { getTaskStatus, uploadImage } from "./api"

afterEach(() => {
  vi.unstubAllGlobals()
})

describe("uploadImage", () => {
  it("posts the file and returns the task id", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ task_id: "abc" }) })
    vi.stubGlobal("fetch", fetchMock)

    const file = new File(["x"], "image.png", { type: "image/png" })
    const result = await uploadImage(file)

    expect(result.task_id).toBe("abc")
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/remove-bg/",
      expect.objectContaining({ method: "POST" }),
    )
  })

  it("throws with the response body when the upload fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, text: async () => "nope" }),
    )

    await expect(
      uploadImage(new File(["x"], "image.png", { type: "image/png" })),
    ).rejects.toThrow("nope")
  })
})

describe("getTaskStatus", () => {
  it("returns the parsed status", async () => {
    const payload = { task_id: "abc", status: "SUCCESS", result: "completed" }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: async () => payload }),
    )

    await expect(getTaskStatus("abc")).resolves.toEqual(payload)
  })

  it("throws when the request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false }))

    await expect(getTaskStatus("abc")).rejects.toThrow("Failed to get task status")
  })
})
