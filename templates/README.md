# Custom Templates

Tracked document methodology lives under `.agents/skills/job-search-core/references/`. Candidate-specific or licensed custom templates belong in ignored `profile/templates/`, not here and not in the skills-only plugin package.

Use `$add-template` to register a private CV or cover-letter template. It records a private manifest, compiles synthetic content when the renderer exists, checks page count, renders every page for visual inspection, extracts ATS text, and updates only `profile/template-settings.json` after confirmation.

The stock tracked examples remain:

- `cv/main_example.tex` for a two-page CV layout;
- `cover_letters/cover_example.tex` for a one-page cover-letter layout.

Both are synthetic fixtures and never candidate evidence.
