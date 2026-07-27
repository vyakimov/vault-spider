---
updated: 2026-03-08T18:26:00
id: 01M6E000000000000000000302
created: 2026-03-07T19:34:00
---
`resolvectl status` shows DNS config under systemd-resolved. Use `resolvectl query example.com` to test DNS, `resolvectl dns eth0 8.8.8.8` to set resolver per interface.
