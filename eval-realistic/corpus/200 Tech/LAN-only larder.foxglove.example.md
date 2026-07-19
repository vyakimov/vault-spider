---
updated: 2026-06-02T08:54:02
id: 01M6B000000000000000000005
created: 2026-04-19T10:05:51
---
a [[technote]] how to reach the [[Larder]] pantry app by name over [[Tailscale]] without exposing it

> [!SUMMARY] TL;DR
> `larder.foxglove.example` resolves to PuddleJumper's tailnet address `100.64.0.9`, and nginx on
> PuddleJumper binds **only** that address, so the app is reachable over the tailnet and nowhere
> else. No port in the URL.

The app itself listens on `localhost:8123`. Two problems: DNS and the port.

## Step 1 --- Point the name at the tailnet address

In the headscale DNS config, add an extra record:

```yaml
extra_records:
  - name: larder.foxglove.example
    type: A
    value: 100.64.0.9
```

## Step 2 --- Front it with nginx

```nginx
server {
    listen 100.64.0.9:80;
    server_name larder.foxglove.example;
    location / { proxy_pass http://127.0.0.1:8123; }
}
```

Binding to `100.64.0.9` (not `0.0.0.0`) is the whole point: the socket only exists on the
tailnet interface.

## Step 3 --- Verify it is tailnet-only

```bash
ss -ltnp | grep ':80'
```

You want `100.64.0.9:80`, not `0.0.0.0:80`. From a machine **off** the tailnet, the name must
not even resolve.

## Final architecture

```text
tailnet client
  ↓ MagicDNS / extra_records
larder.foxglove.example → 100.64.0.9
  ↓ HTTP
nginx on PuddleJumper :80
  ↓ proxy_pass
localhost:8123
```
