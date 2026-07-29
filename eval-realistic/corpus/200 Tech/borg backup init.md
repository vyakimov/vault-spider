---
updated: 2026-04-05T12:34:00
id: 01M6E00000000000000000000D
created: 2026-03-03T11:26:00
---
`borg init -e keyfile-blake2b /mnt/borg/repo` initializes an encrypted backup repo; save the key passphrase securely. Then `borg create archive-2026-07 /home /var` makes incremental backups; always verify with `borg list archive-2026-07`. Prune old archives via `borg prune --keep-daily 30` before listing to avoid clutter.
