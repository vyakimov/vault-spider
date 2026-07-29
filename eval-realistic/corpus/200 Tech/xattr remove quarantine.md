---
updated: 2026-02-24T12:14:00
id: 01M6E000000000000000000266
created: 2026-02-23T19:46:00
---
`xattr -d com.apple.quarantine app.app` — removes download quarantine bit. Files downloaded via Safari/Mail get this flag; Gatekeeper then warns on launch. Useful for unverified binaries.
