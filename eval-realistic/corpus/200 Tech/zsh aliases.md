---
updated: 2026-07-03T16:22:00
id: 01M6E000000000000000000037
created: 2026-06-01T11:38:00
---
Add to `~/.zshrc`: `alias ll='ls -lah'`, `alias gs='git status'`, `alias docker-ps='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'`. Use `alias -s log=less` for file-type aliases (`.log` files open in less). Source: `source ~/.zshrc` to reload. List all: `alias`.
