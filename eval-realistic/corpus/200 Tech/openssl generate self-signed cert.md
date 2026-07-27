---
updated: 2026-01-23T10:40:00
id: 01M6E00000000000000000000Z
created: 2026-07-21T17:20:00
---
`openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem` generates cert + key in one step; `-subj "/CN=example.local"` skips prompts. View with `openssl x509 -text -noout -in cert.pem`. For CSR: `openssl req -newkey rsa:2048 -nodes -keyout key.pem -out csr.pem` (sign later or send to CA).
