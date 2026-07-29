---
updated: 2026-05-15T19:03:00
id: 01M6E000000000000000000283
created: 2026-05-14T12:27:00
---
`(cmd1; cmd2)` subshell: child process, vars don't leak. `{ cmd1; cmd2; }` grouping: same shell, vars persist. Subshell: cleaner scoping, slower. Grouping: faster, share context.
