---
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000008
created: 2026-04-08T13:29:47
---
A [[technote]] on systemd timers vs cron.

## OnCalendar

`OnCalendar=Mon..Fri 07:30` — the syntax is `DOW YYYY-MM-DD HH:MM:SS` with ranges and `*`.
Test an expression with `systemd-analyze calendar 'Mon..Fri 07:30'` before trusting it.

## Why bother over cron

`Persistent=true` runs a missed timer at next boot (laptops!), logs land in journalctl, and the
service unit gets the full sandboxing options. Cron wins on ubiquity, nothing else.
