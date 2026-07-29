---
updated: 2026-07-09T10:10:00
id: 01M6E000000000000000000121
created: 2026-06-07T11:50:00
---
`launchd` (macOS) runs as logged-in user with environment variables intact; `cron` has minimal env. Put `.plist` files in `~/Library/LaunchAgents/` for user jobs. Check logs with `log stream --predicate 'process=="launchd"'`.
