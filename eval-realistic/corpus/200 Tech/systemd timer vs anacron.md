---
updated: 2026-06-08T19:53:00
id: 01M6E000000000000000000120
created: 2026-05-06T10:37:00
---
`systemd` timers are per-user, precise, with dependency support; `anacron` is system-wide and runs missed jobs even if the machine was off. For always-on servers use timers; for laptops/intermittent machines, anacron catches up.
