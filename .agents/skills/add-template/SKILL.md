---
name: add-template
description: Register, verify, list, and activate a private CV or cover-letter template without mutating shared skill rules.
---

# Add Template

Locate and read the nearest repository or plugin-root `AGENTS.md`, the surface-mode contract, and CV/cover-letter references. Custom template data stays outside the skills-only plugin package.

## Modes

- `add`: register a supplied CV or cover-letter template;
- `list`: list private registered templates and the active choices;
- `switch`: change the active CV or cover-letter template after verifying it exists;
- `remove`: propose removal, require explicit confirmation, and never remove an active template without selecting a replacement.

## Add workflow

1. Identify type, name, source format, required assets, compile/render command, expected extension, and whether the template contains any personal data.
2. Refuse to copy personal content into tracked locations. In local mode store the private source and assets under `profile/templates/<safe-name>/`. In portable mode return a template bundle.
3. Create `template.json` with type, source file, output extension, compile command, tool requirements, page target, known pitfalls, and verification date. Commands must use relative paths and PowerShell-compatible examples on Windows.
4. Remove or parameterize candidate facts while preserving layout. Never treat example content as candidate evidence.
5. Verify the renderer exists. Compile a synthetic placeholder document, check CV or letter page target, render every page, visually inspect it, and extract ATS text. Missing tools or failed checks leave the template unverified.
6. Present verification results before activation.
7. On confirmation, update only `profile/template-settings.json` using an atomic write.

Bundled shared files under `job-search-core/references/` remain immutable. The apply skill reads private template settings; no managed block is inserted into a shared reference.

## Portable mode

If ChatGPT Work cannot run the required renderer, return the source bundle and manifest with verification status `not_run`. Do not activate it as verified. The user can re-upload the locally verified manifest later.

Report stored/returned files, privacy result, compile command, page/visual/ATS results, active choice, and any unpassed gate.
