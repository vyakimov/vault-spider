---
updated: 2026-04-04T19:23:00
id: 01M6E000000000000000000090
created: 2026-03-02T16:07:00
---
In `/etc/auto.master`: `/mnt/remote /etc/auto.remote`. In `/etc/auto.remote`: `nfs  -fstype=nfs,hard,intr  server:/export`. Access `/mnt/remote/nfs` and autofs mounts on-demand, unmounts on idle timeout.
