---
updated: 2026-05-06T13:51:00
id: 01M6E00000000000000000000E
created: 2026-04-04T12:39:00
---
`restic -r s3:s3.example.com/bucket init` initializes an S3 backend; export `RESTIC_PASSWORD` before backup. `restic backup /data` creates snapshot; `restic snapshots` lists them. Dedup is automatic; restore with `restic restore latest -t /mnt/restore`. Faster than borg for partial restores, slightly higher overhead.
