---
updated: 2026-05-13T10:50:00
id: 01M6E00000000000000000000N
created: 2026-04-11T19:10:00
---
```
Host nas
  HostName 192.168.1.10
  User admin
  IdentityFile ~/.ssh/id_nas
  Port 2222
```
Now `ssh nas` connects directly. Wildcards work: `Host *.home` for all .home domains. Use `ProxyJump bastion` to tunnel through another host. `ControlMaster auto` + `ControlPath ~/.ssh/socket-%h-%p-%r` reuses connections, speeds up successive SSH calls.
