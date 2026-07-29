---
updated: 2026-06-10T17:49:00
id: 01M6E000000000000000000148
created: 2026-05-08T14:41:00
---
`ykman piv generate-key -a RSA2048 9a` stores a key on the YubiKey slot 9a. Export the cert with `ssh-keygen -D /usr/local/opt/yubico-piv-tool/lib/ykcs11.so`, then add to `~/.ssh/authorized_keys` on remote servers.
