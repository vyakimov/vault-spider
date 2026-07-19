---
updated: 2026-06-02T09:01:12
id: 01M6E000000000000000000004
created: 2026-02-18T10:33:15
---
a [[technote]] on how to use [[python]] uv

`uv snyc` installs from the lockfile (into .venv)
`uv add requests` adds a dep and updates the lockfile
`uv run pytest` runs inside the environment without activating anything
Where are the environments? `.venv` in the project, tools live in `~/.local/share/uv`
`uv python install 3.12` manages interpreter versions too, no more pyenv
`uv pip install -e .` when something still expects pip

in VS Code remember to select the .venv interpreter or nothing imports
