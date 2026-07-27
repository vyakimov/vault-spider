---
updated: 2026-04-09T18:26:00
id: 01M6E000000000000000000069
created: 2026-03-07T19:34:00
---
`tcpdump -i eth0 -w capture.pcap tcp port 80` — capture port 80 traffic to pcap file. `-A` shows ASCII, `-X` shows hex dump. Use `tcpdump -r capture.pcap` to read saved captures.
