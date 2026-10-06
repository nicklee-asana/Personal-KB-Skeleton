# Agent Instructions

A personal knowledge base read by humans and agents. Answering a question should cost a few small files. When to read and capture, and the `personal/` rules, are in `setup/knowledge-base.md`; this file adds the repo-local rules.

## Hard rules

- **Never read the whole knowledge base.** No `cat kb/**`, no globbing and reading `kb/**/*.md`, no preemptive context loading.
- **Start at `kb/INDEX.md`.**
- **`personal/`** is outside retrieval: open it only for career or personal questions. Never copy it into `kb/` or cite a `personal/` path in a `visibility: team` note.
- **`projects/`** holds specs read whole, outside the three-file budget. Read a project's `README.md` in full when working on it; don't use specs to answer knowledge questions. Conventions: `projects/README.md`.

## Retrieval

Stop as soon as you can answer.

1. `kb/INDEX.md`.
2. The matching domain's `INDEX.md`: its notes, the lessons that apply, and project specs targeting it. Read the lessons table.
3. At most 3 leaf files, chosen from summaries, not guessed filenames.
4. If 3 weren't enough, say so and ask before opening more.

For a cross-domain question with no obvious domain, use `kb/tags.md`. When a summary is ambiguous, read just the front matter. If nothing matches, say the knowledge base doesn't cover it.

Find candidates with `rg` rather than opening files:

```sh
rg -l "tags:.*<topic>" kb/
rg "^summary:" kb/domains/<domain>/
```

## Capturing

Follow the capture list in `setup/knowledge-base.md`, plus:

- An open question recorded in a domain gets answered: move it to Resolved and update the domain note it concerns.
- A project ships or is abandoned: extract into `kb/` how it works, why the approach won, or why it was dropped.

Write first and mention it briefly. Before reorganizing files, say what you propose.

## Writing

Read `kb/CONVENTIONS.md` first; it holds the front-matter contract, status values, visibility, and conflict rules. The rules most often broken:

- One topic per file.
- Every note declares `visibility` (`team` or `self`, no default). Write `team` notes impersonally; open questions, recorded mistakes, and anything naming a colleague are `self`. Export ships only `team` notes.
- Never hand-edit inside `<!-- kb:generated:... -->`; change the note's `summary` and sync.
- Run `python3 scripts/kb.py sync` after any change and `check` before committing. Don't hand-verify what the script verifies.
- Never promote `reported` to `verified` without checking; cite the file, line, or command that confirmed it.

## Lessons

When a correction reveals wrong reasoning, write a durable rule to `kb/lessons/` (format in `kb/lessons/INDEX.md`). If it wouldn't change what someone does next time, don't write it. Every lesson needs `applies_to`, or no domain index will surface it.
