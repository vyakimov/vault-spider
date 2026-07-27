---
updated: 2026-07-05T14:18:00
id: 01M6E000000000000000000065
created: 2026-06-03T15:42:00
---
`smartctl -a /dev/sda` — full disk health report; check Reallocated_Sector_Ct and Power_On_Hours. Use `smartctl -t short /dev/sda` to run self-test, check result later.
