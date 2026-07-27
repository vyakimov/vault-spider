---
updated: 2026-01-12T19:23:00
id: 01M6E000000000000000000150
created: 2026-07-10T16:07:00
---
Set `SSH_AUTH_SOCK=~/.1password/agent.sock` in `.zprofile`. 1Password's agent handles SSH keys from your vault without storing passphrases. Requires 1Password 7.8+; enable in Settings > Developer > SSH Agent.
