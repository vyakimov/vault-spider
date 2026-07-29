---
updated: 2026-04-09T19:43:00
id: 01M6E000000000000000000303
created: 2026-04-08T20:47:00
---
`hostnamectl set-hostname webserver01` sets the hostname persistently (requires root). Use `hostnamectl status` to view. Changes apply after reboot or systemctl restart systemd-hostnamed.
