---
updated: 2026-03-11T18:16:00
id: 01M6E00000000000000000000K
created: 2026-02-09T17:44:00
---
`redis-cli -h localhost -p 6379 GET key` fetches value; `SET key value EX 3600` sets with expiry. `KEYS pattern` finds matching keys (slow on large DBs); use `SCAN 0 MATCH pattern COUNT 100` for cursored iteration. `MONITOR` shows all commands in real-time; `FLUSHDB` clears current DB (dangerous). INCR, LPUSH, SADD for counters, lists, and sets.
