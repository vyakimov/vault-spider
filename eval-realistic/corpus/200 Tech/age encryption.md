---
updated: 2026-06-07T14:08:00
id: 01M6E00000000000000000000F
created: 2026-05-05T13:52:00
---
`age-keygen > key.txt` creates a key; encrypt with `age -e -r age1xxx... file.txt > file.txt.age`. Decrypt via `age -d -i key.txt file.txt.age`. Supports multiple recipients (useful for shared secrets): `age -e -r recipient1 -r recipient2 ...`. Simpler than GPG; no key servers or expiry hassle.
