---
updated: 2026-07-22T19:23:00
id: 01M6E00000000000000000000Y
created: 2026-06-20T16:07:00
---
`nmap -sS 192.168.1.0/24` TCP SYN scan (stealthy, requires root). `nmap -sV hostname` probes service versions; `-O` attempts OS detection (slow, root required). Export results: `-oN output.txt` for text, `-oX output.xml` for XML (parseable). Avoid scanning without permission; use `-Pn` to skip ping if host blocks ICMP.
