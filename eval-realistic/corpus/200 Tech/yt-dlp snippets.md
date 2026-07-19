---
updated: 2026-06-02T09:05:20
id: 01M6H000000000000000000004
created: 2025-10-02T19:27:44
---
A [[technote]] and [[code snippet]] for yt-dlp.

Audio only, best quality, sane filename:
```bash
yt-dlp -x --audio-format m4a -o '%(title)s.%(ext)s' <url>
```

Entire playlist but skip what's already downloaded: add `--download-archive done.txt` — the
archive file is the whole trick, everything else is flags.
