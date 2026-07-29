---
updated: 2026-02-28T17:49:00
id: 01M6E000000000000000000088
created: 2026-01-26T14:41:00
---
In `/etc/samba/smb.conf` define shares with `[sharename]`, `path`, `valid users`, `read only`. Use `smbpasswd -a user` to add a Samba user. Test config with `testparm`; restart `smbd` after changes.
