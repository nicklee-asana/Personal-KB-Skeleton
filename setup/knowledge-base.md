# Personal Knowledge Base

`{{KB_ROOT}}/kb/` holds verified notes on the user's work: the systems they work on, who owns what, and the traps that cost them time.

## When to read it

- When the user asks what they know or have recorded, mentions "my notes" or "the KB", or asks a question it plausibly answers.
<!-- Optional, and the highest-value line in this file once you have notes about your main repo.
     Uncomment and point it at the domain that records your repo's traps:
- **Before the first git, build, or test command** in `~/path/to/your/repo`: read `{{KB_ROOT}}/kb/domains/<your-repo-domain>/INDEX.md` and open the notes that match the task.
-->
- Not for unrelated coding tasks. Capturing (below) applies in every session.

**Read budget:** `kb/INDEX.md`, then one domain `INDEX.md`, then at most 3 leaf files chosen by their `summary`. Never glob or bulk-read `kb/**`.

## When to capture (without asking)

- The user states a durable work fact: behavior, ownership, or the reason for a decision.
- A session finds something **costly to find**: a trap that burned time, behavior that contradicts the docs or the obvious reading, or a failure the error message didn't explain. Use `status: verified` and cite the source. Skip anything grep, the repo's docs, or the error message would surface in minutes.
- A meeting or 1:1: write a dated note in `kb/meetings/` and extract the durable facts. If it was mostly career or interpersonal, write it to `personal/meetings/` and extract only the system facts.
- A recorded fact is contradicted: update the note and set `updated`. A primary source beats hearsay. If you can't tell which is right, record both as conflicting.
- A note's reasoning was wrong, not just its fact: fix the note and write a lesson.
- A `reported` claim is confirmed: promote it to `verified` with the source.

Link to the repo's own docs rather than copying from them. Don't record scheduling. Tell the user what you recorded in one sentence.

## Write it succinctly

Everything in `kb/` and `setup/` is agent context, and every extra word costs tokens on every load.

- State the rule, fact, or trap and its fix. Leave out origin stories, attributions, dated quotes, and motivation that doesn't change what the reader does.
- Include a "why" only when it decides an edge case the rule alone doesn't.
- Keep a note to a handful of sentences. Past about 30 lines it is probably explaining code that should just be read.

## Writing mechanics

- Read `{{KB_ROOT}}/kb/CONVENTIONS.md` before creating or restructuring files. Every note has YAML front matter and covers one topic.
- Never hand-edit inside `<!-- kb:generated:... -->`. After any change, run `python3 {{KB_ROOT}}/scripts/kb.py sync`, then `check`.
- Corrections go to `kb/lessons/` with `applies_to`. The full contract is in `{{KB_ROOT}}/AGENTS.md`.

## Outside `kb/`

- `projects/<project>/`: long specs. Read the spec whole when working on that project; the read budget doesn't apply. Don't use specs to answer knowledge questions.
- `personal/`: career, growth, and interpersonal notes, and side projects. Read and write it freely, but nothing routes there. Never copy its content into `kb/`, and never cite a `personal/` path in a `visibility: team` note. The split is by kind: "Sam owns the CLI" goes in `kb/` (`visibility: self`); "I find Sam hard to work with" goes in `personal/`.
