---
updated: 2026-07-08T15:25:00
id: 01M6E00000000000000000000G
created: 2026-06-06T14:05:00
---
`sops -i --rotate secrets.yaml` re-encrypts with current key (age or GPG). Edit with `sops secrets.yaml` (editor opens decrypted version, auto-encrypts on save). `.sops.yaml` config specifies key provider; use `creation_rules` to auto-tailor per file type. Integrates with CI/CD via env vars, no key files in repos.
