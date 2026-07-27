---
updated: 2026-02-24T11:57:00
id: 01M6E000000000000000000032
created: 2026-01-22T18:33:00
---
`gpg --gen-key` (or `--full-generate-key` for advanced options) creates keypair. Encrypt: `gpg -e -r recipient@example.com file.txt` → file.txt.gpg. Decrypt: `gpg -d file.txt.gpg`. Sign: `gpg -s file.txt` → file.txt.gpg (combine with encrypt: `-es`). List keys: `gpg --list-keys`. Always back up private key securely.
