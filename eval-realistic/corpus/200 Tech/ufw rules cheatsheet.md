---
updated: 2026-05-17T16:42:00
id: 01M6E000000000000000000077
created: 2026-04-15T15:18:00
---
`ufw allow 22/tcp && ufw allow from 192.168.1.0/24 to any port 3306` — allow SSH globally, MySQL only from LAN. `ufw delete allow 80` removes rules; `ufw default deny incoming` sets default policy.
