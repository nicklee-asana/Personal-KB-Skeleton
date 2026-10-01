# Projects

One directory per project. Long-form specs, iterated on during design and read whole.

## Why these live outside `kb/`

`kb/` is built on assumptions a good spec breaks all four of:

| `kb/` assumes | A spec is |
|---|---|
| One topic per file | Inherently multi-topic — problem, approach, alternatives, rollout |
| Under ~150 lines | As long as the thinking requires |
| Read via routing, three files max | Read whole, start to finish, by whoever is doing the work |
| Stable once written | Churning constantly until the design settles |

Forcing specs into `kb/` would mean weakening the rules that make `kb/` cheap to retrieve from. So they sit alongside it instead, and the relationship runs one way: **a project produces knowledge, and that knowledge gets extracted into `kb/`.** Same relationship `meetings/` has — working material on one side, settled knowledge on the other.

## How specs get found

Living outside `kb/` would otherwise make a spec findable only if you already knew it existed. So the `domain` field in each project's front matter earns its keep: that domain's `INDEX.md` carries a generated "Related project specs" table, listing every project pointing at it with its current status.

Nothing to maintain by hand — set `domain` correctly and run `python3 scripts/kb.py sync`. Specs never appear in a team export, since `export` covers `kb/` only.

## Layout

```
projects/<project-name>/
├── README.md         the spec; the only required file
├── decisions.md      optional: decision log, once README.md gets long
└── notes/            optional: research, benchmarks, scratch
```

Directory names are lowercase and hyphenated. Prefix with `_` to have tooling ignore a directory (`_template` is ignored this way).

## Front matter

`README.md` in each project directory needs front matter. `scripts/kb.py check` validates it.

```yaml
---
title: Observability documentation gap
status: designing
domain: example-team
visibility: self
started: 2026-09-01
updated: 2026-09-01
summary: One sentence on what the project is and why it exists.
---
```

| Field | Rule |
|---|---|
| `title` | Matches the H1 |
| `status` | `exploring` \| `designing` \| `implementing` \| `shipped` \| `abandoned` |
| `domain` | The `kb/domains/` entry this relates to, or `cross-cutting` |
| `visibility` | `team` or `self`. Default `self` while a design is half-formed |
| `started` | ISO date |
| `updated` | ISO date of last substantive edit |
| `summary` | One sentence |

## The lifecycle

`exploring` → `designing` → `implementing` → `shipped` or `abandoned`.

**When a project reaches `shipped` or `abandoned`, extract what it taught into `kb/`.** This is the step that makes the directory worth keeping:

- How the thing works now that it exists → the relevant domain note, `status: verified`
- Why a particular approach was chosen → the domain note, or a lesson if the reasoning generalizes
- Why it was abandoned → **especially this.** An abandoned project is a documented dead end, which is worth more than an undocumented one and is exactly the knowledge that gets lost. Most halted initiatives leave no trace.

A shipped project whose spec was never mined is a spec nobody will read again.

## Writing specs

Start from `_template/README.md`. Its sections exist to force the parts that are easy to skip: what you are explicitly *not* doing, what you considered and rejected, and what you still don't know.

Keep the spec honest as it changes. A spec edited to look like it predicted the outcome is worse than no spec, because it teaches you nothing next time.
