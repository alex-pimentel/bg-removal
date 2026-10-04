import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"
import ImagePreview from "./ImagePreview"

function stubObjectUrl() {
  Object.defineProperty(URL, "createObjectURL", {
    configurable: true,
    value: vi.fn(() => "blob:mock"),
  })
  Object.defineProperty(URL, "revokeObjectURL", {
    configurable: true,
    value: vi.fn(),
  })
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe("ImagePreview", () => {
  it("renders the original and result images", () => {
    render(<ImagePreview original="a.png" resultUrl="b.png" onReset={() => {}} />)

    expect(screen.getByAltText("Original")).toBeDefined()
    expect(screen.getByAltText("Result")).toBeDefined()
  })

  it("calls onReset when remove another is clicked", () => {
    const onReset = vi.fn()
    render(<ImagePreview original="a.png" resultUrl="b.png" onReset={onReset} />)

    fireEvent.click(screen.getByText("Remove another"))

    expect(onReset).toHaveBeenCalledOnce()
  })

  it("downloads the result as a png blob", async () => {
    const blob = new Blob(["data"], { type: "image/png" })
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, blob: async () => blob })
    vi.stubGlobal("fetch", fetchMock)
    stubObjectUrl()
    const clickSpy = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => {})

    render(<ImagePreview original="a.png" resultUrl="b.png" onReset={() => {}} />)
    fireEvent.click(screen.getByText("Download PNG"))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("b.png"))
    expect(clickSpy).toHaveBeenCalled()
  })

  it("logs an error when the download request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false }))
    stubObjectUrl()
    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {})

    render(<ImagePreview original="a.png" resultUrl="b.png" onReset={() => {}} />)
    fireEvent.click(screen.getByText("Download PNG"))

    await waitFor(() => expect(errorSpy).toHaveBeenCalled())
  })
})
