---
updated: 2026-01-05T12:24:00
id: 01M6E000000000000000000143
created: 2026-07-03T09:36:00
---
`curl -X POST -H 'Content-Type: application/json' -d '{"key":"value"}' http://localhost:8080/webhook` tests a webhook. Use `--data-binary @payload.json` for file payloads. Add `-v` to see headers; `-w '%{http_code}'` for status code only.
