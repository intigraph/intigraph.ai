# Failed playground: before and after

[Before: visible 404](before-404.webm) → [After: failed section removed](after-404.webm).
[Ready host control](after-ready.webm) shows the section revealed only after HTTP
success and a message from the expected child origin and window.

These are source-checkout browser recordings at 1200 × 850 using the same
controlled cross-origin HTTP 404 fixture. The ready recording uses an explicitly
labelled message fixture, not the Quipu engine. The before source is
`239169c59b7115e3ce16f159782775c15fcd7385`; the PR body pins the candidate.
The [source manifest](source-sha256.txt) identifies its tested host bytes.
No deployment is claimed. Download the WebMs to replay if the repository viewer
does not play them inline.

The host keeps its section and links hidden without JavaScript. With JavaScript,
HTTP failure, network failure, an explorer error, or no actual ready signal within
eight seconds removes the entire section and both links. A later explorer error
also removes a previously revealed section. Forged origin/source messages cannot
reveal it. A cold engine import that exceeds eight seconds is intentionally hidden;
a fast iframe load or saved preview is not a successful engine import.

The producer is Quipu PR951, head
`c6b9a0a9f8a14ffc15bf8833595a72ee698aca40`: `quipu:state` reports
`state: loading|ready|error`, the actual loading `stage`, and a safe
`pendant: repository|selected` label. Its separate real-engine browser controls
exercise a download error followed by successful import/retry and a real query.

Reproduce host assertions with `xvfb-run -a node scripts/test-playground.cjs`
after installing the workflow's pinned Playwright version and Chromium.
Run `python3 scripts/check-links.py` for local target existence and live HTTPS
status checks. Both checks run in normal site CI. Live acceptance still requires
the reviewed producer to be deployed before the site consumer can receive readiness.
