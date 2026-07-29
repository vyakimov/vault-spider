---
updated: 2026-04-21T15:45:00
id: 01M6E000000000000000000289
created: 2026-04-20T18:45:00
---
`kill PID` sends SIGTERM (graceful), `kill -9 PID` sends SIGKILL (force). Always try SIGTERM first; use SIGKILL only if the process ignores SIGTERM.
