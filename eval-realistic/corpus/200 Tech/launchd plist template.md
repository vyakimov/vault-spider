---
updated: 2026-06-28T15:05:00
id: 01M6E000000000000000000036
created: 2026-05-26T10:25:00
---
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>local.backup</string>
  <key>ProgramArguments</key>
  <array><string>/usr/local/bin/backup.sh</string></array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>2</integer><key>Minute</key><integer>0</integer></dict>
</dict>
</plist>
```
Place in `~/Library/LaunchAgents/local.backup.plist`; load with `launchctl load ~/Library/LaunchAgents/local.backup.plist`.
