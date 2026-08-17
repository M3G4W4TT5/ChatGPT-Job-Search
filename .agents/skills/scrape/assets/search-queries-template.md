# Private Search Query Template

Copy and personalize this structure as `profile/search-queries.md`. Do not place candidate-specific queries in the skill directory.

## Portal strategy

- Enabled portal skills: `[skill names from config/portals.json plus private overrides]`
- Primary market boards: `[boards]`
- Target employer career pages: `[employers]`
- Web-search fallback sites: `[sites without a maintained CLI]`

## Languages

Create natural query variants for every working language declared in `profile/candidate-profile.md`. Translate roles by market usage, not literal word substitution. Apply the shared Language Gate to job requirements; the language in which an advert is written is not itself a job requirement.

## Priority 1: Primary function

```text
"[PRIMARY TITLE 1]" [CITY OR REGION]
"[PRIMARY TITLE 2]" [CITY OR REGION]
"[CORE SKILL]" [FUNCTION] [CITY OR REGION]
```

## Priority 2: Domain expertise

```text
"[DOMAIN KEYWORD 1]" [ROLE VARIANT] [REGION]
"[DOMAIN KEYWORD 2]" [ROLE VARIANT] [REGION]
```

## Priority 3: Adjacent roles

```text
"[ADJACENT TITLE 1]" [TRANSFERABLE SKILL] [REGION]
"[ADJACENT TITLE 2]" [TRANSFERABLE SKILL] [REGION]
```

## Constraints

- Acceptable locations and commute: `[locations and limits]`
- Remote/hybrid/onsite: `[preferences]`
- Employment type: `[types]`
- Freshness: `[days; default 14]`
- Exclusions: `[deal-breakers]`

## Rules

- Organize by function and include several market-realistic title variants.
- Never insert salary, contact information, or credentials into a search query.
- Include postings with unknown dates but flag them; exclude verified expired deadlines.
- A focus supplied to the scrape skill selects relevant categories and may add a few temporary variants without overwriting this file.
