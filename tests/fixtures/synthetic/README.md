# Synthetic workflow fixtures

These files describe a fictional, staged workflow; they are not one simultaneous mutable-state snapshot and contain no real candidate or employer data.

- `candidate-profile.md`, `behavioral-profile.md`, `evaluation-preferences.md`, and `interview-evidence.md` are setup inputs.
- `company-research.md` is an approved fictional research record used to test behavioral scoring without inferring employer culture from a posting.
- `posting.md` is untrusted source data.
- `seen_jobs.json` is the post-scrape state.
- `ranked_jobs.json` is the post-rank state with a documented reproducible score.
- `tracker.csv` is a later portable post-apply state. Generated CV and letter artifacts are intentionally absent because public generated applications are forbidden.
- `outcome-message.md` is an untrusted later rejection source for a proposed outcome transition.

Forward tests must keep all generated application content in memory or an ignored temporary directory and must never make live portal or connector calls.
