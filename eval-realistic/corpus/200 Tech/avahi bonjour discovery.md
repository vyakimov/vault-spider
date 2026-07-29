---
updated: 2026-01-27T16:32:00
id: 01M6E000000000000000000087
created: 2026-07-25T13:28:00
---
`avahi-browse -a` — find all .local services on LAN. `avahi-publish-service myname _http._tcp 80 path=/data` announces your service. Needs `avahi-daemon` running; check with `systemctl status avahi-daemon`.
