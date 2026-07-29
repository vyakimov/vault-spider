---
updated: 2026-05-17T17:59:00
id: 01M6E000000000000000000311
created: 2026-05-16T16:31:00
---
`seq 1 10` generates numbers 1 to 10 (newline-separated). Use `seq 0 2 10` for step 2, `seq -w 1 100` for zero-padded width. Good for loops: `for i in $(seq 1 5); do echo $i; done`.
