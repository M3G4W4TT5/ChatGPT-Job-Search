---
name: reset
description: Safely clear selected private candidate state with an exact preview, explicit confirmation, and no shared-file mutation.
---

# Reset

Locate and read the nearest repository or plugin-root `AGENTS.md` and surface-mode contract. This workflow is destructive and applies only to ignored private runtime data.

## Scopes

- `profile`: files below `profile/`, except `.gitkeep`;
- `search`: `job_scraper/seen_jobs.json`, sync state, private reports, and `job_search_tracker.csv`;
- `applications`: generated application, interview, posting, and outcome files under `documents/` plus generated CV/letter outputs;
- `all`: all three scopes.

Never delete tracked examples, shared skills/references, portal source, tests, configuration defaults, licence, history, or user files outside the repository. Never interpret an empty or ambiguous input as `all`.

## Local workflow

1. Resolve the repository root and the requested scope.
2. Enumerate exact existing target paths without following symlinks or junctions outside the repository.
3. Verify every resolved target is inside an allowed ignored directory and is not tracked by Git.
4. Present the exact deletion list, total file count, and which files remain unchanged.
5. Require explicit confirmation that names the scope. A prior unrelated approval is not confirmation.
6. Delete only the previewed unchanged set. If the set changed, preview again.
7. Recreate required empty private directories or `.gitkeep` placeholders only when they are tracked project structure.
8. Run `git status --short` and confirm no tracked file was deleted or modified.

Prefer a recoverable trash operation when the current environment supports it. If deletion is permanent, say so in the confirmation prompt.

## Portable ChatGPT Work mode

Return the exact artifact/file deletion checklist. Do not claim local deletion. If the conversation platform has generated downloadable artifacts, explain that deleting the chat or local downloads remains the user's action.

## Completion

Report deleted files, skipped or changed targets, recovery status, and tracked-file integrity. Stop immediately if a resolved path leaves the intended private directories.
