# ChatGPT Job Search
<p align="center">
  <img src="assets/mascot/pip_flight_loop.gif" alt="Pip, the courier bird" width="200">
</p>
The job search that runs on your machine. An OpenAI-native framework for ChatGPT and Codex that ranks roles, tailors CVs, writes cover letters, and prepares interviews.

## What it does

- builds a private evidence-backed candidate profile;
- searches supported job portals and normalizes results;
- ranks jobs without smoothing over gaps;
- drafts CVs, cover letters, and portal fields;
- independently reviews factual grounding and quality;
- compiles, visually inspects, and ATS-checks PDFs in local mode;
- prepares interviews and records outcomes;
- produces private reports and learning plans;
- optionally reconciles Gmail or Notion data with explicit approval.

## Architecture

| Path | Purpose |
|---|---|
| `AGENTS.md` | provider-neutral authority for safety, verification, and repository conventions |
| `.agents/skills/` | native repository skills discovered by Codex |
| `.agents/skills/job-search-core/references/` | shared immutable methodology |
| `.codex-plugin/plugin.json` | skills-only plugin manifest |
| `config/portals.json` | tracked portal defaults |
| `profile/` | ignored private profile and preferences |
| `documents/`, `job_scraper/`, `reports/`, `upskill/` | ignored private runtime state and generated outputs |
| `.claude/` and `CLAUDE.md` | thin optional compatibility pointers only |

The plugin release layout requires `skills/`, while repository discovery uses `.agents/skills/`. `tools/package_plugin.py` creates the release layout from the single `.agents/skills/` authority; no second tracked copy can drift. It also includes the provider-neutral authority, tracked portal defaults, and public synthetic document sources needed by those skills.

## Execution surfaces

### Codex Desktop and Codex CLI

Open the repository as the workspace. Codex reads `AGENTS.md` and discovers `.agents/skills/`. Local workflows may use approved workspace files and installed tools, subject to sandbox and approval boundaries.

Example prompts:

```text
Use $setup to build my private profile from the CVs in documents/cv.
Use $scrape to find backend roles in Copenhagen from the last 14 days.
Use $rank to score the new jobs.
Use $apply for this attached posting.
```

## Windows quick start

1. Clone the repository and enter it in PowerShell.
2. Inspect the environment without installing anything:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\check_environment.ps1
   ```

3. Create a local Python environment for validators:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install PyYAML==6.0.3
   ```

4. Install each portal CLI's local development dependencies after reviewing them:

   ```powershell
   $resolver = Resolve-Path .agents\skills\job-search-core\scripts\resolve-bun.ps1
   Get-ChildItem .agents\skills -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'cli\package.json') } | ForEach-Object {
     $cliDirectory = Join-Path $_.FullName 'cli'
     $bun = & $resolver -CliDirectory $cliDirectory
     Push-Location $cliDirectory
     & $bun install --frozen-lockfile
     Pop-Location
   }
   ```

5. Run the checks:

   ```powershell
   .\.venv\Scripts\python.exe tools\lint_skills.py
   .\.venv\Scripts\python.exe tools\security_guards.py
   .\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
   ```

See [SETUP.md](SETUP.md) for Python, Bun, MiKTeX, and Poppler details.

## Native skills

| Skill | Result |
|---|---|
| `$setup` | private profile and search configuration |
| `$scrape` | normalized, deduplicated job state |
| `$rank` | reproducible fit scores and shortlist |
| `$apply` | grounded, independently reviewed application artifacts |
| `$interview` | stage-specific prep pack and practice |
| `$outcome` | tracker/archive update and calibration evidence |
| `$expand` | proposed evidence-backed profile additions |
| `$upskill` | gap heatmap and learning plan |
| `$html-report` | private self-contained dashboard |
| `$add-template` | verified private document template |
| `$add-portal` | tested native portal skill scaffold |
| `$reset` | explicitly confirmed private-data reset |
| `$gmail-sync` | proposed Gmail-derived tracker changes |
| `$notion-sync` | proposed and approved Notion synchronization |

Portal skills currently include Freehire, a user-controlled LinkedIn export/browser workflow, Akademikernes Jobbank, Jobdanmark, Jobindex, and Jobnet. Only Freehire is enabled by default; all other portals require an intentional private opt-in after reviewing their current access rules.

## Plugin packaging

Assemble a local package without publishing it:

```powershell
.\.venv\Scripts\python.exe tools\package_plugin.py
```

The ignored output is `dist/chatgpt-job-search/`. Validate that bundle with the current OpenAI plugin validator before distribution. Packaging copies the native skills and only their tracked public support files: the manifest, `AGENTS.md`, README, licence, portal defaults, and synthetic document sources. Private runtime directories are outside the package source.

## Licence

ChatGPT Job Search is an OpenAI-native port of [Mads Lorentzen's AI Job Search](https://github.com/MadsLorentzen/ai-job-search). Mads Lorentzen designed and authored the original project.

MIT. Copyright (c) 2026 Mads Lorentzen. See [LICENSE](LICENSE).
