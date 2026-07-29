---
updated: 2026-06-19T12:44:00
id: 01M6E000000000000000000183
created: 2026-05-17T13:16:00
---
`rclone config` adds B2 remote with API key + app key. `rclone sync local/ b2://bucket/` pushes files; cheaper than S3 at $6/TB egress. Metadata limitations (no xattrs); sync is reliable but slow on large trees due to API throttling.
