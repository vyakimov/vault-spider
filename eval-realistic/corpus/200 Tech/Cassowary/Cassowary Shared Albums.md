---
updated: 2026-03-09T11:28:00
id: 01M6P000000000000000000008
created: 2026-02-09T10:56:00
---
# Cassowary Shared Albums

I wanted to share a specific album with family members without exposing my entire photo library, so I built a sharing feature that generates time-expiring, read-only access tokens.

## Token System
Each shared album gets a unique token that's valid for 30 days by default. The token is embedded in a URL like `/albums/share/<token>` that serves a stripped-down gallery view with no navigation to other albums or metadata.

## Limitations
Tokens are bearer-based (no auth), so anyone with the link can access the album. For sensitive trips, I use shorter expiry windows (7 days) and rotate tokens periodically. I considered password-protecting shares but decided the token entropy is sufficient for casual sharing.
