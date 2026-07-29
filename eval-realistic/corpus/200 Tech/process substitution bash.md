---
updated: 2026-04-14T18:46:00
id: 01M6E000000000000000000282
created: 2026-04-13T11:14:00
---
`diff <(sort file1) <(sort file2)` — treats cmd output as file. Avoids temp files; cleaner than pipes for multiple inputs. Not POSIX; bash/zsh only.
