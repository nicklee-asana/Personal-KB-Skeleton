# Blueprint

A self-contained specification for rebuilding this system from nothing. It describes the *structure* — layout, schema, triggers, tooling contract — and deliberately contains none of the accumulated knowledge itself.

Read this if you are recreating the setup in a fresh repository, porting it to a different job or subject area, or trying to understand why a piece of it is shaped the way it is before changing it.

For day-to-day use, read `AGENTS.md` and `kb/CONVENTIONS.md` instead. This file duplicates parts of both on purpose, so that it survives being copied out alone.

---

## 1. The problem

A personal knowledge base fails in four predictable ways. Every design decision below is aimed at one of them.

| Failure | Consequence |
|---|---|
| It grows until reading it is expensive | An agent burns its context loading notes to answer one question |
| Hearsay becomes indistinguishable from fact | You confidently repeat something nobody ever verified |
| Corrections are recorded but never resurface | The same mistake recurs; the note documenting it goes unread |
| Sharing requires a manual scrubbing pass | So it never gets shared, or something private leaks |

## 2. Invariants

These are the load-bearing rules. A rebuild that drops one of them will regress into one of the failures above.

1. **Answering a question costs at most three leaf files.** Achieved with a two-level index, not with search.
2. **Every note declares whether it was told or verified.** A `verified` note must cite sources.
3. **Every index table is generated from front matter.** A description must exist in exactly one place.
4. **Every correction names the domains it applies to.** Otherwise nobody encounters it when it matters.
5. **Sharing is a command, not a cleanup.** Visibility is metadata; the export enforces it.
6. **The invariants are machine-checked and wired to a pre-commit hook.** Conventions that rely on memory decay.
7. **A rule that must always apply is pushed, not stored.** Anything the agent has to know before it is asked lives in `setup/` and installs into every tool; `kb/` holds only what is worth looking up.

## 3. Layout

```
<repo>/
├── AGENTS.md              agent contract: retrieval protocol, capture triggers, hard rules
├── BLUEPRINT.md           this file
├── README.md              human orientation
├── kb/                    work knowledge, structured for retrieval
│   ├── INDEX.md           top-level router: domains + cross-cutting files
│   ├── CONVENTIONS.md     authoring contract
│   ├── glossary.md        terms and acronyms
│   ├── tags.md            generated: tag → notes
│   ├── domains/<name>/
│   │   ├── INDEX.md       generated file table + generated applicable-lessons table
│   │   └── <topic>.md     leaf notes, one topic each
│   ├── lessons/           durable corrections; surfaced via domain indexes
│   │   ├── INDEX.md       generated
│   │   └── YYYY-MM-DD-<slug>.md
│   └── meetings/          raw records; durable facts extracted into domains
│       ├── INDEX.md       generated
│       └── YYYY-MM-DD-<slug>.md
├── projects/              per-project specs; long documents, read whole
│   └── <project>/
├── personal/              career, interpersonal, side projects; readable, never exported
├── scripts/kb.py          validator, generator, exporter
├── tools/                 optional: runnable tooling, such as an API request collection
├── setup/                 machine config that lives outside the repo when installed
│   ├── <rule>.md          always-on rule bodies: the one source for each standing rule
│   ├── .generated/        git-ignored: bodies rendered with this machine's paths, plus .mdc files for Cursor
│   ├── install.sh         installs every body into Cursor, Claude Code, and Codex
│   └── hooks/             capture-check: detects a turn that recorded nothing
└── .githooks/pre-commit   runs the validator
```

Three areas sit outside the retrieval protocol on purpose: `meetings/` (raw material), `projects/` (read whole, not routed), and `personal/` (readable, but nothing routes to it).

`setup/` sits outside it for the opposite reason. Everything under `kb/` is pull-based and is read only when a question calls for it; the bodies in `setup/` are pushed into every session before any question is asked. That split is the system's central trade and §9 describes how it is installed.

## 4. Front matter schema

Every file under `kb/` except `INDEX.md` and `CONVENTIONS.md` carries YAML front matter.

| Field | Required | Rule |
|---|---|---|
| `title` | yes | Matches the H1 |
| `domain` | yes | A directory under `kb/domains/`, or `cross-cutting` |
| `tags` | yes | Lowercase, hyphenated, 2–5; aggregated into `tags.md` |
| `summary` | yes | One sentence. **The only place a description lives** — indexes are generated from it |
| `status` | yes | `verified` \| `reported` \| `stale` |
| `updated` | yes | ISO date of last substantive edit |
| `sources` | when `verified` | Paths, URLs, or people |
| `applies_to` | lessons only | Domains the lesson concerns, or `[all]` |
| `visibility` | yes, no default | `team` \| `self` — a permissive default meant sharing by omission |
| `size_exempt` | no | `true` waives the ~150-line guidance; state the reason in the body |

Status semantics matter more than they look: `reported` means someone said it, `verified` means it was checked against a primary source and says which, `stale` means known-outdated but kept because the history is instructive.

## 5. Visibility

Two independent questions, which is the part most likely to be collapsed by mistake:

- **Personal or work?** decides the *directory*. `personal/` vs `kb/`.
- **Shareable or not?** decides `visibility`, and applies only inside `kb/`.

| Tier | Contains |
|---|---|
| `visibility: team` | Facts about systems, written impersonally for a colleague to read |
| `visibility: self` | Open questions, recorded mistakes, meeting notes, anything naming a colleague |
| `personal/` | Career, compensation, interpersonal material, personal side projects |

`personal/` is agent-readable. Since it and `visibility: self` are both withheld from an export, secrecy isn't the distinction between them — retrieval is. `kb/` is indexed and routed to; nothing points into `personal/`, so a work fact filed there is one the agent will never surface. The enforced consequence: `check` fails on a specific `personal/` path inside a team-visible note, since the path would ship in an export while the file stays behind.

`team` means shareable with colleagues. It does **not** mean publishable — the content describes an employer's internal systems either way.

## 6. Capture triggers

The knowledge base only compounds if capture happens during normal work. Agents record without being asked when:

- The user states a durable fact about their work
- A session establishes something from code or docs that isn't recorded yet (`verified`, with sources)
- The user relays a meeting or 1:1 → a dated note in `kb/meetings/`, then durable facts extracted into domain notes
- Something recorded turns out to be wrong → correct the note *and* write a lesson
- A `reported` claim gets confirmed → promote to `verified` and add the source
- An open question gets answered → move it to Resolved and update the domain file

Not captured: scheduling and logistics; anything already documented upstream, which gets a link rather than a copy.

**Placement note that is easy to get wrong:** the triggers must live in the always-loaded rule, not only in `AGENTS.md`. A nested `AGENTS.md` loads only once an agent touches that directory, so triggers kept there alone will never fire during work in a *different* repository — which is exactly when new knowledge appears.

## 7. Generated blocks

Regions delimited by `<!-- kb:generated:NAME -->` and `<!-- kb:generated:end -->` are produced from front matter. Text outside them is hand-written and preserved.

| Block | Location | Content |
|---|---|---|
| `files` | domain `INDEX.md` | Each note in the domain with its `summary` |
| `lessons` | domain `INDEX.md` | Lessons whose `applies_to` names this domain |
| `projects` | domain `INDEX.md` | Specs in `projects/` whose `domain` matches |
| `lessons` | `kb/lessons/INDEX.md` | All lessons, newest first |
| `meetings` | `kb/meetings/INDEX.md` | All meetings, newest first |
| `tags` | `kb/tags.md` | Every tag mapped to its notes |

The `projects` block carries its own `###` heading *inside* the markers, so that a domain with no projects produces no section at all — and so the section disappears from an export, where specs aren't included. Any block whose content is conditional should be built this way.

## 8. Tooling contract

`scripts/kb.py` implements three subcommands and depends on nothing outside the standard library, so it keeps working without a virtualenv years later.

**`check`** — exits non-zero on any error.

Errors: missing or unparseable front matter; a required field absent; `domain` not resolving; invalid `status` or `visibility`; `verified` without `sources`; `updated` not an ISO date; a lesson without `applies_to`, or naming a domain that doesn't exist; a domain absent from `kb/INDEX.md`; a domain without `INDEX.md`; a broken relative link anywhere in the repo; a generated block that is out of date or missing.

Warnings: a note over ~150 lines without `size_exempt`; a `team` note containing first-person prose or tagged `people`; a meeting marked `team`; a project at `shipped` or `abandoned`, which prompts extracting what it taught into `kb/` (the check can't tell whether that happened, so the warning persists until the project is archived or the status changes).

Notices: a third tier below warnings, printed but never affecting the exit code. Currently one case — an aging marker whose rendered value has moved. A marker changes with the calendar rather than with an edit, so treating it as drift would fail a commit on a day nobody touched the repo, and a pre-commit hook that fails for no authored reason is one people learn to bypass. Saying nothing was the other wrong answer, because the label would then lag silently behind the last `sync`.

Deliberately **not** warned about: an old `updated` date. See §10.

**`sync`** — rewrites every generated block. Must be idempotent.

**`export DIR`** — writes a team-shareable copy. Refuses to run if `check` fails. Copies only `visibility: team` notes, regenerates all indexes from the filtered set, then removes references to what it withheld in two passes: a table row whose *every* link points at an excluded file is dropped whole, and any individual surviving link to a missing target is unwrapped to its plain text. The second pass exists because a row can carry several links — `tags.md` lists every note sharing a tag — so dropping the row loses the notes that did ship while keeping it leaks the ones that didn't. Unwrapping also covers hand-written prose links in note bodies, which no row-level rule can reach.

It then verifies that no withheld filename appears anywhere in the output and that no relative link dangles, and prints what it withheld. That self-check earns its keep: it has twice caught a *prose* mention of a withheld note's filename, which no amount of correct link handling would have found, most recently in a paragraph written minutes earlier.

## 9. Machine setup

Two tiers live outside the repo and are therefore tracked in `setup/` so they survive a new machine.

**The always-on rules.** Each is a plain Markdown body in `setup/`, and `setup/install.sh` derives all three installed forms from it:

| Agent | Mechanism | Installed where |
|---|---|---|
| Cursor | One project rule per body, `alwaysApply: true` | `<workspace-root>/.cursor/rules/<rule>.mdc` — the only mechanism documented to load in every session regardless of context; a nested `AGENTS.md` is conditional |
| Claude Code | User-level `CLAUDE.md` importing each body with `@<abs-path>` | `~/.claude/CLAUDE.md` |
| Codex | Global `AGENTS.md`, read before any repo-level one | `~/.codex/AGENTS.md`, generated by concatenating the bodies |

Bodies write `{{KB_ROOT}}` wherever they mean the repo, and `install.sh` renders that to the clone's absolute path, so the same text works from any working directory and any clone location. Edit the body, never a generated file, then re-run `install.sh`; `install.sh --check` reports drift and exits non-zero. Adding a rule is one file plus one line in the script's `RULES` array.

The set as of this writing: `knowledge-base.md` (retrieval protocol and capture triggers), `response-preferences.md` (how output is written), `engineering-principles.md` (how work is done and verified).

**The hooks.** `setup/hooks/hooks.json` merges into `~/.cursor/hooks.json` and wires `capture-check.py` to `afterFileEdit`, `postToolUse`, and `stop`, all fail-open. `kb-autosync.py` sits alongside it: it runs `kb.py sync` at most twice a day so aging markers do not lag behind the calendar, and `install.sh` also registers it as a Claude Code `SessionStart` hook. The general shape is that anything the design needs run on a cadence gets attached to an event that already happens, never to the operator's memory. The `failClosed` `beforeReadFile` and `beforeShellExecution` pair that once guarded `personal/` was removed; see §10. Pre-commit is enabled with `git config core.hooksPath .githooks`.

Rules take effect in a new chat. Hooks require restarting the editor. Running `install.sh` from inside an agent's own sandbox generally fails, because the three install targets sit outside the writable set; run it from a terminal.

## 10. Decisions, and what was rejected

Recorded so a rebuild doesn't cheerfully undo them.

**Indexes are generated, not written.** Descriptions previously lived in both the front-matter `summary` and the index row, in different wordings. They drifted, and a drifting index degrades routing while continuing to look correct.

**Lessons declare `applies_to`.** Retrieval routes to domains and never visits `lessons/`, so lessons without back-links were written and then never read again. Validation fails on a lesson that omits it, because an unreachable lesson is worse than none — it costs the effort of writing and returns nothing.

**Meetings are separated from domain notes.** Otherwise "who owns X?" starts resolving to a transcript from some Tuesday instead of the note that owns the answer. Meetings are provenance; domain notes are the product.

**Projects live outside `kb/`.** Specs are long, multi-topic, read whole, and churn during design — every one of those fights the retrieval protocol's assumptions. Keeping them out avoids weakening the rules that make `kb/` cheap to read.

**Projects are surfaced back into domain indexes anyway.** Living outside `kb/` initially meant a spec was findable only by someone who already knew it existed — the same reachability failure that lessons had. Each project declares a `domain`, and that domain's index carries a generated table of its specs. The general rule: anything kept outside the retrieval path still needs a link *into* it from somewhere on the path.

**Blocking agent reads of `personal/` was built, then deliberately reverted.** `.cursorignore` was rejected first and correctly: Cursor's [own documentation](https://cursor.com/docs/reference/ignore-file) states that "the terminal and MCP server tools used by Agent cannot block access to code governed by `.cursorignore`," and its [hardening guide](https://cursor.com/docs/enterprise/security-hardening) classifies both rules and ignore files as best-effort guardrails. So `setup/hooks/` carried a `failClosed` `beforeReadFile` hook, the documented deterministic control, and it worked.

It was removed anyway, because it solved a problem that wasn't there. `personal/` needed an *export* boundary, not an *access* boundary — and blocking reads mostly prevented the agent helping with the career notes and side projects the directory exists to hold. The generalizable form: before building a control, check whether the thing you're protecting needs protecting from *this particular reader*. Two failure modes the attempt exposed are recorded in `setup/README.md`, including that a `failClosed` hook whose script lives in the repo it guards cannot be safely deleted before it is unwired.

**Standing rules were kept out of `kb/` and given their own always-on tier.** A preference about how to write a reply, or a rule about what counts as verified, is useless if it is only read when someone asks for it — and `kb/` is deliberately built so that nothing is read unless a question routes there. Response preferences sat in a Cursor rule for weeks and consequently applied in Cursor and nowhere else. The fix was to make `setup/` the single source for anything that must be pushed rather than pulled, and to derive every agent's copy from it, so a rule is written once and cannot be true in one tool and absent in another.

The same reasoning promoted a cluster of `kb/lessons/` entries. Five of them were the same failure — a verification verdict read as covering content it never touched — and a lesson that recurs five times is no longer a note to look up, it is a rule that must be present before the work starts. The general form: **a correction that keeps recurring has outgrown the pull-based tier.** Leave the full reasoning in the leaf note and move the trigger into the always-on rule, per §10's own principle that structure beats prose.

**The export verifies itself rather than trusting the filter.** It re-scans its own output for withheld filenames. This caught a real leak on its first run: prose in `CONVENTIONS.md` named a withheld file, which no amount of correct filtering would have caught.

**Warnings, not errors, for the heuristics.** A first-person line may be a quotation; a project may be legitimately unmined for a week. Errors would train you to bypass the hook, which costs you the checks that are real.

**A timed re-verification warning was built and then removed.** It fired when a `verified` note passed 180 days. The problem is that re-verifying is genuine work and is never the most valuable thing to do on the day a timer happens to fire, so the realistic response is bumping the date to clear the warning — which leaves the note equally stale while making it look freshly checked. A check that can only be satisfied by lying actively corrupts the signal it was meant to protect.

Notes are corrected when something contradicts them instead. Contradictions arrive on their own during real work, at the moment when fixing the note is cheapest because the answer is already in hand. Dates are still recorded and validated: their job is to adjudicate a contradiction when one appears — a note verified in August loses to code you are reading today — not to schedule a review.

**A narrow decay was added afterwards, as a label rather than a check.** The timer above was the wrong instrument, but the gap it aimed at is real: correction-on-contradiction only fires when you re-encounter the subject, and some facts — ownership, headcount, vendor terms — are never re-encountered during work. So an optional `half_life` on individual notes marks them `_(aging)_` past one half-life and `_(may be stale)_` past two, in the generated index rows, which is the only surface retrieval reads.

It avoids what killed the timer by asking for nothing. There is no warning to clear, so there is no incentive to bump `updated` on a note nobody checked. It is opt-in, it is meant to stay under about ten notes, and it never deletes: a note past two half-lives is unread, not disproven. `check` also ignores drift in the marker itself, since a pre-commit hook that fails because the calendar advanced is one people learn to bypass.

The general shape, which is the part worth keeping: **when a signal cannot be satisfied honestly, weaken it from a demand into an observation.** A demand you can clear by editing a date corrupts the data. A label alongside the data leaves the reader to judge, and costs nothing when it is wrong.

The corollary, worth enforcing socially since no script can: **a changed fact is not a lesson.** Only a flawed inference is. Recording world-changes in `lessons/` erodes the bar for what a lesson is until the directory isn't worth reading.

If a mechanical staleness signal is ever wanted, the one that fits this model is hashing each cited source at verification time and reporting when a cited file *actually changes*. That detects the real event rather than nagging on a calendar.

## 11. Checked against prior art (Kiro Crew)

This system was designed from its own constraints and only afterwards compared against [Kiro Crew](https://github.com/kirodotdev/KiroCrew) (AWS, Apache 2.0, orchestration open but the `kiro-cli` agent runtime proprietary). Recorded because the comparison settles several questions a rebuild would otherwise reopen.

**Independent convergence on the central split.** Crew's [knowledge module](https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md) separates a memory layer — "small, distilled, always-on," "injected into every prompt," and "lossy by design (it dedups, decays, and paraphrases)" — from a knowledge library holding the "durable, **verbatim, cited** detail that memory can only approximate," reached on demand through a search tool. That is exactly the always-applied rule versus `kb/` division here. Their lessons tier carries a per-repository `repo_scope` gate, which is `applies_to` under another name. Two independent designs landing on the same two structures is the strongest evidence available that the structures are load-bearing.

**Their knowledge retrieval also refuses to treat age as a decay weight**, breaking ties by `updated_at` as "a secondary sort key, **not** a decay weight." Their *episodic* memory does decay, at 0.03/day. So they draw the same line §10 arrives at: age adjudicates, it doesn't penalise — and decay belongs to conversation history, not to cited knowledge. If pruning is ever added here, `kb/meetings/` is where it belongs, not domain notes.

**The conflict ladder was borrowed.** Crew resolves competing writes by precedence: `user_explicit` wins, only another `user_explicit` may overwrite it, otherwise higher confidence wins and near-ties go to the newer write. This system had defined how status is *assigned* after a contradiction but never which side *wins*; `kb/CONVENTIONS.md` now states it. The one place this design deliberately diverges: Crew's retrieval must "surface the conflict, not silently pick one" because it cannot edit ingested sources, whereas notes here are owned and edited in place, with git holding the history of what was previously believed. That is only safe while an *unresolved* contradiction is recorded as unresolved, which is why that rule is written down rather than left to judgement.

**Deliberately not adopted.** Crew stores memory in SQLite plus FAISS vectors with hybrid FTS5/graph/vector retrieval, and consolidates automatically via an LLM (preferences at 30 messages, history and lessons at 3 hours idle). Both are better than what is here in isolation, and both were rejected for this corpus: knowledge that can't be read, diffed, or reviewed by its owner is unusable for career-relevant facts, and an LLM paraphrase pass is an unacceptable corruption risk for the specific claims — who owns what, what was decided — that this base exists to hold. Crew also has no notion of team-visibility filtering; its `memory export` is backup and restore, not sharing.

**Their automated consolidation was partly replicated, on purpose only partly.** Crew extracts knowledge with a scheduled LLM pass, which is deterministic in a way that standing instructions are not. `setup/hooks/capture-check.py` takes the detection half of that idea and leaves the extraction half alone: it counts what a turn touched, and when a turn did work without writing to `kb/`, the `stop` hook returns a `followup_message` that Cursor submits as the next user message. Detection is exact; the judgement of what's worth recording stays with the model, because the alternative is an LLM paraphrasing facts into notes unread by their owner — the specific failure this design rejects elsewhere in this section. The follow-up therefore has to say that "nothing to record" is an acceptable answer, or it becomes pressure to fabricate. Note also that `preCompact` exists because long sessions get summarized, so an end-of-turn pass may be reasoning over a summary: incremental capture still beats deferred capture, and this hook is a backstop rather than the mechanism.

**Two defects were found by reading their source, not by reasoning about ours.** Crew's rule that a *present but unusable* scope is dropped from every reader rather than admitted globally — because admitting it is the one direction the gate must never fail — pointed straight at `visibility`, which was optional and defaulted to `team`. Eleven of fifteen notes were in the shared export because nobody had typed anything, and the export's own leak-check could not see it: that check re-scans output for the filenames of *withheld* notes, and a note missing the field was never withheld. `visibility` is now required, with no default. Separately, their habit of validating a replacement before deleting what it supersedes exposed `export` calling `shutil.rmtree` on any path handed to it, so a mistyped destination was a silent recursive delete; it now refuses any directory containing this repo, and any non-empty directory without the marker file a previous export left behind.

The general lesson, worth more than either fix: **an optional field with a permissive default is a decision nobody made.** Where the failure is unrecoverable, require the field.

**One risk Crew addresses that this system does not.** Crew screens every memory write for prompt injection, on the reasoning that "a poisoned turn could persist steering instructions that get re-injected into future contexts." This design has that shape: agents read external docs, capture triggers tell them to record what they learned, and the rule re-injects `kb/` every session. Instruction-shaped text laundered into a note becomes permanent. Unmitigated here by choice; the exposure is real but the only author is the owner.
