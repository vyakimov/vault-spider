---
updated: 2026-01-06T15:35:00
id: 01M6E000000000000000000066
created: 2026-07-04T16:55:00
---
`hdparm -S 120 /dev/sda` — spin down disk after 10 minutes of inactivity (120 * 5 sec = 600 sec). Add `-B 1` for aggressive power saving on battery, `-M` for acoustic mode.
