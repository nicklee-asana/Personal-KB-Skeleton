---
title: Search name variants before concluding something doesn't exist
domain: cross-cutting
applies_to: [all]
visibility: team
tags: [research, search, verification]
summary: A negative search result only rules out the pattern you searched, not the thing you were looking for.
status: verified
updated: 2026-10-01
sources:
  - a directory search for an exact name that missed a prefixed directory
---

# Search name variants before concluding something doesn't exist

An example lesson. A directory search for `^cli$` "proved" a repo had no command-line tool; it lived in a directory with a prefix, and a stale doc that also left it out seemed to confirm the miss.

- **Search three ways before reporting absence:** exact name, substring, and the content the thing would contain.
- **Report the pattern, not the conclusion:** "no directory named exactly `cli`".
- **Two weak negatives aren't one strong one** when they could share a cause.
- **A person's direct knowledge outweighs a search miss.**
