---
updated: 2026-07-03T17:39:00
id: 01M6E000000000000000000271
created: 2026-07-02T12:51:00
---
`nohup long-task &` — runs job immune to terminal hangup (SIGHUP). Output goes to `nohup.out` in current dir. Use `disown` or `&` to detach; `nohup` preserves after logout.
