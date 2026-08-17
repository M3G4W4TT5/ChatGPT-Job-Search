# Application Tracker Contract

Use this exact CSV column order:

```text
company,role,sector,fit_score,status,date,cv_file,cover_letter_file,source,notes,deadline
```

## Status vocabulary

Canonical write values:

- `drafted`
- `applied`
- `interviewing`
- `offer`
- `rejected`
- `withdrawn`
- `no_response`
- `interview_only`

Readers may accept legacy space-separated forms, but writers always use the underscore forms. Treat `rejected`, `withdrawn`, `no_response`, and `interview_only` as final. Other values are open unless a workflow explicitly documents a later terminal state.

Never remove or reorder columns. If a legacy tracker lacks `deadline`, append it to the header and leave existing rows with an empty final field. Never guess a deadline.

`date` is the effective date of the row's current status. Before replacing an application date with a later status date, preserve the verified application date in the private application archive or notes. Follow-up timing must use a verified application or last-contact date, not an inferred tracker date.

There is no built-in `no_response` timeout. Write `no_response` only when the user or a supplied authoritative source explicitly confirms that classification and its effective date. A user may keep a private follow-up threshold, but crossing it proposes a follow-up; it does not silently change status.
