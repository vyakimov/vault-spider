---
tags:
  - homelab
updated: 2026-03-21T10:07:00
id: 01M6N000000000000000000003
created: 2026-04-18T09:59:00
---
SQLite schema is minimal: `links` table (id, url, title, created_at, read_at, deleted_at), `tags` table (id, name), and a join table `link_tags` (link_id, tag_id). Indices on url and created_at for query speed. No foreign-key constraints; I rely on application-level cleanup (soft delete via deleted_at). The read_at column is nullable; null means unread.

Early mistakes: I had denormalized tag names into the links table (comma-separated string), which made filtering by tag a LIKE query (slow). Normalized it properly after the first 500 links. No migration story yet (will probably just write a one-off script if schema changes again). Backups are SQLite dumps via `sqlite3 < .dump`, manually uploaded to cold storage monthly.
