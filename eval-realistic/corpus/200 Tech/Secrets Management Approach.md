---
updated: 2026-05-20T11:15:00
id: 01M6V000000000000000000006
created: 2026-04-20T10:15:00
---
# Secrets Management Approach

Where secrets live for each self-hosted app, and what is deliberately not in git.

## The Inventory
API keys for external services (Mapbox, Stripe test keys) live in a .env file that's git-ignored. Database passwords are in environment variables set at container startup. OAuth client secrets are in the password manager, not in any config file. SSH keys are on an encrypted USB and never leave it—I load them into ssh-agent only when needed. The rule is: if it can unlock something, it's not in source control.

## What Actually Matters
I've stopped trying to fully rotate secrets (who has the time). Instead, I focus on containment: each service gets its own credentials, so a leaked password only burns that one thing. The database password is unique per server. External API keys are test-tier only, so they can't actually spend money. It's not perfect security, but it's proportional to the risks in a hobby homelab.
