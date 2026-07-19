---
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000006
created: 2026-02-27T20:03:11
---
`rsync -aHAX --delete --dry-run src/ dest/` — archive plus hardlinks/ACLs/xattrs, mirror
deletions, and always dry-run first. Drop `--dry-run` when the file list looks right.

[[NAS Snapshot Replication]]
