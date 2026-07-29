---
tags:
  - homelab
  - llm
updated: 2026-01-15T10:47:00
id: 01M6A00000000000000000000E
created: 2026-03-12T09:19:00
---
Signal's message size limit is 32KB, which means long reports get split into chunks automatically. The bot sends them as thread replies to preserve context. Reactions (😂, ❤️, etc.) are logged but can't be used as command triggers — Signal's client SDK doesn't expose a reaction-intent API, only the fact that a reaction happened. Group chats are a special case: the bot mutes notifications after 5 consecutive messages to avoid spamming, and it stops responding if it detects more than 10 participants (to avoid turning into a party trick).
