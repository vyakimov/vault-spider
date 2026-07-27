---
updated: 2026-02-08T11:17:00
id: 01M6N000000000000000000007
created: 2026-01-08T10:49:00
---
# Millwright Import from Pocket Export

A one-time Python script to migrate my ~800 saved articles from a Pocket export into Millwright's schema without losing tags, starred status, or timestamps.

## Process
I downloaded Pocket's HTML export, parsed the link and tag metadata, then bulk-inserted into Millwright's schema as a single transaction. The script checked for duplicates by URL to avoid re-ingesting articles I'd already saved manually.

## Gotchas
Pocket includes a lot of junk—ads masquerading as articles, dead links, duplicates. I filtered out obvious noise (domain patterns like "doubleclick.net"), and manually deleted the worst offenders after import. Tags needed normalization because Pocket allowed spaces and I wanted consistent slugs.
