---
updated: 2026-07-12T12:34:00
id: 01M6E000000000000000000306
created: 2026-07-11T11:26:00
---
`ntpdate -s pool.ntp.org` does one-shot time sync (deprecated but still works). Requires stopping ntpd/chrony first. Modern: use `chronyc makestep` or `timedatectl set-ntp true`.
