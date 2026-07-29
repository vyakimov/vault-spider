---
updated: 2026-01-25T18:36:00
id: 01M6E000000000000000000059
created: 2026-07-23T09:24:00
---
`rclone config create s3remote s3 provider=AWS env_auth=true` — setup S3 remote with env auth. `rclone sync /local s3remote:bucket --dry-run` tests before executing.
