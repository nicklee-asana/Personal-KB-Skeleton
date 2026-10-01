# Personal Knowledge Base

A personal work knowledge base lives at `{{KB_ROOT}}/kb/`. It holds verified notes about the user's work: the systems they work on, who owns what, and the traps that cost them time.

## When to use it

Consult it when the user asks what they know or have recorded about a work topic, refers to "my notes" or "the KB", asks to record or update something they've learned, or asks a question the knowledge base plausibly already answers.

<!-- Optional, and the highest-value line in this file once you have notes about your main repo.
     Uncomment and point it at the domain that records your repo's traps:

Also consult it, unprompted, **before the first git, build, or test command in any task inside `~/path/to/your/repo`**: read `{{KB_ROOT}}/kb/domains/<your-repo-domain>/INDEX.md` and open the notes matching what you are about to do. It records the traps the repo's own docs leave out.
-->

Do **not** read it for unrelated coding tasks unless the user's question is about their own recorded knowledge. Capturing, below, still applies in every session.

## When to capture

These are the user's notes for everything work-related, so record as things surface rather than waiting to be asked. Write without asking permission when:

- The user states a durable fact about their work — how something behaves, who owns what, why a decision was made
- A session establishes something from code or docs that isn't recorded yet **and was hard to find** (`status: verified`, cite the source). The bar is cost, not novelty. Record a trap that burned real time, a behavior that contradicts the docs or the obvious reading, or a failure whose cause wasn't in the error message. Don't record anything a future session could rediscover in a few minutes by grepping the code, reading the repo's own docs, or reading the error: code maps, how a function works, which file holds what, one bug's analysis. A bulky KB costs every lookup.
- The user relays a meeting or 1:1 → a dated note in `{{KB_ROOT}}/kb/meetings/`, then extract durable facts into the domain notes. If it was mostly career, growth, or interpersonal, the note goes to `{{KB_ROOT}}/personal/meetings/` instead and only the system facts are extracted into `kb/`
- Something recorded is contradicted by code or by what the user is told → update the note to the new state and set `updated`. This is how notes stay current; there's no review schedule. Primary sources beat hearsay regardless of date; if you can't tell which is true, record both and say they conflict rather than picking
- The *reasoning* behind a note was wrong, not just the fact → fix the note *and* write a lesson. A changed fact isn't a lesson
- A `reported` claim gets confirmed → promote to `verified` with the source

Don't copy anything already documented in the repo — link to it. Don't record scheduling.

Mention what you recorded in a sentence; don't narrate the whole note back.

## Read budget

The knowledge base is built for cheap retrieval. Follow this and stop as soon as you can answer:

1. Read `{{KB_ROOT}}/kb/INDEX.md` — the top-level router.
2. Read the one matching domain's `INDEX.md`.
3. Open **at most 3 leaf files**, chosen from the `summary` line in each file's front matter.

Never glob or bulk-read `{{KB_ROOT}}/kb/**`. The indexes exist so that isn't necessary.

## Project specs

Long-form specs live in `{{KB_ROOT}}/projects/<project>/`, outside the knowledge base. Read a spec whole when working on that project; the three-file budget doesn't apply. Don't consult specs to answer a knowledge question — what a project concluded belongs in `kb/`.

## `personal/`

`{{KB_ROOT}}/personal/` holds career and growth material, interpersonal and communication notes, and personal side projects. Read and write it freely — it is an export boundary, not a vault.

It sits outside the retrieval protocol, with no indexes and nothing routing to it, so open it when the question is about career or personal matters rather than as a step in answering a work question. Two rules do bind: never cite a `personal/` path in the `sources` of a `visibility: team` note, since that path ships to teammates in an export, and never copy its content into `kb/`.

The split is by *kind*, not by sensitivity. "Sam owns the CLI" is work knowledge and belongs in `kb/` with `visibility: self`; "I find Sam hard to work with" belongs in `personal/`.

## Writing to it

Before creating or restructuring files, read `{{KB_ROOT}}/kb/CONVENTIONS.md`. Every note needs YAML front matter, one topic per file.

Index tables are generated — never hand-edit inside `<!-- kb:generated:... -->` markers. After any change run `python3 {{KB_ROOT}}/scripts/kb.py sync`, then `check` before committing.

Corrections go to `{{KB_ROOT}}/kb/lessons/` as durable rules, each declaring `applies_to`. Full contract is in `{{KB_ROOT}}/AGENTS.md`.
