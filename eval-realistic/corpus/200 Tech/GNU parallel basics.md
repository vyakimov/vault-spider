---
updated: 2026-04-07T10:30:00
id: 01M6E000000000000000000041
created: 2026-03-05T15:30:00
---
`seq 1 10 | parallel -j 4 "echo job {} && sleep 1"` — execute shell command for each input line using 4 jobs. -j limits parallelism.
