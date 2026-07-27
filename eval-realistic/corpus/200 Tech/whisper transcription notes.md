---
updated: 2026-02-27T14:38:00
id: 01M6E000000000000000000165
created: 2026-01-25T19:22:00
---
`whisper audio.mp3 --model small --output_format srt` transcribes to SRT subtitles. Larger models (medium/large) handle accent/noise better but need 4+ GB VRAM. Use `--language en` if auto-detect fails on accented speech.
