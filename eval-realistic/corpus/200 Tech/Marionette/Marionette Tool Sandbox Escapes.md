---
tags:
  - homelab
  - security
updated: 2026-06-14T10:36:00
id: 01M6A00000000000000000000D
created: 2026-02-11T09:12:00
---
Two near-misses where a proposed tool call would have escaped the allowlist sandbox. The first was a `curl` command that tried to reach `http://localhost:8888`, which isn't in the allowlist but assumed it would route to an internal service. The second was a symbolic-link traversal in a file-move tool that tried to follow a symlink into a forbidden directory. Both were caught by the sandbox logic before execution; the model never actually ran them.

The fix was to tighten the allowlist regex to disallow localhost IPs outright (external URLs only), and to add a symlink-resolution step to file operations so the sandbox sees the real path, not the link. Since then, no escapes in three months of continuous operation.
