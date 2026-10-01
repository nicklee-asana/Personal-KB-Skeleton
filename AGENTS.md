# Agent Instructions

This repo is a personal knowledge base. It is read by both humans and agents. These rules exist so that answering a question costs a few small files, not the whole repo.

## Hard rules

**`personal/` is an export boundary, not a vault.** It holds career and growth material, interpersonal and communication notes, and personal side projects. Read and write it freely — it was agent-blocked by a hook until that turned out to prevent the agent from helping with the very things kept there. Two prohibitions remain: never cite a `personal/` path in the `sources` of a `visibility: team` note, because that path ships to teammates in an export, and never copy its content into `kb/`.

It sits outside the retrieval protocol — no indexes, nothing routes to it — so open it when the question is about career or personal matters, not as a step in answering a work question.

**Never read the whole knowledge base.** Do not run `cat kb/**`, do not glob `kb/**/*.md` and read the results, do not "load context" preemptively. The index files exist so you don't have to.

**Start at `kb/INDEX.md`. Always.** It is small by design and tells you where to go next.

**`projects/` is not part of the knowledge base.** It holds long specs that are read whole, not routed to, and the three-file budget doesn't apply there. Read a project's `README.md` in full when working on that project. Don't pull specs in while answering a knowledge question — the settled version of anything a spec decided belongs in `kb/`. Conventions are in `projects/README.md`.

## Retrieval protocol

Follow this in order. Stop as soon as you can answer.

1. Read `kb/INDEX.md` — the top-level router. One line per domain.
2. Read the `INDEX.md` of the one domain that matches. It lists every file in that domain with a one-line summary, the lessons that apply to it, and any project specs targeting it.
3. Open **at most 3 leaf files**. Pick them from the summaries, not by guessing at filenames.
4. If 3 files weren't enough, say so and ask before opening more.

When a question cuts across domains and step 1 gives no single obvious match, use `kb/tags.md` instead — it maps every tag to the notes carrying it.

Every leaf file starts with YAML front matter containing a `summary` field. When an index summary is ambiguous, read just the front matter before committing to the whole file.

If nothing matches, say the knowledge base doesn't cover it. Do not go spelunking through directories hoping to find something.

## Search before you read

`rg` over front matter is cheap; reading files is not. To find candidates:

```sh
rg -l "tags:.*<topic>" kb/
rg "^summary:" kb/domains/<domain>/
```

Prefer this over opening files to see what's in them.

## When to write — without being asked

This knowledge base is the user's notes for everything work-related. It only compounds if things get captured as they surface, so **don't wait to be told**. Record when any of these happen:

- **The user states a durable fact about their work** — how a system behaves, who owns what, why a decision was made, what a team is planning. Write it to the relevant domain note.
- **A session establishes something by reading code or docs** that isn't already written down. Capture it with `status: verified` and cite what you read.
- **The user relays a meeting, 1:1, or conversation.** Write a meeting note in `kb/meetings/`, then extract any durable facts into the domain notes that own them.
- **Something recorded is contradicted** by code you're reading or something you're told. Update the note to the new state, set `updated`, and record what you checked in `sources`. This is the primary way notes stay current — there is no review schedule, by design. A primary source wins over hearsay regardless of dates; between equals, the newer claim wins; and if you genuinely can't tell which is true, record *both* and say they conflict rather than picking the more plausible one. See `kb/CONVENTIONS.md`.
- **The reasoning behind a note was wrong**, as opposed to the world having changed. Correct the note *and* write a lesson. A changed fact is not a lesson; a flawed inference is.
- **A `reported` claim gets confirmed.** Promote it to `verified` and add the source.
- **An open question recorded in a domain gets answered.** Move it to Resolved and update the domain file it concerns.
- **A project ships or is abandoned.** Extract what it taught into `kb/` — how the thing works, why the approach won, or why it was dropped. A dead end nobody recorded gets rediscovered the hard way.

Two things not to capture: anything already documented in the repo you work in — link to it instead of copying, since the copy will rot — and scheduling or logistics, which is a calendar's job.

Write first and mention it briefly, rather than asking permission for each note. If the knowledge is substantial enough to reorganize files, say what you're proposing first.

## Writing to the knowledge base

Read `kb/CONVENTIONS.md` before creating or restructuring any file. It defines the front matter contract, file naming, and where things belong.

Four rules that matter most:

- **One topic per file.** A file that covers three topics forces three times the tokens to answer a question about one of them.
- **Every note declares `visibility`, and there is no default.** Write `team` notes impersonally. Open questions, recorded mistakes, and anything naming a colleague get `self` instead. `check` fails on a missing field rather than assuming, because a permissive default means sharing happens by omission. `kb.py export` ships only the team notes, so a misfiled note is a note shared with the user's teammates by accident.
- **Never hand-edit inside `<!-- kb:generated:... -->` markers.** Index tables are generated from front matter. Change the `summary` in the note itself, then run sync.
- **Run `python3 scripts/kb.py sync` after any change, and `check` before committing.** `check` fails on missing front matter, unroutable lessons, broken links, and stale generated blocks. Don't hand-verify what the script verifies.

## Lessons

When the user corrects a factual error, or when something in the knowledge base turns out to be wrong, write it to `kb/lessons/`. Format and rationale are in `kb/lessons/INDEX.md`.

A lesson is not a diary entry. It is a durable rule that should change behavior next time. If it wouldn't change what someone does, don't write it.

Every lesson needs `applies_to` naming the domains it concerns. Retrieval routes to domains, never to `kb/lessons/`, so a lesson without it will never be read by anyone who needs it. The domain indexes carry a generated table of the lessons that apply to them — read it as part of step 2 of the retrieval protocol above.

## Verification standard

This knowledge base distinguishes what was *told* from what was *verified*. The `status` field in front matter is not decorative:

- `verified` — checked against code, docs, or a primary source, with the source cited in the file
- `reported` — someone said it; not yet confirmed
- `stale` — known to be outdated, kept for history

Never promote `reported` to `verified` without actually checking. When you do verify something, cite the specific file, line, or command that confirmed it.
