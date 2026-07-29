---
updated: 2026-01-08T14:48:00
id: 01M6E000000000000000000328
created: 2026-01-07T09:12:00
---
`ln source target` creates hardlink (same inode, both names point to data). `ln -s source target` creates symlink (shortcut, can cross filesystems). Symlinks break if source moves.
