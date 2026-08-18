import { afterEach, describe, expect, test } from "bun:test"
import { normalizeHttpUrl, normalizeJobDetailInput } from "../src/commands/detail"
import { htmlFetch } from "../src/helpers"

const originalFetch = globalThis.fetch

afterEach(() => {
  globalThis.fetch = originalFetch
})

describe("Jobindex detail input boundary", () => {
  test("normalizes only safe HTTP(S) URLs emitted from untrusted HTML", () => {
    expect(normalizeHttpUrl("/c?t=abc&amp;x=1")).toBe("https://www.jobindex.dk/c?t=abc&x=1")
    expect(normalizeHttpUrl("https://ats.example/apply")).toBe("https://ats.example/apply")
    expect(normalizeHttpUrl("javascript:alert(1)")).toBeNull()
    expect(normalizeHttpUrl("data:text/plain,no")).toBeNull()
    expect(normalizeHttpUrl("https://user:pass@ats.example/apply")).toBeNull()
  })

  test("accepts strict bare IDs and legitimate Jobindex URLs", () => {
    expect(normalizeJobDetailInput("h1647303")).toEqual({
      id: "h1647303",
      url: "https://www.jobindex.dk/jobannonce/h1647303",
    })
    expect(normalizeJobDetailInput("https://jobindex.dk/jobannonce/r13677312?source=saved#top")).toEqual({
      id: "r13677312",
      url: "https://www.jobindex.dk/jobannonce/r13677312",
    })
  })

  test.each([
    "1647303",
    "h1647303/extra",
    "http://www.jobindex.dk/jobannonce/h1647303",
    "https://user:pass@www.jobindex.dk/jobannonce/h1647303",
    "https://www.jobindex.dk:8443/jobannonce/h1647303",
    "https://evil.example/jobannonce/h1647303",
    "https://localhost/jobannonce/h1647303",
    "https://127.0.0.1/jobannonce/h1647303",
    "https://[::1]/jobannonce/h1647303",
    "https://169.254.169.254/jobannonce/h1647303",
    "https://10.0.0.1/jobannonce/h1647303",
    "file:///jobannonce/h1647303",
    "javascript:alert(1)",
    "https://www.jobindex.dk.evil.example/jobannonce/h1647303",
    "https://www.jobindex.dk/not-a-job/h1647303",
  ])("rejects %s before any network request", (input) => {
    let contacted = false
    globalThis.fetch = (async () => {
      contacted = true
      return new Response("unexpected")
    }) as unknown as typeof fetch

    expect(() => normalizeJobDetailInput(input)).toThrow()
    expect(contacted).toBe(false)
  })

  test("rejects a redirect without contacting its destination", async () => {
    const contacted: string[] = []
    globalThis.fetch = (async (input: string | URL | Request) => {
      contacted.push(String(input))
      return new Response(null, {
        status: 302,
        headers: { Location: "http://169.254.169.254/latest/meta-data/" },
      })
    }) as unknown as typeof fetch

    await expect(htmlFetch("https://www.jobindex.dk/jobannonce/h1647303")).rejects.toThrow(
      "redirect rejected",
    )
    expect(contacted).toEqual(["https://www.jobindex.dk/jobannonce/h1647303"])
  })
})
