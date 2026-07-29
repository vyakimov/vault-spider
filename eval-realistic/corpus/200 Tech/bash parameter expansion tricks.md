---
updated: 2026-07-10T14:38:00
id: 01M6E000000000000000000278
created: 2026-07-09T19:22:00
---
`${var:0:5}` extracts first 5 chars. `${var#prefix}` removes prefix, `${var%suffix}` suffix. `${var/old/new}` substitutes first match, `${var//old/new}` all. No need for cut/sed for simple cases.
