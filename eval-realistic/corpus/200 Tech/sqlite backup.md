---
updated: 2026-06-02T09:05:20
id: 01M6H000000000000000000003
created: 2026-04-14T22:03:18
---

a [[technote]] on backing up SQLite properly

Do NOT just cp a live database file — WAL mode means the copy can be torn.

```bash
sqlite3 app.db ".backup 'backup-$(date +%F).db'"
```

`.backup` takes a consistent snapshot even mid-write. For [[Larder]] this runs nightly and the
output lands in the path that [[NAS Snapshot Replication]] picks up.

`VACUUM INTO 'file.db'` is the other option — also consistent, and compacts while it copies.
