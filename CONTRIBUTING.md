# Contributing

This OpenAI-native port is derived from Mads Lorentzen's MIT-licensed `ai-job-search`. Preserve his copyright, licence, Git history, and visible README credit.

## Architecture rules

- `AGENTS.md` owns provider-neutral safety, verification, and repository conventions.
- `.agents/skills/` owns native workflows. Skill frontmatter contains only `name` and `description`.
- Shared methodology lives once under `job-search-core/references/`.
- Candidate-specific and mutable data lives only in ignored runtime paths.
- `.claude/` remains thin compatibility, never runtime authority.
- The plugin package is generated from `.agents/skills/`; do not add a second tracked copy under `skills/`.
- Hooks are optional conveniences at most and cannot be required for correctness.

## Changes worth proposing

- a tested improvement to factual grounding, privacy, review quality, accessibility, or Windows behavior;
- a maintained public portal integration with documented access boundaries;
- a portable ChatGPT Work fallback for a local-only workflow;
- a reproducible fix with synthetic fixtures;
- an intentional port of a current upstream change.

Do not commit personal candidate data, generated applications, salary data, private correspondence, live portal responses, credentials, or secrets.

## Skill changes

Keep a skill focused and use conversational inputs rather than slash-command variables. Put details in references only when several workflows genuinely share them. Generate `agents/openai.yaml` with the built-in skill-creator tooling and ensure `default_prompt` explicitly names the skill.

For reviewer behavior, keep the independent-subagent contract and the clearly labeled second-pass fallback. Do not let suggested rewrites introduce unsupported claims.

## Validation

Run from PowerShell:

```powershell
.\.venv\Scripts\python.exe tools\lint_skills.py
.\.venv\Scripts\python.exe tools\security_guards.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
```

For every touched portal CLI:

```powershell
Push-Location .agents\skills\<portal>-search\cli
bun install
bun run typecheck
bun test
Pop-Location
```

For document changes, compile both synthetic fixtures, verify exact page counts, render every page, inspect the images, and extract ATS text. Finish with plugin validation, `git diff --check`, and a staged-diff privacy review.

## Upstream changes

Fetch `upstream` and review current commits before porting. A clean cherry-pick is not proof that a Claude-oriented change belongs unchanged in the OpenAI runtime. Preserve the behavior, tests, and safety intent, then express it through `AGENTS.md`, native skills, shared references, or portable fallbacks as appropriate.

Do not push, publish, or submit a plugin as part of a contribution unless the repository owner explicitly authorizes it.
