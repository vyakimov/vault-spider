---
updated: 2026-02-22T11:51:00
id: 01M6R000000000000000000002
created: 2026-01-22T10:27:00
---
# Waystation Schema Notes

Table design for short codes, targets, and click events.

## Schema
Three main tables: `links` (id, code, target, created, expires), `clicks` (id, link_id, timestamp, referrer, user_agent), and `tags` (link_id, tag). Codes are 4 characters (base36) to keep URLs short. Click events are immutable for audit purposes.

## Indexes
I index on (code) for lookups and (link_id, timestamp) for analytics queries. The clicks table grows quickly, so I partition it by month to speed up range queries and allow archival of old months.
