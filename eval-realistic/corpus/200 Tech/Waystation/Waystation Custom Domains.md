---
updated: 2026-03-23T11:02:00
id: 01M6R000000000000000000003
created: 2026-02-23T10:34:00
---
# Waystation Custom Domains

Adding a second short domain for a specific project's links.

## Setup
I registered `go.example.com` (a separate domain) and configured it to use the same Waystation instance. The CNAME points to `go.youyesyou.me`, so links can use either domain. I added a `domain` column to the links table to track which domain a short code was created under.

## Use Case
The second domain lets me hand out links that feel more project-specific without giving away my personal domain. Analytics are still centralized, but I can filter by domain.
