---
updated: 2026-06-02T08:44:03
id: 01M6A000000000000000000003
created: 2026-02-12T16:33:20
---
A [[Marionette]] note that outlines when tools can operate outside the sandbox

marionette.json snippet:

```json
"tools": {
  "shell": {
    "host": "gateway",
    "security": "allowlist",
    "ask": "on-miss"
  },
  "elevated": {
    "enabled": true,
    "allowFrom": {
      "signal": ["primary-account"]
    }
  }
}
```

So: shell commands default to the sandbox, the allowlist is checked first, and anything not on it
asks before running. Elevated access is limited to the **one allowlisted Signal account** — no
other chat can request it.

File writes stay inside `~/.marionette/workspace` unless a bind mount says otherwise. Binds bypass
sandbox isolation for those paths, so only mount directories you are comfortable handing over.

Does that clarify things? Want to add any bind mounts?
