---
tags:
  - index
updated: 2026-06-02T08:41:19
id: 01M6A000000000000000000001
created: 2026-01-19T14:02:41
---
# Marionette

An [[LLM]] [[technote]] hub. Marionette is the self-hosted personal-agent gateway I run —
reachable over Signal, with tools, playbooks and cron-driven sessions.

> [!INFO] Not to be confused with Lantern
> [[Lantern]] is a **separate harness**, run in parallel with Marionette — not a rename of it and
> not a replacement. Notes here are about Marionette specifically.

## Architecture
The setup moved from everything-on-[[PuddleJumper]] to a **gateway/node split**: the *gateway*
("brain") runs on the [[Bramble]] VPS, and PuddleJumper runs as a *node* ("hands") executing
allowlisted commands on the LAN.
- [[Marionette Remote Shell Runbook]] — pairing the node with the gateway.
- [[Marionette Permissions]] — when tools may run outside the sandbox.

## Operations
- [[Marionette Tools]] — the tool list.
- [[Cron vs Wake Events]] — the two ways of scheduling sessions, compared.
- [[Photo Sync Fuckery]] — launchd jobs can't read the Photos library on macOS.

## Related
- [[Lantern]] — the other harness, run in parallel.
- [[Tailscale]] — how the node reaches the gateway.
