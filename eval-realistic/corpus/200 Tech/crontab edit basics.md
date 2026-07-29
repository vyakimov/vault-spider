---
updated: 2026-04-26T14:48:00
id: 01M6E000000000000000000268
created: 2026-04-25T09:12:00
---
`crontab -e` — edits user crontab. Format: `minute hour day month dow command`. `0 3 * * * /usr/bin/backup.sh` runs daily at 3am. `crontab -l` lists entries, `-r` removes all.
