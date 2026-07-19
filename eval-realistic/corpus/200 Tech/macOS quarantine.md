---
updated: 2026-06-02T09:05:20
id: 01M6H000000000000000000005
created: 2026-02-25T15:50:09
---
a [[technote]] on the macOS quarantine attribute

Downloaded binaries refuse to run ("cannot be opened because the developer cannot be
verified"). The fix:

```bash
xattr -d com.apple.quarantine ./the-binary
```

For a whole extracted folder use `-r`. This is TCC-adjacent but a different mechanism than the
[[Photo Sync Fuckery]] problem — quarantine is per-file metadata, not a privacy permission.
