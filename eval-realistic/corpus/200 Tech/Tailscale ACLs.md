---
updated: 2026-06-02T09:10:31
id: 01M6J000000000000000000003
created: 2026-02-09T16:31:40
---
A [[Tailscale]] [[technote]] on the headscale ACL file.

Tags over hostnames: machines get `tag:server` or `tag:client` at registration, and rules refer
to tags, so replacing a machine doesn't mean editing policy.

```json
"acls": [
  {"action": "accept", "src": ["tag:client"], "dst": ["tag:server:*"]},
  {"action": "accept", "src": ["tag:server"], "dst": ["tag:server:*"]}
]
```

Default is deny, which you rediscover every time a new machine can ping nothing. Test with
`headscale policy check` before applying — a syntax error takes the whole tailnet's policy out.
