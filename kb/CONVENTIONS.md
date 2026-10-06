# Conventions

How notes are written and filed, so an agent can answer from two indexes and one leaf.

## Front matter

Every leaf file starts with YAML front matter; without it a file is invisible to search.

```yaml
---
title: Deploy pipeline
domain: example-team
visibility: team
tags: [deploys, ci]
summary: Deploys are gated on the integration suite; how a change reaches production and which step most often blocks it.
status: verified
updated: 2026-08-31
sources:
  - path/to/deploy/pipeline.yml
---
```

| Field | Rule |
|---|---|
| `title` | Human-readable. Matches the H1. |
| `domain` | Directory name under `kb/domains/`, or `cross-cutting` for notes directly in `kb/`. |
| `tags` | Lowercase, hyphenated, 2–5. Aggregated into `tags.md`. |
| `summary` | **One sentence**, answering "what would I learn here?" Indexes are generated from it; never restate it by hand. |
| `status` | `verified`, `reported`, or `stale`. |
| `updated` | ISO date of last substantive edit. |
| `sources` | Paths, URLs, or people. Required when `status: verified`. |
| `visibility` | **Required**, `team` or `self`. No default. |
| `applies_to` | **Lessons only.** Domains the lesson concerns, or `[all]`. |
| `half_life` | Optional. Positive whole days; see Dates. |
| `size_exempt` | Optional. `true` waives the size limit; state the reason in the body. |

## Status

- **`reported`**: someone told you. Attribute it.
- **`verified`**: checked against code, a primary doc, or a command; `sources` says which. Never promote without checking.
- **`stale`**: known outdated. Keep only if the history is instructive; say what superseded it.

## Files

```
kb/
├── INDEX.md          top-level router
├── CONVENTIONS.md
├── glossary.md
├── tags.md           generated
├── domains/<domain>/INDEX.md, <topic>.md
├── lessons/INDEX.md, YYYY-MM-DD-<slug>.md
└── meetings/INDEX.md, YYYY-MM-DD-<slug>.md
```

- **One topic per file.** If the title could be two titles joined by "and", split it.
- **Names are lowercase, hyphenated, descriptive**: `mcp-server.md`, not `mcp.md` or `MCPServer.md`.
- **Leaf files stay under 150 lines**, else split by subtopic or set `size_exempt`.

## Indexes

A domain `INDEX.md` only routes; real content goes in a leaf. Regions between `<!-- kb:generated:NAME -->` and `<!-- kb:generated:end -->` are produced from front matter by `kb.py sync`. Never hand-edit inside them; everything outside is hand-written and preserved.

## Visibility

The directory answers "personal or work?"; `visibility` answers "shareable?" within `kb/`.

| Tier | Where | Contains |
|---|---|---|
| `team` | `kb/` | Facts about systems, written for a teammate. |
| `self` | `kb/` | Open questions, recorded mistakes, notes naming colleagues. |
| — | `personal/` | Career, compensation, interpersonal material, side projects. Never in `kb/`. |

A work fact goes in `kb/` even if not shareable (`self`), because nothing routes into `personal/`.

`kb.py export DIR` writes only `team` notes, regenerates indexes from them, and drops rows pointing at withheld files. It refuses if `check` fails, refuses a target containing this repo, and refuses a non-empty target lacking the `.kb-export` marker. `team` means shareable with colleagues, not public.

Write `team` notes impersonally. When a note is mostly shareable, move its personal parts to their `self` homes (open questions, lessons) rather than marking the whole file `self`.

## Meetings

Meeting notes go in `kb/meetings/`, dated, `status: reported`, `visibility: self`. Write durable facts into the owning domain note and cite the meeting in its `sources`. A mostly career or interpersonal conversation goes to `personal/meetings/`, with only system facts extracted; cite it in prose (`1:1, September 3 2026`), never by path. Format in `meetings/INDEX.md`.

## Lessons

Every lesson declares `applies_to`. Retrieval reaches lessons only through each domain index's generated "Lessons that apply here" table. Format in `lessons/INDEX.md`.

Write a lesson only when reasoning was wrong, not when the world changed. "The AoR doc was edited" is not a lesson; "I treated a doc's silence as evidence of absence" is.

## Summaries

The summary is copied verbatim into the index and is all an agent sees when choosing which note to open. Write the sentence you'd want when choosing between this note and four others. Placeholders (`unchanged`, `n/a`, `see above`, `TBD`) are rejected.

## Dates and `half_life`

Notes are corrected when something contradicts them, not on a schedule. Nothing warns that `updated` is old; never bump it without re-checking.

For facts you'll never naturally re-encounter (ownership, headcount, vendor terms, deprecation dates), set `half_life` in days. Indexes then append `_(aging)_` past one half-life and `_(may be stale)_` past two. It is a label, never a warning or deletion. Keep it rare (about ten notes at most) and set it to how fast the subject moves; team ownership is a 12–18 month question.

## When a note is contradicted

Update it to the new state, set `updated`, and cite what you checked in `sources`. Status follows the source: primary makes it `verified`, hearsay `reported`.

Which side wins:

1. **A primary source** (code, config, owned doc) beats everything, regardless of date.
2. **Same provenance**: newer wins.
3. **Can't tell**: don't pick. Record both, say they conflict, set `status: reported`.

If you fix one claim without re-checking the rest, say so in the note.

## Tooling

```sh
python3 scripts/kb.py check        # verify invariants; non-zero exit on failure
python3 scripts/kb.py sync         # regenerate generated blocks
python3 scripts/kb.py export DIR   # write a team-shareable copy
```

`check` **fails** on: missing or incomplete front matter, unknown `domain`, invalid `status` or `visibility`, `verified` without `sources`, placeholder `summary`, unparseable `updated`, non-positive `half_life`, a domain missing from `kb/INDEX.md` or lacking its own `INDEX.md`, a lesson without valid `applies_to`, a team note citing a `personal/` path, broken relative links, and stale generated blocks.

It **warns** on: files over 150 lines without `size_exempt`, first-person prose or the `people` tag in a team note, a meeting marked `team`, a summary that restates the title, and two lessons with over half their keywords in common. It prints a `note` when an aging marker moved since the last sync.

Run `sync` after any change. The `.githooks/` pre-commit hook runs `check` if enabled (`setup/README.md`).

## Style

- Spell out acronyms on first use in each file; files are read in isolation.
- Prose over fragments. Tables only for enumerable facts.
- Cite full file paths, not line numbers.

## What doesn't belong

- Compensation, performance, career, interpersonal friction, personal life: `personal/`.
- Scheduling and logistics. Meeting content goes in `meetings/`; arrangements don't.
- Anything already documented in the repo you work in. Link to its docs instead of copying.
- Project specs: they live in `projects/` (see `projects/README.md`). What a project concluded belongs here.
