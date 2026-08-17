---
name: notion-sync
description: Propose and perform approved application-pipeline synchronization with Notion or a portable database export.
---

# Notion Sync

Locate and read the nearest repository or plugin-root `AGENTS.md`, surface-mode contract, web-research reference, and tracker schema. Local private state remains authoritative unless the user explicitly selects another source of truth.

## Connection lanes

- Use a connected Notion capability only when present and authorized for the target workspace/database.
- Otherwise accept/export CSV or JSON and return a proposed import/update set.
- Never require Notion for core tracking; the HTML report remains the local no-connector option.

## Preflight

1. Build the sync set entirely from local or attached state before external calls.
2. Validate the target database identity and required properties: company, role, status, fit score, date, source, deadline, and stable local key.
3. Read existing rows/pages needed for matching. Match by stable key first, then source URL; report ambiguous company/role matches.
4. Present creates, updates, conflicts, and skips. Do not silently overwrite richer remote notes or attachments.

## Approval and sync

External creates and updates require explicit approval of the proposed batch. After approval:

- upsert only unchanged proposed fields;
- use canonical status values;
- store source URLs, not credentials or private file paths;
- add a readable posting digest only from retrieved evidence, never from memory;
- minimize candidate contact, salary, correspondence, and weakness data;
- preserve remote-only fields;
- update ignored local sync state with stable remote IDs only after confirmed success.

One approval covers the unchanged batch. New or materially changed rows require a new preview. Never delete remote pages unless the user explicitly requests a separately previewed deletion.

In portable mode without a connector, return a CSV/JSON import bundle and field mapping. Do not claim remote writes.

## Completion

Report created, updated, unchanged, conflicted, failed, and skipped rows, plus the local sync-state result. Keep failure details free of tokens and private page contents.
