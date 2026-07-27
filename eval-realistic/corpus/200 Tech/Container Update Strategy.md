---
updated: 2026-07-22T11:37:00
id: 01M6V000000000000000000008
created: 2026-06-22T10:29:00
---
# Container Update Strategy

How and when self-hosted containers get updated, and the rollback plan when one breaks.

## The Rhythm
I check for updates once a week using Watchtower (a tool that scans registries for new versions). Critical security patches are applied immediately. Feature updates wait for the weekend. I use semantic versioning tags like `latest` only for dev tools; production containers pin to specific versions like `app:7.3.1`. This way I choose when to update.

## Breakage Plan
I always keep the previous container image around. If an update breaks something, I revert the tag, restart the container, and debug later. Database migrations are the risky part—I do a full backup before any container update that touches the database schema. I've only had to rollback twice: once a postgres upgrade that changed a query optimizer, once an app version that had a subtle timezone bug. Both were fixed within a day by keeping the old version available.
