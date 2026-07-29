---
updated: 2026-05-10T19:43:00
id: 01M6E000000000000000000070
created: 2026-04-08T20:47:00
---
`http.host == "example.com" && tcp.port == 443` — filter HTTPS traffic for specific host. Use `ip.src == 192.168.1.100` to isolate one client. Chain with && (and) or || (or).
