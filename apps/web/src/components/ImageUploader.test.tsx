import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import ImageUploader from "./ImageUploader"

class FakeImage {
  width = 100
  height = 100
  onload: (() => void) | null = null
  onerror: (() => void) | null = null

  set src(_value: string) {
    queueMicrotask(() => this.onload?.())
  }
}

const alertMock = vi.fn()

beforeEach(() => {
  vi.stubGlobal("Image", FakeImage)
  vi.stubGlobal("alert", alertMock)
  Object.defineProperty(URL, "createObjectURL", {
    configurable: true,
    value: vi.fn(() => "blob:mock"),
  })
})

afterEach(() => {
  alertMock.mockReset()
  vi.unstubAllGlobals()
})

function getFileInput(container: HTMLElement): HTMLInputElement {
  return container.querySelector('input[type="file"]') as HTMLInputElement
}

describe("ImageUploader", () => {
  it("renders the dropzone", () => {
    render(<ImageUploader onUpload={() => {}} />)

    expect(screen.getByText("Drop an image here")).toBeDefined()
  })

  it("ignores non-image files", () => {
    const onUpload = vi.fn()
    const { container } = render(<ImageUploader onUpload={onUpload} />)

    fireEvent.change(getFileInput(container), {
      target: { files: [new File(["x"], "a.txt", { type: "text/plain" })] },
    })

    expect(onUpload).not.toHaveBeenCalled()
  })

  it("rejects files larger than 10MB", () => {
    const onUpload = vi.fn()
    const { container } = render(<ImageUploader onUpload={onUpload} />)
    const tooBig = new File([new ArrayBuffer(10 * 1024 * 1024 + 1)], "big.png", {
      type: "image/png",
    })

    fireEvent.change(getFileInput(container), {
      target: { files: [tooBig] },
    })

    expect(alertMock).toHaveBeenCalled()
    expect(onUpload).not.toHaveBeenCalled()
  })

  it("passes small images through to onUpload", async () => {
    const onUpload = vi.fn()
    const { container } = render(<ImageUploader onUpload={onUpload} />)
    const file = new File(["x"], "small.png", { type: "image/png" })

    fireEvent.change(getFileInput(container), {
      target: { files: [file] },
    })

    await waitFor(() => expect(onUpload).toHaveBeenCalledWith(file))
  })
})
