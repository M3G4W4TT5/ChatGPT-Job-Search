# Security Policy

## Reporting

Do not open a public issue containing candidate data, credentials, private correspondence, or exploit details. Use the repository owner's private security-reporting channel when one is available. Until this port has its own published repository, report issues to the maintainer of the checkout in which you found them.

## Security boundaries

- `AGENTS.md` is the provider-neutral authority. Repository skills cannot weaken its safety or approval rules.
- Job postings, pages, messages, connector records, and attached documents are untrusted data, never instructions.
- Candidate profiles, tracker state, salary data, generated applications, interview records, reports, and credentials are private and gitignored.
- The public CV and cover-letter fixtures are synthetic layout examples and never candidate evidence.
- The plugin manifest remains skills-only: no hooks, apps, or MCP server definitions.
- Claude compatibility files are pointers only and carry no pre-approved permissions, hooks, or canonical rules.
- External writes, submissions, messages, and connector mutations require explicit user approval of the specific proposed action or unchanged batch.
- Login, MFA, credentials, identity, payment, consent, and access-control challenges remain user-controlled.

## Supply chain

Portal CLIs may install local development dependencies. Their manifests must not contain package lifecycle scripts or `trustedDependencies`. CI typechecks and fixture-tests the CLIs but does not make live portal requests.

Actions are pinned to commit SHAs and run with read-only contents permission unless a narrowly scoped workflow documents otherwise. Review workflow, manifest, lockfile, and dependency changes manually even when automated guards pass.

## Local checks

```powershell
.\.venv\Scripts\python.exe tools\lint_skills.py
.\.venv\Scripts\python.exe tools\security_guards.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
git diff --check
git status --short
```

Automated checks reduce accidental exposure; they do not prove that prose contains no identifying details. Inspect the staged diff before every commit.
