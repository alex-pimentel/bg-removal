import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import App from "./App"

describe("App", () => {
  it("renders the service shell navigation and uploader", () => {
    render(<App />)

    expect(screen.getAllByText("Remover fundo").length).toBeGreaterThan(0)
    expect(screen.getByText("Drop an image here")).toBeDefined()
  })
})
