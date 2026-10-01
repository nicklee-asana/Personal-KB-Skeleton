# Lessons — Index

Durable corrections. Each file records something that was wrong once, why it was wrong, and the rule that prevents it recurring.

**A lesson is not a diary entry.** If it wouldn't change what someone does next time, it doesn't belong here. The test: could this be phrased as "next time, do X instead of Y"?

## Format

Filename: `YYYY-MM-DD-<slug>.md`

```yaml
---
title: Short imperative rule
domain: cross-cutting
applies_to: [example-team]   # or [all]
tags: [verification, research]
summary: One sentence — the rule, not the story.
status: verified
updated: 2026-09-01
sources:
  - where the mistake happened
---
```

`applies_to` is what makes a lesson reachable. Domain indexes surface the lessons naming them, so a lesson without it is invisible to anyone reading the domain it concerns. `scripts/kb.py check` fails on a lesson that omits it.

Body sections, in order:

1. **What happened** — brief, concrete, no self-flagellation
2. **Why it happened** — the generalizable cause, which is the actual value
3. **The rule** — what to do differently, stated so it can be followed without rereading the story

## Keeping this directory worth reading

A lessons directory fails by accumulation rather than by error: thirty entries, several of them near-restatements of each other, and reading it stops being worth the time. Two rules hold that off.

**Merge overlapping lessons instead of adding another.** `check` warns when two lessons share more than half their significant keywords, which usually means the same mistake was written up twice from slightly different angles. Fold them into the more general rule — the one that would have prevented both — and delete the narrower one. Git keeps the original if the framing is ever wanted back.

**Prefer amending an existing lesson.** A second occurrence of the same mistake is stronger evidence for a rule already written down than it is a reason for a new file. Add the new instance to that lesson's "What happened" and sharpen the rule.

Nothing prunes automatically, and there's no cap. If this directory ever gets long enough that the count itself is the problem, that's a signal the entries are too specific, not that a limit is needed.

## Lessons

<!-- kb:generated:lessons -->
| Date | Lesson | Applies to |
|---|---|---|
| 2026-10-01 | [Search name variants before concluding something doesn't exist](2026-10-01-search-name-variants-before-concluding-absence.md) | all |
<!-- kb:generated:end -->
