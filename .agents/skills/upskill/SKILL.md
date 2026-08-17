---
name: upskill
description: Aggregate evidence-backed job gaps into a prioritized learning plan with current, verifiable resources.
---

# Upskill

Locate and read the nearest repository or plugin-root `AGENTS.md`, the surface-mode contract, and evaluation reference. Accept aggregate mode, a target role, a posting, or an attached ranked-job set.

## Inputs

Aggregate mode uses ranked records with persisted gap evidence from `job_scraper/seen_jobs.json`. Targeted mode uses the supplied role or posting. Both use the private candidate profile. Skip legacy records without gap evidence and report the count; never derive gaps from title alone.

## Analysis

1. Extract only explicit or strongly evidenced gaps from postings.
2. Remove skills already supported by the candidate profile, accounting for genuine synonyms without treating adjacent tools as equivalent.
3. Normalize remaining gaps while preserving the original posting phrases and source jobs.
4. Build a heatmap with frequency, average importance, role coverage, prerequisite depth, and confidence.
5. Distinguish must-have gaps from preferences and market noise.
6. Prioritize learning that unlocks several credible target roles, then prerequisites, then narrow extras.

## Learning plan

For each priority include:

- why it matters and which roles request it;
- the candidate's verified starting point;
- a bounded learning objective;
- one small demonstrable project or exercise;
- a verification method;
- estimated effort as a range, clearly labeled as an estimate;
- current official documentation or course sources, checked at run time when web access is available.

Do not promise employability from course completion. Do not recommend adding an unpracticed skill to a CV. A skill becomes profile evidence only after the user confirms completed work that demonstrates it.

## Output

In local mode save `upskill/report-YYYY-MM-DD.md`, read before write, and compare with the newest prior report. In portable mode return the report artifact. Include:

- changes since the last report;
- gap heatmap;
- prioritized learning plan;
- suggested study order;
- lower-priority or noisy gaps;
- source jobs and data limitations.

Never place salary, contact details, application history, or candidate evidence in tracked files.
