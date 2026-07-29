---
updated: 2026-07-04T11:07:00
id: 01M6E000000000000000000142
created: 2026-06-02T20:23:00
---
`mysql -u root -p < schema.sql` initializes DB. Set `character_set_client=utf8mb4` and `collation_connection=utf8mb4_unicode_ci` for emoji/unicode. For homelab: MariaDB is faster than MySQL; Docker makes setup trivial.
