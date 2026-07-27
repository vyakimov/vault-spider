---
updated: 2026-03-15T14:08:00
id: 01M6E000000000000000000075
created: 2026-02-13T13:52:00
---
`acme.sh --issue -d example.com --dns dns_cloudflare --renew-hook "systemctl reload nginx"` — get cert via Cloudflare DNS plugin, auto-reload nginx on renewal. `acme.sh --list` shows managed certs.
