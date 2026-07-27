---
updated: 2026-06-28T13:11:00
id: 01M6E000000000000000000114
created: 2026-06-26T16:19:00
---
`curl --retry 3 --retry-delay 1 --retry-max-time 60 url` — retry on transient errors, 1-second delay, timeout after 60s. `--retry-all-errors` also retries on HTTP 4xx/5xx. Modern curl requires `--retry-connrefused` for refused connections.
