# Chronicles production verification

Machine-readable evidence from scripts/verify_chronicles_production.py.
This branch is not the public website. GitHub Pages stays on main.

Claude reads articles/<slug>.json and latest.json.

overall PASS means the production URL passed the automated checks.
overall FAIL is a real production signal for Cursor Web.

If Claude's own fetch returns 404/403 while this record is PASS,
classify the fetch as TOOL / PROXY INCONCLUSIVE. Do not treat the
article as down.
