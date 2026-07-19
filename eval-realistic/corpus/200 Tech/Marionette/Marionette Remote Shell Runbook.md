---
updated: 2026-06-02T08:44:03
id: 01M6A000000000000000000002
created: 2026-03-08T10:17:55
---
# Marionette — Remote Shell Runbook

A [[Marionette]] [[technote]] — the runbook for pairing the PuddleJumper node with the gateway.

> [!SUMMARY] TL;DR
> Pair the node on [[PuddleJumper]] with the gateway on **Bramble** so agents can run allowlisted
> commands at home. The node dials out over [[Tailscale]] to the gateway's tailnet address
> `100.64.0.7`; nothing is exposed to the public internet. Versions must match exactly.

## Prereqs

1. Bramble gateway running (see `bootstrap-bramble.md`).
2. Tailscale up on both machines; `tailscale status` shows Bramble as `100.64.0.7`.
3. `marionette` CLI installed on PuddleJumper **at the same version as the gateway**:

   ```sh
   ssh bramble 'marionette --version'
   marionette --version   # must match; pin with npm install -g marionette@<exact>
   ```

## Token exchange

The gateway mints a one-shot pairing token. On Bramble:

```sh
marionette nodes mint-token --name "puddlejumper-shell"
```

Tokens are single-use and **expire after 10 minutes**; mint one right before you pair.
The node never listens for inbound connections — it dials out to `100.64.0.7:9410` over the
tailnet, so no port forwarding and nothing public.

## Install the node service (PuddleJumper)

```sh
marionette node install \
  --gateway 100.64.0.7:9410 \
  --token <pairing_token> \
  --display-name "puddlejumper-shell"
```

This writes `~/.marionette/node.json`, installs the LaunchAgent `net.marionette.node`, and starts
the node. It connects and blocks until approved.

## Approve on the gateway (Bramble)

```sh
ssh bramble 'marionette nodes pending'
ssh bramble 'marionette nodes approve <requestId>'
```

The approval must show `"caps": ["shell"]`.

## Verify

```sh
ssh bramble 'marionette nodes list --connected'   # puddlejumper-shell: just now
marionette node status                             # Runtime: running
tail -20 ~/.marionette/logs/node.err.log           # expect nothing
```

## Gotchas

- **Version skew**: node and gateway must run the same Marionette version. A mismatch shows up
  as a crash loop with protocol errors in `node.err.log`.
- **Stale token**: a token older than 10 minutes fails with `token_expired`; mint a fresh one.
- **Log noise**: crash loops balloon `node.log` fast; truncate with `: > ~/.marionette/logs/node.log`.
