---
updated: 2026-01-13T12:34:00
id: 01M6E000000000000000000073
created: 2026-07-11T11:26:00
---
`openssl s_client -connect example.com:443 -showcerts` — inspect SSL/TLS cert chain and handshake details. `-tls1_2` forces TLS version. Use `echo | openssl s_client ...` for non-interactive mode.
