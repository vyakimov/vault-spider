---
updated: 2026-06-04T11:51:00
id: 01M6V000000000000000000042
created: 2026-05-04T10:27:00
---
# Guest Network Isolation Test

Verification testing that the guest SSID truly blocks guest devices from accessing the LAN, as intended by the firewall rules.

## Test Methodology
I connected a test device to the guest network, then attempted to ping internal servers by both IP and hostname. Pings to LAN IPs returned no response. DNS queries for internal hostnames timed out or returned NXDOMAIN, confirming the guest network has no visibility to the internal DNS server. I also tried connecting to the HTTP port on a known machine—connection was refused as expected.

## Results and Implications
The isolation is solid. Guests can reach the internet but have zero visibility into LAN devices or services. The test also confirmed that guest devices can still reach the Bramble exit node if they somehow know its IP, which is acceptable since external IPs are not sensitive. The router logs showed no leaked DNS or ARP traffic between the networks. This setup will let me safely give guests the WiFi password without worrying about their devices probing the network.
