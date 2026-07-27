---
updated: 2026-06-21T11:26:00
id: 01M6V000000000000000000007
created: 2026-05-21T10:22:00
---
# Home Server Power Outage Response

What the UPS covers and what still needs a manual restart after a long outage.

## UPS Scope
The UPS powers the network switch, wifi, and headscale controller for about 45 minutes. That's enough time for the house to get power back or for me to come home and see the blinking lights. The file servers (LordByron, Blackbird) are plugged into the wall directly—losing those immediately is annoying but not catastrophic. I made peace with this because powering both servers on UPS would need a bigger battery.

## Post-Power Recovery
If the power was out long enough for everything to fully shut down, I have to restart LordByron first (it's the storage anchor), then Blackbird, then trigger the NFS mounts on the other machines. This is manual—no fancy startup orchestration. The database usually recovers fine from an unclean shutdown, but I always check logs. I've been burned once by a corrupted index and now I'm paranoid about it.
