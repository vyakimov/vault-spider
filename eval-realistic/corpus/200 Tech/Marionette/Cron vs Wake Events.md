---
updated: 2026-06-02T08:44:03
id: 01M6A000000000000000000004
created: 2026-04-02T11:09:12
---
Directly relevant for [[Marionette]] but probably broadly for [[LLM]] scheduling.


## **Cron sessions** (the obvious default)

**Pros:**

- Familiar semantics, easy to reason about
- Fires whether or not anything interesting happened
- Good for digests: "every morning at 07:30, summarize the queue"

**Cons:**

- Wasteful when there is nothing to do
- A burst of events between ticks gets batched or missed
- Timezone bugs, forever

## **Wake events**

**Pros:**

- Fire on a concrete signal (file appeared, message arrived, price moved)
- No empty runs — the session wakes with its reason attached
- Compose well: one watcher, many subscribers

**Cons:**

- Requires something to emit the event
- Harder to debug ("why did nothing wake up?")
- Storms if the source misbehaves

## **When wake events make sense:**

1. **Bursty sources** — mail, chat, webhooks
2. **Expensive sessions** — don't pay for empty cron runs
3. **Latency matters** — react in seconds, not at the next tick

**TL;DR:** cron for periodic digests, wake events for reacting to things. If the session would
mostly find nothing to do, it should be a wake event.

Fenwick
