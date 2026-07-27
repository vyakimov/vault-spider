---
updated: 2026-01-11T15:55:00
id: 01M6E000000000000000000279
created: 2026-01-10T20:35:00
---
`printf "%s\n" "$var"` is POSIX/portable; echo's -e flag and escapes vary by shell. Use printf for: hex/octal output, fixed widths, consistent escaping. Echo fine for simple messages.
