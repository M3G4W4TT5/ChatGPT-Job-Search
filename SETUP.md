# Windows-First Setup

This guide detects tools first and leaves installation decisions to you. Nothing in the project requires a global install to be performed automatically.

## 1. Check the environment

From the repository root in PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\check_environment.ps1
```

The check reports:

- Python 3.11 or newer for repository tools and tests;
- Bun for portal CLIs and their TypeScript checks;
- LuaLaTeX and XeLaTeX from MiKTeX or TeX Live;
- Poppler commands `pdfinfo`, `pdftotext`, and `pdftoppm`;
- Git with `origin` configured for this port and `upstream` configured for Mads Lorentzen's original project.

A missing tool is reported as missing, not installed and not counted as a passed gate.

## 2. Python

Create an ignored repository-local environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install PyYAML==6.0.3
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
```

If `py` is unavailable but `python` points to a supported version, use `python -m venv .venv`. Review [python.org](https://www.python.org/downloads/windows/) or the Microsoft Store package before choosing an installation route.

## 3. Bun and portal CLIs

Install Bun only if you intend to run local portal skills. See [Bun's Windows installation documentation](https://bun.sh/docs/installation) and review the command before running it.

Bun is separate from the Python `.venv`. On Windows, the shared resolver checks each portal's `cli\node_modules\.bin\bun.exe`, `$env:BUN_INSTALL`, `$env:USERPROFILE\.bun\bin\bun.exe`, `PATH`, and repository-local `.tools`. A successful fallback does not require a persistent `PATH` change.

The repository pins Bun 1.3.14 in `.bun-version`, each CLI manifest, and CI. Verify that exact version and install only from the committed lockfiles:

```powershell
$resolver = Resolve-Path .agents\skills\job-search-core\scripts\resolve-bun.ps1
Get-ChildItem .agents\skills -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'cli\package.json') } | ForEach-Object {
  $cliDirectory = Join-Path $_.FullName 'cli'
  $bun = & $resolver -CliDirectory $cliDirectory
  if ((& $bun --version) -ne (Get-Content .bun-version -Raw).Trim()) { throw 'Wrong Bun version' }
  Push-Location $cliDirectory
  & $bun install --frozen-lockfile
  & $bun run typecheck
  & $bun test
  Pop-Location
}
```

Portal live calls are intentionally excluded from CI. Mock/fixture tests may run automatically; live searches remain small, explicit, and subject to the portal skill's access rules.

## 4. MiKTeX or TeX Live

The stock CV requires `lualatex`; the stock cover letter requires `xelatex`. On Windows, MiKTeX is the primary documented option: [MiKTeX downloads](https://miktex.org/download).

After installation, open a new PowerShell session and verify:

```powershell
lualatex --version
xelatex --version
```

MiKTeX may prompt to install missing packages during the first compile. Review the package names and keep on-the-fly installation under your control. Do not run a package-manager install from an agent without approval.

Compile the synthetic fixtures:

```powershell
Push-Location cv
lualatex -interaction=nonstopmode -halt-on-error main_example.tex
Pop-Location

Push-Location cover_letters
xelatex -interaction=nonstopmode -halt-on-error cover_example.tex
Pop-Location
```

Expected page counts are two for the CV and one for the cover letter.

## 5. Poppler

PDF validation requires:

```powershell
pdfinfo -v
pdftotext -v
pdftoppm -v
```

Use a trusted Windows Poppler distribution or an existing managed tool bundle. Add its `Library\bin` directory to the current process `PATH` for testing rather than moving binaries into the repository. The apply workflow needs page count, page rendering, and text extraction; one command is not a substitute for the others.

## 6. Private profile

Keep candidate materials in the ignored locations described by `documents/README.md`, then ask:

```text
Use $setup to build my private profile from the files I supplied.
```

The setup skill writes private files below `profile/`. It does not personalize `AGENTS.md`, shared skill references, `cv/main_example.tex`, or `cover_letters/cover_example.tex`.

Before adding real data, confirm the ignore rules:

```powershell
git check-ignore -v profile\candidate-profile.md
git check-ignore -v job_search_tracker.csv
git check-ignore -v documents\cv\candidate.pdf
```

Each command should print the matching ignore rule.

## 7. Validation

```powershell
.\.venv\Scripts\python.exe tools\lint_skills.py
.\.venv\Scripts\python.exe tools\security_guards.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe tools\package_plugin.py
```

Run CLI typechecks/tests as shown above, then run `git diff --check` and inspect `git status --short`.

## 8. ChatGPT Work

Use the packaged skills through an authorized workspace installation process. ChatGPT Work can use attached artifacts and approved connectors, but it cannot be assumed to have this repository, a shell, or local renderers. Every native skill defines a portable result and reports local-only gates as not run when those capabilities are absent.

Do not publish or submit the plugin as part of setup.

## 9. Updating from Mads Lorentzen's upstream repository

Verify the remote:

```powershell
git remote get-url upstream
git fetch upstream
git log --oneline --decorate HEAD..upstream/master
```

Merge or cherry-pick intentionally. The original upstream remains the methodology source of truth, but `AGENTS.md`, `.agents/skills/`, plugin packaging, and private-state separation are the OpenAI port's runtime architecture and must be reconciled rather than overwritten.
