# Chronicles production verification

These records are written by `.github/workflows/chronicles-production-verify.yml`
using `scripts/verify_chronicles_production.py` after a request to the live
production URL. This branch is not the website. GitHub Pages stays on `main`.

Files:

- `articles/<slug>.json` — one article
- `latest.json` — copy of the most recent record written by that run

Each record lists the checks performed, the URL requested for the page and
for each asset, HTTP status, response size, response SHA-256, selected
response headers, and the commit and Actions run that produced it.

`overall` is `PASS` only when every required check in that record passed.
`overall` is `FAIL` when one or more of those checks failed.
The result is limited to the checks named in `checks_performed`.

Audit a record with its `github_actions_run_id`, `production_commit`,
`verifier_script_commit`, and `workflow_commit`.
