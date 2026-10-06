# Lessons — Index

Durable corrections: something was wrong once, why, and the rule that prevents it. A lesson must be phrasable as "next time, do X instead of Y"; otherwise don't write it.

## Format

Filename: `YYYY-MM-DD-<slug>.md`

```yaml
---
title: Short imperative rule
domain: cross-cutting
applies_to: [example-team]   # or [all]; check fails without it
visibility: self
tags: [verification, research]
summary: One sentence — the rule, not the story.
status: verified
updated: 2026-09-01
sources:
  - where the mistake happened
---
```

Body, briefly: what happened, the generalizable cause, and the rule stated so it can be followed without the story.

## Keeping it lean

- **Amend before adding.** A repeat of the same mistake goes into the existing lesson's account, sharpening its rule.
- **Merge overlaps.** When `check` warns that two lessons share over half their keywords, fold them into the more general rule and delete the narrower one.

## Lessons

<!-- kb:generated:lessons -->
| Date | Lesson | Applies to |
|---|---|---|
| 2026-10-01 | [Search name variants before concluding something doesn't exist](2026-10-01-search-name-variants-before-concluding-absence.md) | all |
<!-- kb:generated:end -->
