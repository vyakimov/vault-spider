---
updated: 2026-01-14T11:23:00
id: 01M6C000000000000000000008
created: 2026-07-14T10:31:00
---
# Larder Multi-User Notes

Considering whether Larder needs real accounts now that a partner uses it too. Currently everything is single-user with a shared read-only app.

## Current Setup
I built Larder for myself, so there's no auth layer. My partner can view the pantry and see recipes, but can't add or modify items. This works for now because I do most of the inventory management.

## Decision
I'm deferring multi-user support for now. Adding auth would complicate the setup, and our use case (one person managing, one person reading) is working fine. If we ever need two people writing simultaneously, I'd add a simple token-based system and conflict resolution for competing updates.
