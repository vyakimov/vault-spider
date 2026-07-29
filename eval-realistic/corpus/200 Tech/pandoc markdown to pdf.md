---
updated: 2026-04-19T16:32:00
id: 01M6E00000000000000000000V
created: 2026-03-17T13:28:00
---
`pandoc input.md -o output.pdf` requires `pdflatex` (via `mactex` on macOS). Use `-V geometry:margin=1in` for custom margins; `-H header.tex` injects LaTeX preamble. Convert to other formats: `pandoc input.md -o output.docx` or `-o output.html`. For HTML: add `-s -c style.css` for self-contained doc with custom CSS.
