---
name: job-search-core
description: Shared grounding, writing, evaluation, document, interview, and web-research methodology for the AI Job Search skills. Use only as supporting context for another job-search skill, not as a standalone user workflow.
---

# Job Search Core

Locate and read the nearest repository or plugin-root `AGENTS.md` before using any bundled methodology. It is the authority for safety, privacy, verification, execution surfaces, and repository conventions.

Load only the references required by the active workflow:

- `references/surface-modes.md`: local repository and portable ChatGPT Work behavior
- `references/03-writing-style.md`: writing voice, tone, and phrasing rules
- `references/04-job-evaluation.md`: fit scoring, requirements, gates, and deal-breakers
- `references/05-cv-templates.md`: CV structure, tailoring, compilation, and ATS rules
- `references/06-cover-letter-templates.md`: cover-letter structure and formatting
- `references/07-interview-prep.md`: interview questions, STAR structure, and practice
- `references/08-application-forms.md`: portal free-text and structured fields
- `references/09-web-research.md`: safe posting and company research
- `references/tracker-schema.md`: tracker columns and status vocabulary

Candidate facts never live in this skill. In local repo mode, load them from gitignored `profile/` and source documents under `documents/`. In portable Work mode, use only the user-provided profile and source files in the current conversation.

Do not duplicate these references into focused workflow skills. Link to the relevant file and keep workflow-specific sequencing in that workflow's `SKILL.md`.
