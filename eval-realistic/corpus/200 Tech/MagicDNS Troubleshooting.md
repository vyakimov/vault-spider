---
updated: 2026-04-27T10:59:00
id: 01M6B00000000000000000000A
created: 2026-01-24T09:43:00
tags:
  - homelab
  - networking
---
`tailscale status` shows IP but name won't resolve → check Headscale `/etc/headscale/config.yaml` has `derpServer` and `dnsConfig` set; `systemctl restart headscale` if changed. On client: `resolvectl status` to verify tailscale's nameserver is queried; flush cache with `resolvectl flush-caches`. Last resort: manual DNS entry in `/etc/hosts` or re-auth node.
