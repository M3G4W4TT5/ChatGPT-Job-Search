import { afterEach, describe, expect, test } from "bun:test";
import {
  extractJobIdFromUrl,
  normalizeRssDate,
  normalizeRssItems,
  parseRssDescription,
  rssFetch,
  USER_AGENT,
} from "../src/helpers";

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
});

describe("rssFetch", () => {
  test("serializes repeated filters and parses CDATA and plain RSS fields", async () => {
    let requestedUrl = "";
    let requestedUserAgent = "";
    globalThis.fetch = (async (input, init) => {
      requestedUrl = String(input);
      requestedUserAgent = new Headers(init?.headers).get("User-Agent") ?? "";
      return new Response(`<?xml version="1.0"?>
        <rss><channel><item>
          <title><![CDATA[Data Scientist]]></title>
          <description><![CDATA[Fuldtidsjob hos Acme A/S, København (Ansøgningsfrist: 31.07.2026)]]></description>
          <link>https://jobbank.dk/job/12345/acme/data-scientist</link>
          <pubDate>Mon, 13 Jul 2026 08:00:00 GMT</pubDate>
        </item></channel></rss>`);
    }) as typeof fetch;

    const items = await rssFetch({ key: "data science", cvtype: ["3", "6"] });
    const url = new URL(requestedUrl);

    expect(url.pathname).toBe("/job/rss");
    expect(url.searchParams.get("key")).toBe("data science");
    expect(url.searchParams.getAll("cvtype")).toEqual(["3", "6"]);
    expect(requestedUserAgent).toBe(USER_AGENT);
    expect(items).toEqual([
      {
        title: "Data Scientist",
        description: "Fuldtidsjob hos Acme A/S, København (Ansøgningsfrist: 31.07.2026)",
        link: "https://jobbank.dk/job/12345/acme/data-scientist",
        pubDate: "Mon, 13 Jul 2026 08:00:00 GMT",
      },
    ]);
  });
});

describe("parseRssDescription", () => {
  test("separates multiple job types, company, location, and deadline", () => {
    expect(
      parseRssDescription(
        "Fuldtidsjob, Graduate/trainee hos Acme A/S, København (Ansøgningsfrist: 31.07.2026)",
      ),
    ).toEqual({
      jobType: "Fuldtidsjob, Graduate/trainee",
      company: "Acme A/S",
      location: "København",
      deadline: "31.07.2026",
    });
  });

  test("normalizes a rolling deadline to null", () => {
    expect(
      parseRssDescription("Deltidsjob hos Example ApS, Aarhus (Ansøgningsfrist: løbende)"),
    ).toEqual({
      jobType: "Deltidsjob",
      company: "Example ApS",
      location: "Aarhus",
      deadline: null,
    });
  });

  test("keeps an unstructured description as the company fallback", () => {
    expect(parseRssDescription("Unstructured feed value")).toEqual({
      jobType: "",
      company: "Unstructured feed value",
      location: "",
      deadline: null,
    });
  });
});

describe("normalizeRssDate", () => {
  test("normalizes valid RSS dates and represents missing or malformed dates as null", () => {
    expect(normalizeRssDate("Mon, 13 Jul 2026 08:00:00 GMT")).toBe("2026-07-13T08:00:00.000Z");
    expect(normalizeRssDate("")).toBeNull();
    expect(normalizeRssDate(undefined)).toBeNull();
    expect(normalizeRssDate("not a date")).toBeNull();
  });

  test("one malformed or missing date does not drop otherwise valid feed items", () => {
    const items = ["Mon, 13 Jul 2026 08:00:00 GMT", "broken", ""].map((pubDate, index) => ({
      title: `Role ${index + 1}`,
      description: `Fuldtidsjob hos Company ${index + 1}, København`,
      link: `https://jobbank.dk/job/${index + 1}/company/role`,
      pubDate,
    }));
    const results = normalizeRssItems(items);
    expect(results).toHaveLength(3);
    expect(results.map((result) => result.posted)).toEqual([
      "2026-07-13T08:00:00.000Z",
      null,
      null,
    ]);
  });
});

describe("extractJobIdFromUrl", () => {
  test("extracts numeric IDs and rejects unsupported URL shapes", () => {
    expect(extractJobIdFromUrl("https://jobbank.dk/job/12345/acme/role")).toBe("12345");
    expect(extractJobIdFromUrl("https://jobbank.dk/job/not-a-number/acme/role")).toBe("");
  });
});
