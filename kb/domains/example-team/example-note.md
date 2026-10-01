---
title: Example note
domain: example-team
visibility: team
tags: [example, conventions]
summary: A worked example of a leaf note — the shape every note takes, and what makes one worth writing; delete it once you have real notes.
status: verified
updated: 2026-10-01
sources:
  - kb/CONVENTIONS.md
---

# Example note

A good note records a trap that cost real time and that the code or docs won't tell the next person. For example: "the integration suite passes locally but fails in CI because CI runs it against a fresh database, so any test relying on seeded data needs its own fixture."

Keep it to the trap and the fix, in a handful of sentences. The `summary` above is what the domain index shows, so it carries most of the routing weight: write it as the one sentence you would want to read when choosing between this note and four others.

Set `status: verified` only when `sources` names the code, doc, or command you checked. Something a colleague told you is `reported` until you check it.
