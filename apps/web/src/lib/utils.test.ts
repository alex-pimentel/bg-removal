import { describe, expect, it } from "vitest"
import { cn } from "./utils"

describe("cn", () => {
  it("joins truthy class names", () => {
    expect(cn("a", "b")).toBe("a b")
  })

  it("filters falsy values", () => {
    expect(cn("a", false, undefined, null, "b")).toBe("a b")
  })

  it("returns an empty string when nothing is provided", () => {
    expect(cn()).toBe("")
  })
})
