---
updated: 2026-05-08T11:47:00
id: 01M6E000000000000000000042
created: 2026-04-06T16:43:00
---
`yq '.foo.bar' config.yaml` — extract nested YAML value. Use `yq eval-all 'select(.name == "prod")'` to filter arrays by field match.
