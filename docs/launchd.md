# Periodic Vault Spider sync with launchd

Vault Spider ships a macOS per-user LaunchAgent named `ai.vault-spider.sync`. A LaunchAgent is a
better fit than a system daemon: it runs as the signed-in user, can read the user's vault and
repository `.env`, and does not require root.

## Default behavior

- Runs once when loaded and every 60 minutes afterward.
- Launches through the absolute `uv` binary recorded at install time, then executes the serialized
  maintenance helper and stable `bin/vault-spider sync` wrapper from the repository root.
- Uses the normal root resolution from `config.yaml` and the normal Chroma path.
- Serializes runs with a non-blocking file lock, so a slow sync is not started twice.
- Writes compact JSON-line events to the launchd log and the latest full sync envelope to a private
  state directory.
- Runs with background process priority and low-priority I/O.

Incremental sync computes a content/path diff first. When every indexed note is unchanged, it makes
no embedding calls and does not replace index entries; the result simply reports the unchanged
count.

## Install or update

The setup command is a dry run unless `--apply` is supplied:

```bash
uv run scripts/setup_launchd.py
uv run scripts/setup_launchd.py --apply
```

The apply command validates the generated plist, installs it at
`~/Library/LaunchAgents/ai.vault-spider.sync.plist`, loads it into the current GUI session, and
starts a run immediately. Re-running the command safely updates the existing agent.

Choose another interval, in minutes, when installing:

```bash
uv run scripts/setup_launchd.py --apply --interval-minutes 30
```

Five minutes is the enforced minimum. Hourly is the recommended default for a personal vault.

## Optional lint

Enable a read-only `vault-spider lint` after each successful sync with:

```bash
uv run scripts/setup_launchd.py --apply --with-lint
```

Lint is disabled by default because it scans the full corpus and an hourly health report is usually
more noise than signal. When enabled, the log contains only its summary; the full latest envelope is
stored privately at `~/Library/Caches/VaultSpider/last-lint.json`. No fixer flags are ever passed.

Enrichment is intentionally excluded. `enrich` requires a particular note or stdin, invokes an LLM,
and produces a proposal that still needs a deliberate apply step. Scheduling it without a note
selection and review workflow would spend tokens without safely improving the vault.

## Status and logs

Inspect the loaded service:

```bash
launchctl print gui/$(id -u)/ai.vault-spider.sync
```

Trigger a run immediately:

```bash
launchctl kickstart -k gui/$(id -u)/ai.vault-spider.sync
```

Logs and latest envelopes are kept at:

```text
~/Library/Logs/VaultSpider/sync.stdout.log
~/Library/Logs/VaultSpider/sync.stderr.log
~/Library/Caches/VaultSpider/last-sync.json
~/Library/Caches/VaultSpider/last-lint.json  # only with --with-lint
```

The logs and state directories are mode `0700`; full state files are mode `0600`. The plist contains
paths and options but no API keys. The job's working directory is the repository root, allowing
`python-dotenv` to load the gitignored `.env` normally.

### macOS Documents-folder permission

When either the repository or vault is under `~/Documents`, macOS may deny some background
executables with `Operation not permitted` even though the same command succeeds in Terminal. The
agent launches through the absolute `uv` binary shown by the setup dry run; this avoids the common
denial applied to background `/usr/bin/python3` processes.

If macOS still denies access, use **System Settings → Privacy & Security → Files and Folders** to
allow that `uv` binary to access Documents. Full Disk Access is a broader fallback. Moving both the
repository and vault outside macOS-protected Desktop/Documents locations is the other option. After
changing the permission, reload and test:

```bash
uv run scripts/setup_launchd.py --apply
launchctl print gui/$(id -u)/ai.vault-spider.sync
tail -20 ~/Library/Logs/VaultSpider/sync.stderr.log
```

A successful run writes `last-sync.json` under `~/Library/Caches/VaultSpider/` and reports exit code
zero in `launchctl print`.

## Disable lint or uninstall

Reapply without `--with-lint` to return to sync-only operation:

```bash
uv run scripts/setup_launchd.py --apply
```

Preview and then apply removal:

```bash
uv run scripts/setup_launchd.py --uninstall
uv run scripts/setup_launchd.py --uninstall --apply
```

Uninstalling unloads and removes the plist but preserves logs and latest-run state. If the repository
is moved, rerun the setup command from its new location so the installed absolute paths are updated.
