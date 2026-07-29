---
updated: 2026-06-26T15:15:00
id: 01M6E000000000000000000086
created: 2026-06-24T12:15:00
---
Edit `/etc/netplan/01-netcfg.yaml` with YAML indentation. Set static IP, routes, and nameservers. Apply with `netplan apply`; validate first via `netplan try` (reverts after 120s if no signal).
