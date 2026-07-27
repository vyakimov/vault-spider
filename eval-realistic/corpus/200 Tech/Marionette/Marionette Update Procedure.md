---
tags:
  - homelab
  - runbook
updated: 2026-04-13T10:25:00
id: 01M6A00000000000000000000C
created: 2026-01-10T09:05:00
---
# Marionette Update Procedure

The gateway and node must stay in sync during releases, or they'll enter a version-skew crash loop. The gateway talks to the node over a versioned gRPC protocol; if they diverge, the gateway hangs waiting for a handshake that never completes.

## Safe Update Steps

1. Stop the node (`systemctl stop marionette-node`)
2. Update both binaries (`apt upgrade marionette-gateway marionette-node`)
3. Restart the node first (`systemctl start marionette-node`)
4. Wait 10 seconds for it to fully initialize
5. Restart the gateway (`systemctl restart marionette-gateway`)
6. Check logs to confirm the handshake succeeded

Never update the gateway first — it will try to connect to the node before it's upgraded, see a protocol mismatch, and crash repeatedly. The node-first approach gives it a chance to boot cleanly before the gateway tries to connect.
