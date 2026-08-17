# Private Career Documents

Everything placed below these folders is candidate-private and ignored by Git. Only this README and `.gitkeep` structure belong in the public repository.

```text
documents/
├── cv/              source CVs supplied by the user
├── linkedin/        exports supplied by the user
├── diplomas/        education evidence
├── references/      recommendations and assessments
├── postings/        posting snapshots supplied before an application
└── applications/    private per-application archive
```

The setup skill reads user-supplied material and writes structured state under `profile/`. It never copies candidate facts into shared skills, `AGENTS.md`, or the public LaTeX examples.

## Application archive

Use a safe normalized folder name such as:

```text
documents/applications/northstar_platform_automation/
├── job_posting.md
├── submitted_cv.pdf
├── submitted_cover_letter.pdf
├── application_fields.md
├── interview_recruiter.md
└── outcome.md
```

Archive exact submitted artifacts when available. Never reconstruct an expired posting or missing submitted version from memory. Outcome and interview files may contain sensitive weaknesses, decisions, and correspondence; keep them private.

## Before using real data

```powershell
git check-ignore -v documents\cv\candidate.pdf
git check-ignore -v documents\applications\example\outcome.md
git status --short
```

The first two commands must show ignore rules, and real candidate files must not appear in `git status`.
