---
tags:
  - index
updated: 2026-06-02T09:05:20
id: 01M6H000000000000000000006
created: 2026-01-19T14:20:51
---
A [[technote]] on Bramble — the small VPS that runs the always-on pieces.

It runs:
- The [[Marionette]] gateway ("brain"); [[PuddleJumper]] pairs to it as a node.
- headscale, coordinating the tailnet — see [[Tailscale]].
- Nothing else on purpose. 2 vCPU / 4GB; if something needs more it belongs at home.

Boring by design: unattended-upgrades on, a weekly snapshot, and one admin user. Rebuild notes
live in `bootstrap-bramble.md` next to the deploy scripts, not in the vault.
