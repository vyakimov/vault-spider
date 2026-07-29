---
updated: 2026-06-20T15:55:00
id: 01M6E000000000000000000106
created: 2026-05-18T20:35:00
---
Most frameworks load `.env` then `.env.local` then `.env.*.local` (env-specific). Process overrides only if key not already set. Check `dotenv` lib docs for exact order. Never commit `.env.local`.
