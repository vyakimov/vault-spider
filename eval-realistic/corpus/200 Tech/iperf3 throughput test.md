---
updated: 2026-06-21T18:06:00
id: 01M6E00000000000000000000X
created: 2026-05-19T15:54:00
---
Server: `iperf3 -s -B 192.168.1.10` listens on specific NIC. Client: `iperf3 -c 192.168.1.10 -t 30 -R` tests reverse direction (download). Use `-b 100M` to limit bandwidth; `-P 4` spawns 4 parallel streams. Result shows Mbps throughput; lower latency variance = more stable link. Test multiple times and average.
