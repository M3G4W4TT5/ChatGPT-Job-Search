---
name: rank
description: Score normalized job postings against verified candidate evidence and produce an honest, reproducible shortlist.
---

# Rank

Locate and read the nearest repository or plugin-root `AGENTS.md`, the surface-mode contract, `../job-search-core/references/04-job-evaluation.md`, `../job-search-core/references/09-web-research.md`, and the tracker schema.

## Input selection

Accept `all`, `new`, an explicit list of IDs or URLs, or a user-supplied/attached job set. Default to unranked records. In local mode load `job_scraper/seen_jobs.json`, `profile/candidate-profile.md`, and `profile/evaluation-preferences.md`. In portable mode use the attached equivalents and return revised state as an artifact.

## Evaluation

For each job:

1. Retrieve the full posting using the safe escalation order. Keep retrieval failures distinct from expiry.
2. Run eligibility and language gates before scoring. Quote the posting text that triggers a hard failure or warning.
3. Confirm that the private profile contains enough evidence for every weighted dimension. If not, return `needs_profile`, list the missing fields, and withhold the overall score. Never invent neutral values or renormalize the remaining dimensions.
4. Score the shared dimensions exactly as defined in the evaluation reference. Apply private weighting overrides only when the user has explicitly recorded them.
5. Cite candidate evidence for every claimed match. Lack of evidence is a gap, not an invitation to infer experience.
6. Record dimension scores, overall score, strengths, gaps, gate result, deadline, retrieval date, and source URL.

Independent jobs may be evaluated concurrently by separate workers when supported. Give every worker the same immutable rubric and candidate evidence. When workers are unavailable, evaluate each posting in a clean second pass against the same checklist. Aggregation never changes individual scores to produce a prettier shortlist.

## State update

In local mode read the current JSON again immediately before writing so scrape results added during evaluation are not lost. Update only the selected records. Preserve unknown fields and write atomically. Use `status: ranked` for successful scores, `status: needs_profile` for incomplete candidate evidence, and a specific retrieval state for source failures.

In portable mode return a revised JSON artifact or an explicit patch. Do not claim local state was updated.

## Shortlist report

Show:

- ranked jobs with company, role, score, gate result, deadline, top evidence, and top gap;
- reasons the highest-ranked jobs lead;
- roles closing soon;
- below-threshold roles;
- excluded, unavailable, and expired roles as separate categories;
- any source or profile uncertainty that could change the result.

If the user requests tracker updates, propose rows first and use the canonical tracker schema. Never label a job applied merely because it was ranked.

## Rules

- Keep low scores low when the evidence is weak.
- Never invent a candidate skill, company fact, or posting requirement.
- A search snippet alone cannot support a score.
- Preserve stored source text and provenance so the score can be reproduced.
