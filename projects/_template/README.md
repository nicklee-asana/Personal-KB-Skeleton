---
title: <Project name>
status: exploring
domain: cross-cutting
visibility: self
started: YYYY-MM-DD
updated: YYYY-MM-DD
summary: One sentence on what this is and why it exists.
---

# <Project name>

## Problem

What is actually wrong today, stated so someone unfamiliar could agree it's a problem. Symptoms and who feels them, not the solution.

## Why now

What makes this worth doing at this moment rather than later. If the honest answer is "it's interesting," say that — it's a legitimate reason and a different kind of bet.

## Non-goals

What this explicitly does not attempt. The most useful section in the document and the one most often skipped: it's what stops scope creep later, and it's what makes review possible, because a reviewer can't tell you the boundary is wrong until you've drawn one.

## Approach

The proposed design. Enough detail that someone else could implement it, or that you could implement it in three weeks having forgotten the reasoning.

## Alternatives considered

Each with why it was rejected. Reasons decay — "too slow" is worthless in six months, "adds a round trip per request, measured at 40ms p50" survives.

Also record alternatives rejected for non-technical reasons: no ownership, wrong team, bad timing. Those get revisited when circumstances change, and nobody remembers which was which.

## Open questions

What is still unknown, and who or what would resolve it. Keep this current — a spec with no open questions either finished or stopped being honest.

## Rollout

How it ships: order of operations, what can be reverted, what can't, what to watch afterward.

## Decision log

Append-only. Date, decision, and the reasoning at the time. Never rewrite an entry when a decision turns out wrong — add a new one superseding it, since the pair is what teaches you something.

| Date | Decision | Reasoning |
|---|---|---|
| YYYY-MM-DD | | |
