import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import App from "./App"

describe("App", () => {
  it("renders the header and footer", () => {
    render(<App />)

    expect(screen.getByText("bg-removal")).toBeDefined()
    expect(screen.getByText("alexwebmaster.com.br")).toBeDefined()
    expect(screen.getByText("Drop an image here")).toBeDefined()
  })
})
