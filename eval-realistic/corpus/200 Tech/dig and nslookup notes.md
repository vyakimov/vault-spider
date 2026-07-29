---
updated: 2026-07-12T11:17:00
id: 01M6E000000000000000000072
created: 2026-06-10T10:13:00
---
`dig @8.8.8.8 example.com MX +short` — query Google DNS for mail records in short format. `nslookup -type=NS example.com` shows nameservers. Add `+trace` to dig for full resolution chain.
