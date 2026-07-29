---
updated: 2026-01-17T18:26:00
id: 01M6E000000000000000000129
created: 2026-07-15T19:34:00
---
`poetry add package` updates `pyproject.toml` and `poetry.lock` atomically. Cleaner than pip; slower than uv. Best for libraries; overkill for scripts. `poetry build` creates wheels and sdists for distribution.
