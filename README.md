# Personal KB Skeleton

A personal work knowledge base built to be read and written by coding agents — Cursor, Claude Code, and Codex — as well as by you. This is the empty structure: the conventions, the agent rules, and the tooling that keeps it consistent, with one example note to show the shape.

The idea in one line: your agent records the traps and facts you learn during normal work, and reads them back before it repeats a mistake — at a cost of about three small files per question.

## Quick start

```sh
# 1. Clone it and give it a private remote of your own. Your notes will describe internal
#    systems, so never push a filled-in copy anywhere public.
git clone https://github.com/nicklee-asana/Personal-KB-Skeleton.git ~/sandbox/Personal-Repo
cd ~/sandbox/Personal-Repo
git remote remove origin        # then add your own private remote

# 2. Enable the pre-commit validator.
git config core.hooksPath .githooks

# 3. Install the always-on agent rules into Cursor, Claude Code, and Codex.
#    Run from a normal terminal, not from inside an agent's sandbox.
bash setup/install.sh

# 4. Confirm everything holds together.
python3 scripts/kb.py check
```

Clone it anywhere; `install.sh` renders the rules with whatever path you chose. For Cursor, it writes rules into `<parent of the repo>/.cursor/rules/`, which assumes the repo sits one level below the folder you open as your Cursor workspace (here, `~/sandbox`). Set `CURSOR_RULES_DIR` if yours differs.

Optional: merge `setup/.generated/hooks.json` into `~/.cursor/hooks.json` for the capture check, which nudges the agent when a turn did real work and recorded nothing. Details in `setup/README.md`.

Start a new chat afterwards. Rules take effect in a new chat; hooks need an editor restart.

## Make it yours

1. **Rename the example domain.** `kb/domains/example-team/` → your team or main system. Update the row in `kb/INDEX.md` and `domain:` in the notes, then run `python3 scripts/kb.py sync`.
2. **Rewrite `setup/response-preferences.md`.** It is one engineer's preferences for how agents should talk to him, kept as a worked example. Edit it to match yours.
3. **Point the knowledge-base rule at your repo.** `setup/knowledge-base.md` has a commented-out line that makes the agent read your repo's notes before its first git, build, or test command there. Once you have a few notes about your repo's traps, that line is the most valuable one in the system.
4. **Delete the example note and lesson** once you have real ones.

Re-run `bash setup/install.sh` after editing anything in `setup/`.

## Using it

You mostly don't drive it by hand. Work as normal and the agent will:

- record a note when you state a durable fact, or when a session uncovers something that was hard to find
- read the relevant domain index before answering a question it plausibly covers
- write a lesson when a recorded belief turns out to have been wrong for a reason that generalizes

You can also ask directly: "what do my notes say about X", "record that Y owns Z", "I just had a 1:1 with A, here's what we covered".

## Layout

```
kb/                          Work knowledge, structured for retrieval
├── INDEX.md                 top-level router: one row per domain
├── CONVENTIONS.md           how to write and file a note; read before adding one
├── glossary.md, tags.md     terms, and a generated tag → notes index for cross-domain questions
├── domains/<name>/          one directory per team or system
│   ├── INDEX.md             generated table of the domain's notes, lessons, and project specs
│   └── <topic>.md           leaf notes, one topic each, under ~150 lines
├── lessons/                 corrections to reasoning, as YYYY-MM-DD-<slug>.md
└── meetings/                dated raw records of 1:1s and discussions
projects/<name>/README.md    long specs, read whole; start from projects/_template/
personal/                    career, growth, interpersonal, side projects; never exported
setup/                       always-on agent rule bodies, hooks, and install.sh
scripts/kb.py                validator, index generator, and team exporter
.githooks/pre-commit         runs `kb.py check` on every commit
AGENTS.md                    agent contract: retrieval protocol, capture triggers, hard rules
BLUEPRINT.md                 why the system is shaped this way, and what was rejected
```

**`kb/`** is the only part an agent searches. It answers a question in three hops: `kb/INDEX.md` picks the domain, the domain's `INDEX.md` lists every note with its one-line `summary`, and the agent opens at most three notes. The index tables are generated from each note's front matter, so you edit the note and run `kb.py sync`, never the table. Every note declares `status` (`verified`, `reported`, or `stale`) and `visibility` (`team` or `self`).

- **`domains/`** holds the settled facts, one directory per team or system. A good first domain is your main repo's workflow traps: how commits, PRs, and CI actually behave, beyond what its docs say.
- **`lessons/`** holds rules learned from being wrong, such as "a green targeted test is not a green build". Each lesson names the domains it `applies_to`, and those domain indexes list it, so it surfaces when the work is relevant.
- **`meetings/`** is provenance. A durable fact from a meeting gets written into the domain note that owns it; the meeting note stays as the record of who said it.

**`projects/`** sits outside `kb/` because specs are long, multi-topic, and change constantly, which breaks the one-topic, three-file rules. Each spec names a `domain`, and that domain's index links to it. When a project ships or is abandoned, what it taught moves into `kb/`.

**`personal/`** is readable by the agent but has no index and is never included in `kb.py export`, so it's where career and interpersonal material goes. Work facts you don't want to share belong in `kb/` with `visibility: self` instead, because nothing routes into `personal/`.

**`setup/`** is the part that loads before you ask anything. Its three rule bodies are installed into Cursor, Claude Code, and Codex by `install.sh`, which is why the agent knows to check the KB and capture notes without being told.

Read `BLUEPRINT.md` before changing the structure; most of the rules exist because the obvious alternative failed.

## Design goals

**Answering a question should cost three small files, not the whole repo.** Every domain has an index; every note has a one-line summary in front matter. An agent reads `kb/INDEX.md`, then a domain index, then one or two leaf files.

**Told and verified are different things.** Every note carries a `status` of `reported`, `verified`, or `stale`, so something you heard doesn't quietly become something you treat as fact.

**Being wrong should compound into being right.** Corrections go to `kb/lessons/` as durable rules, and each lesson declares which domains it applies to so those domain indexes surface it.

**The structure enforces itself.** `scripts/kb.py check` fails on missing front matter, unroutable lessons, broken links, and stale indexes, and runs as a pre-commit hook.

**Sharing with your team is a command, not a cleanup pass.** Every note declares `visibility: team` or `self`. `python3 scripts/kb.py export DIR` writes a copy with only the team notes, indexes rebuilt to match, and verifies that no withheld file is mentioned anywhere in the result.

## Day-to-day commands

```sh
python3 scripts/kb.py sync          # regenerate index tables from front matter
python3 scripts/kb.py check         # verify everything holds together
python3 scripts/kb.py export DIR    # write a team-shareable copy to DIR
bash setup/install.sh --check       # report drift in the installed agent rules
```

Index tables live inside `<!-- kb:generated:... -->` markers and are built from each note's front-matter `summary`. Edit the note, not the index.

Requires only Python 3 and bash; `kb.py` uses the standard library alone.

## Credit

`setup/engineering-principles.md` is adapted from the principle set in [cursor/plugins `pstack`](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan.
