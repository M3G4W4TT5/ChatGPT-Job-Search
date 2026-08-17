# Execution Surface Contract

Select one mode before running a workflow.

## Local repo mode

Use this mode only when the repository and local tools are actually available.

- Resolve paths from the repository root, not from the current skill directory.
- Use PowerShell-first commands on Windows and preserve workspace sandbox boundaries.
- Read existing private state before writing. Keep writes inside gitignored runtime paths.
- Run required commands and report their real exit status. A missing tool is a skipped gate, not a pass.
- Never install a global dependency without explicit approval.

## Portable ChatGPT Work mode

Use this mode when the skill is installed in ChatGPT Work without verified local repository or shell access.

- Ask for or use files attached in the conversation. Do not claim to inspect paths that were not uploaded.
- Represent private state as a small downloadable profile, tracker, JSON, Markdown, HTML, or document artifact that the user can retain and re-upload.
- Produce document source plus a rendered artifact only when the surface can actually render it. Otherwise return the source and a precise local compile handoff.
- Use connected plugins only when they are present and the user authorized the relevant read or write. If a connector is absent, accept an export and return a proposed update set.
- Do not claim to execute Bun, Python, LaTeX, Poppler, Git, or PowerShell.
- Preserve the same grounding, untrusted-input, approval, and reviewer rules as local mode.

## Portable result rule

Every local mutation must have a portable equivalent:

| Local result | Portable result |
|---|---|
| update `profile/` | revised profile artifact or explicit patch |
| update tracker CSV | revised CSV artifact |
| save scraper JSON | normalized JSON artifact |
| write CV or letter source | downloadable source artifact |
| compile and inspect PDF | rendered file if supported, otherwise an unpassed compile gate |
| update Gmail or Notion | approved connector write, or a proposed update table |
| reset private files | exact deletion checklist for the user; never claim deletion |

If the portable equivalent cannot preserve a material guarantee, stop and state the limitation instead of claiming ChatGPT Work compatibility.
