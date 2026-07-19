---
updated: 2026-06-02T09:10:31
id: 01M6J000000000000000000004
created: 2026-03-25T11:19:55
---
a [[Tailscale]] [[technote]] on using home as an exit node while travelling

`tailscale up --advertise-exit-node` on [[PuddleJumper]], approve it server-side, then on the
laptop pick it as the exit node. All traffic leaves via home — hotel wifi sees only the tunnel.

Worth remembering: the exit node is opt-in per client and off by default, and battery cost on
the laptop is real. Turn it off when back on a network you trust.
