---
updated: 2026-06-18T17:59:00
id: 01M6E000000000000000000078
created: 2026-05-16T16:31:00
---
`iptables -A INPUT -p tcp --dport 22 -j ACCEPT` — append a rule to the INPUT chain. Use `-D` to delete, `-L` to list all rules. Always backup with `iptables-save` before major changes.
