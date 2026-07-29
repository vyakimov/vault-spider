---
updated: 2026-01-25T10:37:00
id: 01M6B000000000000000000008
created: 2026-06-22T09:29:00
tags:
  - homelab
  - networking
---
Headscale ACL groups defined in `/etc/headscale/acl.hujson` as `groups = { "group:admin": ["user@example.com"], "group:devices": ["tag:nas", "tag:gw"] }` and referenced in rules; tags auto-assigned via `tailscale tag <device> tag:nas` on node registration or via ACL auto-tagging. Reload with `systemctl reload headscale`.
