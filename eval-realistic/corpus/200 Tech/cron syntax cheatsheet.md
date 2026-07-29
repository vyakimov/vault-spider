---
updated: 2026-06-14T11:07:00
id: 01M6E00000000000000000000P
created: 2026-05-12T20:23:00
---
```
# minute hour day month day-of-week command
0 2 * * * /backup.sh
*/15 * * * * /health-check.sh
0 0 1 * * /monthly-report.sh
0 9-17 * * 1-5 /work-hours.sh
```
`*/15` runs every 15 minutes; ranges like `9-17` for 9am-5pm; comma-separated values `1,15` for specific days. Test with `run-parts --test /etc/cron.daily`. Always use absolute paths in scripts; capture output: `0 2 * * * /backup.sh >> /var/log/backup.log 2>&1`.
