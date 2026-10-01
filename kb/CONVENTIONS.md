# Conventions

How notes are written and filed. The goal is that an agent can answer a question by reading two index files and one leaf file.

## Front matter

Every leaf file starts with YAML front matter. No exceptions — files without it are invisible to search.

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
| `domain` | Directory name under `kb/domains/`, or `cross-cutting` for notes that sit directly in `kb/` and belong to no single domain. |
| `tags` | Lowercase, hyphenated, 2–5 of them. Aggregated into `tags.md`, which is how cross-domain questions get answered. |
| `summary` | **One sentence.** The single source of truth for how this file is described — indexes are generated from it, so it is never restated by hand elsewhere. Write it as the answer to "what would I learn here?" |
| `status` | `verified`, `reported`, or `stale`. See below. |
| `updated` | ISO date of last substantive edit. |
| `sources` | Paths, URLs, or people. Required when `status: verified`. |
| `half_life` | Optional. Whole days after which the note starts being marked as aging in the indexes. Only for notes whose subject you would never naturally re-encounter. |
| `applies_to` | **Lessons only.** Domains the lesson is relevant to, or `[all]`. This is what makes a lesson reachable — see below. |
| `visibility` | **Required**, `team` or `self`. Controls whether the note appears in a shared export — see below. There is deliberately no default: sharing should be a decision someone made, not a consequence of leaving a line out. |
| `size_exempt` | Optional. `true` to waive the line guidance, with the reason stated in the body. |

## Status values

This is the most important convention in the repo, because the failure mode of a personal knowledge base is confidently recording something you were told and later treating it as fact.

- **`reported`** — someone told you. Useful, not yet trustworthy. Attribute it.
- **`verified`** — you checked it against code, a primary doc, or a command, and `sources` says which.
- **`stale`** — known outdated. Keep it if the history is instructive; say what superseded it.

When a `reported` claim turns out to be wrong, don't just fix it silently. Correct the file and write a lesson (see `lessons/INDEX.md`), because the *reason* it was wrong usually generalizes.

## File organization

```
kb/
├── INDEX.md                    top-level router
├── CONVENTIONS.md              this file
├── glossary.md                 terms and acronyms
├── tags.md                     generated tag index
├── domains/<domain>/
│   ├── INDEX.md                generated file table + generated lessons table
│   └── <topic>.md              leaf notes
├── lessons/
│   ├── INDEX.md
│   └── YYYY-MM-DD-<slug>.md
└── meetings/                   raw records; durable facts get extracted to domains
    ├── INDEX.md
    └── YYYY-MM-DD-<slug>.md
```

**One topic per file.** The test: could this file's title be two titles joined by "and"? If so, split it. A combined file makes every question about either half cost double.

**Names are lowercase, hyphenated, and descriptive.** `mcp-server.md`, not `mcp.md` or `MCPServer.md`. The filename should be enough to guess the contents.

**Leaf files stay under ~150 lines.** Past that, split by subtopic and let the domain index route between them. Set `size_exempt: true` when a file is genuinely better read whole, and say why in the body, such as a set of diagrams that cross-reference each other.

## Indexes

Every domain has an `INDEX.md` whose only job is routing. If an index starts accumulating real content, that content belongs in a leaf file.

**Index tables are generated, not written.** Regions delimited by `<!-- kb:generated:NAME -->` and `<!-- kb:generated:end -->` are produced from front matter by `scripts/kb.py sync`. Never hand-edit inside them; the next sync will overwrite it. Everything outside the markers is hand-written and preserved.

This exists because descriptions used to live in two places — the front-matter `summary` and the index row — in two different wordings. They drifted, and a drifting index degrades routing while still looking correct.

## Three tiers of visibility

There are two different questions here, and conflating them is how things leak.

**Personal or work?** decides the directory. Career, compensation, interpersonal material, and personal side projects go in `personal/`; work knowledge goes in `kb/`.

**Shareable with the team or not?** decides `visibility`, and only applies within `kb/`.

| Tier | Where | Contains |
|---|---|---|
| `visibility: team` | `kb/`, the default | Facts about systems. Written for a teammate to read. |
| `visibility: self` | `kb/` | Your open questions, your recorded mistakes, notes naming colleagues. |
| — | `personal/` | Career, compensation, interpersonal material, side projects. Never in `kb/` at any visibility. |

`personal/` is agent-readable; it is an export boundary rather than a vault, and the reasoning is in `personal/README.md`. Since both it and `visibility: self` are withheld from a team export, secrecy is not what separates them — retrieval is. `kb/` is indexed and routed to, while nothing points into `personal/`, so a work fact filed there is one the agent will never surface when it's needed.

`kb.py export DIR` emits a copy containing only `team` notes, regenerates every index from that filtered set, and drops table rows pointing at withheld files. It refuses to run if `check` fails, and verifies afterwards that no withheld filename appears anywhere in the output.

Two refusals guard the destination, because export replaces it wholesale and a mistyped path would otherwise be a silent recursive delete. It will not write to a directory containing this repo, and it will not overwrite a non-empty directory unless that directory carries the `.kb-export` marker file left by a previous run. An empty or nonexistent target is always fine.

Note that `team` is *not* the same as public. Everything in `kb/` describes your employer's internal systems, so an export is shareable with colleagues and with nobody else.

### Writing team-visible notes

Write them impersonally. `check` warns when a `team` note contains first-person prose or carries the `people` tag, because both mean it was written as a note to yourself and would read strangely — or reveal more than intended — to someone else.

When a note is mostly shareable but has a personal section, don't mark the whole file `self` — that withholds the useful part too. Move the personal section into the note where it belongs (unresolved questions and recorded mistakes each have their own home, both marked `self`), and the remainder stays shareable.

## Meetings are raw material

Meeting notes go in `kb/meetings/`, dated, `status: reported`, `visibility: self`. They preserve what was said. Domain notes hold what turned out to be true.

A conversation that was mostly career, growth, or interpersonal goes to `personal/meetings/` instead, with only the system facts extracted into `kb/`. Cite it in prose — `1:1, September 3 2026` — never by path: `check` fails on a `personal/` path inside a team-visible note, because the path would ship to teammates in an export while the file itself stays behind.

Keeping them separate is what stops the knowledge base becoming a transcript archive. A question like "who owns the CLI?" should land in an ownership note, not in a September 1st 1:1 — so when a meeting produces a durable fact, write it into the domain note that owns it and cite the meeting in `sources`. The meeting note remains as provenance for where the claim came from.

Full contract in `meetings/INDEX.md`.

## Lessons must declare where they apply

A lesson nobody reads at the right moment is wasted. Retrieval routes an agent to a *domain*, never to `kb/lessons/`, so a lesson only becomes reachable when it names the domains it concerns via `applies_to`. Each domain index then carries a generated "Lessons that apply here" table.

`scripts/kb.py check` fails on a lesson missing `applies_to`, because the alternative is a lesson that exists but never surfaces.

## Tooling

```sh
python3 scripts/kb.py check        # verify invariants; non-zero exit on failure
python3 scripts/kb.py sync         # regenerate the generated blocks
python3 scripts/kb.py export DIR   # write a team-shareable copy to DIR
```

`check` enforces: front matter present and complete, `domain` resolves, `status` valid, `verified` notes cite sources, `visibility` present and valid, `summary` not a placeholder, `updated` parses as a date, every domain registered in `kb/INDEX.md`, every lesson routable, no team-visible note citing a `personal/` path, no broken relative links, and every generated block current. It warns on oversized files, on team-visible notes that read personally, on a summary that only restates its title, and on two lessons that overlap enough to be competing.

Run `sync` after adding or editing a note. The pre-commit hook in `.githooks/` runs `check` automatically if you've enabled it — see `setup/README.md`.

## Writing style

Written for a reader who wasn't there. Spell out acronyms on first use in a file, even if they're obvious in context — files are read in isolation, so context from other files isn't available.

Prefer prose to fragments. Tables are for enumerable facts (paths, statuses, field definitions), not for explanations.

Cite specifics. `Routes.scala` is better than "the route table," and the full path from the repo root is better still. Line numbers rot; file paths mostly don't.

## What doesn't belong here

- Anything about compensation, performance, career plans, interpersonal friction, or personal life — that's `personal/`.
- Anything you wouldn't want a colleague to read. If it's work knowledge but not for sharing, it belongs in `kb/` with `visibility: self`, not in `personal/`.
- Scheduling and logistics: sprint tickets, TODOs, who's dialing in. Meeting *content* belongs in `meetings/`; meeting *arrangements* belong in a calendar.
- Anything already documented in the repo you work in. Link to its docs instead of copying it — a copy is a second source of truth that will silently go stale.
- Project specs. Long, multi-topic, iterated documents live in `projects/`, outside `kb/`, because they break every assumption the retrieval protocol relies on. What a project *concluded* belongs here; the document working it out does not. Specs still surface in the domain index they name, so nothing is lost by keeping them out. See `projects/README.md`.

## When to write

The knowledge base only compounds if things get captured as they surface, so notes are written during normal work rather than in a dedicated session. Agents are instructed to record without asking when the user states a durable fact, when a session establishes something from code, when a meeting gets relayed, when something recorded is contradicted, when the reasoning behind a note turns out to have been wrong, and when a `reported` claim gets confirmed. The full list is in the root `AGENTS.md`.

The corollary is that `check` matters more, not less: things written in passing are exactly the things written carelessly.

## Summaries carry more weight than they look like they do

The `summary` is not a courtesy line. It is copied verbatim into the generated index, and that index is what an agent reads when deciding which notes to open — so the summary *is* the note, until something opens the file.

That creates a failure worth naming. A placeholder summary (`unchanged`, `n/a`, `see above`, `TBD`) doesn't merely fail to help: it becomes the note's apparent content on every later pass, including for the agent deciding whether to rewrite it. `check` rejects a placeholder outright and warns when a summary only restates the title, since a row that repeats the heading adds nothing to routing.

Write it as the one sentence you would want to read when choosing between this note and four others.

## Dates, and why nothing nags you about them

Every note carries `updated`, and `check` validates it. Nothing warns when it gets old. `check` never fails on a moved aging marker — a day passing must not block a commit — but it prints a `note` line saying the marker moved, so the label cannot silently lag behind the last `sync`.

There was a six-month re-verification warning here and it was removed deliberately. Re-verifying a note is real work — re-reading the code, re-confirming the claim — and it is never the most valuable thing to do on the day a timer happens to fire. The realistic outcome isn't re-verification; it's bumping the date to silence the warning, which leaves the note exactly as stale while making it *look* freshly checked. A check that can only be satisfied by lying is worse than no check.

### The one exception: `half_life`

Correction-on-contradiction works because you bump into the subject. You read the code and it disagrees; someone mentions the ownership changed. That covers almost everything here, since almost everything here is about code you touch.

It does not cover facts you never re-encounter — who owns what, headcount, vendor terms, deprecation dates. Nothing ever disagrees with those out loud. They just quietly go wrong, which is the failure a lesson in this repo records: an ownership doc that stayed authoritative-looking long after it stopped being current.

For those notes only, set `half_life` to a number of days. The indexes then append `_(aging)_` past one half-life and `_(may be stale)_` past two, so the agent reading the index sees the note's age alongside its summary and can weigh it.

Three properties make this different from the six-month warning that was deleted:

- **It is a label, not a warning.** Nothing asks you to act, so there is nothing to clear — which removes the incentive to bump `updated` on a note you did not actually check. That incentive is what made the old check worse than no check.
- **It is opt-in and should stay rare.** The old one fired on every note, most of which self-correct through ordinary work, so it became noise. If more than about ten notes carry `half_life`, it has rotted back into the thing it replaced; drop it from the ones that don't need it.
- **It never deletes anything.** A note past two half-lives is unread, not disproven. Removal stays a human judgment about a note that is both wrong and uninstructive, and `status: stale` already exists for a wrong note whose history teaches something.

Set the horizon to how fast the subject really moves. Team ownership at this company is a twelve-to-eighteen-month question, not a six-month one.

**Notes get corrected when something contradicts them, not on a schedule.** Contradictions surface on their own during real work — you read the code and it disagrees, or someone tells you the ownership changed. That's the moment when correcting the note is cheap, because you already have the answer in front of you.

The date's job is to help you adjudicate that moment: a note verified in August against code you're reading today means today wins. It's context for a decision, not an alarm.

### When a note is contradicted

Update it to reflect the new state, set `updated`, and put whatever you checked in `sources`. Status follows where the contradiction came from — a primary source makes it `verified`, hearsay makes it `reported`.

Which side wins, in order:

1. **A primary source beats everything.** Code, a config, an owned doc. Dates don't enter into it: something checked against code today beats a claim from any date.
2. **Same provenance, newer wins.** Two `reported` claims from different people, or two readings of the same code — take the recent one.
3. **If you can't tell, don't pick.** Record both readings in the note, say plainly that they conflict, and set `status: reported`. A note stating that two sources disagree is genuinely useful; a note that silently guessed and looks settled is a trap, because nothing downstream can tell it was a guess.

Rule 3 is the one that gets skipped, and it's the one that matters. Resolving a contradiction by picking the more plausible side and writing it up as fact converts an open question into fabricated confidence.

**Only write a lesson if your reasoning was wrong, not if the world changed.** "The AoR doc was edited" teaches nothing and isn't a lesson. "I treated a doc's silence as evidence of absence" is. Recording world-changes as lessons erodes the bar for what a lesson is, and the directory stops being worth reading.

If you fix one claim in a note without re-checking the rest, say so in the note. The alternative is a fresh date implying more confidence than you actually earned.
