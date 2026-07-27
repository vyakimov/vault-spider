---
updated: 2026-05-07T18:36:00
id: 01M6E000000000000000000119
created: 2026-04-05T09:24:00
---
On Linux: `/var/log/syslog` or `/var/log/cron` (distro-dependent). Check `journalctl -u cron` or `journalctl -u cron.service` for systemd cron. Cron emails output to the job owner unless redirected.
