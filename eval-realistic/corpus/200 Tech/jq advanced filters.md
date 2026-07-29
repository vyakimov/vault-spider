---
updated: 2026-06-27T12:54:00
id: 01M6E000000000000000000113
created: 2026-05-25T15:06:00
---
`jq '.items[] | select(.status == "active") | .name'` — filter and map JSON. `group_by(.type)` groups, `unique_by(.id)` deduplicates. `@base64` encodes, `@csv` exports. Composable, chainable transformations.
