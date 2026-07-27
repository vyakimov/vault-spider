---
updated: 2026-03-23T16:52:00
id: 01M6E000000000000000000187
created: 2026-02-21T17:08:00
---
`wg genkey | tee privatekey | wg pubkey > publickey` generates keys. Server config: `[Interface] PrivateKey=... Address=10.0.0.1/24` + `[Peer] PublicKey=... AllowedIPs=10.0.0.2/32`. Client mirrors with swapped keys. Bring up with `ip link add wg0 type wireguard` + `ip addr add ...` + `wg set ...`.
