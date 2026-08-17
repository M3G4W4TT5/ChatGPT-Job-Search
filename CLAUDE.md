# Compatibility Entry Point

This file exists only for clients that still look for `CLAUDE.md`.

The repository authority is [`AGENTS.md`](AGENTS.md). Native workflows live under [`.agents/skills/`](.agents/skills/). Read and follow those files directly; do not place candidate data or canonical workflow rules here.

Compatibility command wrappers under `.claude/commands/` point to the native skills. They contain no provider-specific tool permissions or runtime behavior.
