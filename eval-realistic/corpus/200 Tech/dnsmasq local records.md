---
updated: 2026-05-25T18:26:00
id: 01M6E000000000000000000189
created: 2026-04-23T19:34:00
---
`address=/example.local/10.0.0.1` in dnsmasq.conf resolves *.example.local to 10.0.0.1. `server=8.8.8.8` sets upstream. SRV records: `srv-host=_service._tcp.local,hostname,5000`. Light DHCP server included; skip if Router already DHCP.
