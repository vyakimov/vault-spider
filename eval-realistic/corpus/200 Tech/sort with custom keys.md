---
updated: 2026-04-23T13:41:00
id: 01M6E000000000000000000317
created: 2026-04-22T10:49:00
---
`sort -k 2 file.txt` sorts by field 2 (space/tab separated). Use `-k 2,2` to sort on field 2 only, `-n` for numeric, `-r` for reverse. `sort -t: -k 3 -n /etc/passwd` sorts by UID.
