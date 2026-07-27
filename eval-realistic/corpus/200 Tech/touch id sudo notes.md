---
updated: 2026-07-11T18:06:00
id: 01M6E000000000000000000149
created: 2026-06-09T15:54:00
---
Edit `/etc/pam.d/sudo` and add `auth sufficient pam_tid.so` as the first auth line. Touch ID then works for sudo without a password prompt. Revert by removing the line if it breaks (e.g., SSH sessions without a terminal).
