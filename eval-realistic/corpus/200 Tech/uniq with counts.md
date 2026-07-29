---
updated: 2026-05-24T14:58:00
id: 01M6E000000000000000000318
created: 2026-05-23T11:02:00
---
`sort file.txt | uniq -c` counts duplicate lines (uniq needs sorted input). Use `-d` to show only duplicates, `-u` for unique lines only. `uniq -c | sort -rn` to sort by count.
