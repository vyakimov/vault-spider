---
updated: 2026-04-16T15:25:00
id: 01M6E000000000000000000076
created: 2026-03-14T14:05:00
---
```
[sshd]
enabled = true
maxretry = 3
bantime = 3600
findtime = 600
```
Jail config: ban IP for 3600s after 3 fails in 600s window. Use `fail2ban-client status` to see active jails, `fail2ban-client set sshd unbanip <ip>` to unban.
