# Meetings — Index

Raw records of 1:1s, standups, design discussions, and onboarding sessions. Captured as they happen, in the words they happened in.

**Meeting notes are raw material, not the finished product.** A meeting note preserves what was said and by whom; a domain note holds what turned out to be true. When a meeting produces a durable fact, write that fact into the relevant domain file and cite the meeting in its `sources`. The meeting note stays as provenance.

This is why meetings don't appear in domain indexes. Retrieval should route to "what do we know about the CLI," not to "what was said on August 25."

## Format

Filename: `YYYY-MM-DD-<slug>.md`

```yaml
---
title: 1:1 with <name> — <topic>
domain: example-team                # or cross-cutting
visibility: self                # meetings name people; default to self
tags: [1-1, onboarding]
summary: One sentence on what was covered.
status: reported                # it's what someone said, not what you verified
updated: 2026-09-01
sources:
  - 1:1, September 1 2026
---
```

`status: reported` is almost always right for a meeting. Something said in a meeting is a claim until you check it, and the whole point of the status field is keeping that distinction visible.

`visibility: self` is the default because meeting notes record who said what, including things people said informally. `check` warns if a meeting is marked `team`.

## What to write down

Decisions and the reasoning behind them, ownership claims, names attached to areas, anything contradicting what's already recorded, and follow-ups you agreed to. Skip scheduling and logistics — this is a knowledge base, not a calendar.

## Meetings

<!-- kb:generated:meetings -->
_No meetings recorded yet._
<!-- kb:generated:end -->
