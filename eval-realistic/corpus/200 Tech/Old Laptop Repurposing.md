---
updated: 2026-05-01T11:32:00
id: 01M6V00000000000000000000D
created: 2026-04-01T10:04:00
---
# Old Laptop Repurposing

Turning a retired laptop into a lightweight backup relay.

## The Hardware
A 2018 MacBook Pro with decent battery life and reliable wifi. It was slow by my standards but perfectly adequate for a background task. I wiped it clean, set it to auto-start, and left it in the closet running a single cron job: every midnight, it pulls a delta backup from LordByron over SSH and pushes it to a cloud storage service. Total network traffic is maybe 50MB most nights.

## Why This Works
It's a dedicated relay—it doesn't run anything else, so I don't have to worry about it locking up or getting bogged down. The laptop battery is in good shape, so it survives brief power dips. It's off the main tailnet (connected via a specific SSH key with restricted permissions) so even if someone compromises the backup account, they can't pivot to other machines. I've essentially created a third backup path (cloud storage) for about $0 in incremental cost.
