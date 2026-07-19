---
updated: 2026-06-02T08:52:17
id: 01M6B000000000000000000003
created: 2025-11-03T12:20:44
---
A [[vpn]] [[technote]]
- Tailscale mostly Just Works, but the interesting bits here are self-hosted

> [!SUMMARY] TL;DR
> The current tailnet is coordinated by **headscale on [[Bramble]]** (no Tailscale SaaS).
> [[PuddleJumper]] is a **subnet router advertising `192.168.4.0/24`**, so tailnet clients reach
> LAN devices without installing anything on them. MagicDNS gives every machine a stable name.
> This replaced the port-forwarding mess described in [[Flat Network - Archived 2024]].

Advertise the LAN from PuddleJumper:

```
tailscale up --advertise-routes=192.168.4.0/24 --accept-dns=true
```

then approve the route on the headscale side. Clients see `192.168.4.0/24` via PuddleJumper and
MagicDNS resolves `puddlejumper`, `lordbyron`, `bramble` without IPs.

Here is a chat explaining the moving parts

# Chat GPT Answer
Question:
What is the difference between a subnet router and running tailscale on every device?

AI Response:
A subnet router advertises an entire LAN prefix into the tailnet, so devices that cannot run
Tailscale (printers, NAS appliances, lightbulbs) are reachable through one gateway machine.
Running the client everywhere gives each device its own identity, per-device ACLs and direct
connections, at the cost of installing and updating the client on each one.

### Step 1: Advertise the route

On the gateway machine run `tailscale up --advertise-routes=<prefix>` and enable IP forwarding
(`sysctl -w net.ipv4.ip_foward=1` on Linux).

### Step 2: Approve the route

On the coordination server, approve the advertised route so clients start using it.

### Step 3: Test from a client

`tailscale ping` the gateway, then connect to a LAN-only address behind it.

Question:
Do I still need port forwarding on the router?

AI Response:
No. All connections are outbound from each node to the coordination server and relays, so no
inbound ports need to be opened on your home router at all.
