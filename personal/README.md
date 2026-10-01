# Personal

Career, growth, interpersonal, and side-project material. Never shared with the team, never exported.

## An export boundary, not a vault

Everything here is readable and writable by the agent. The line this directory draws is about what reaches a *teammate*, not about what an AI may see.

That is a deliberate reversal. A `beforeReadFile` hook with `failClosed: true` used to block agent reads of this directory, and it was removed once the cost became clear: the block prevented the agent from helping with the exact things kept here — thinking through a career decision, working on a side project — while the material it protected was awkward rather than dangerous. Access control and sharing control turned out to be separate problems, and only the sharing one was real.

The removal also settled a rule that had never been honest. The instruction said this directory was off-limits "unless the user names a file explicitly," but the hook only ever saw a file path, never the conversation, so there was no way for consent to reach it. The exception was unimplementable as written; saying so out loud was what prompted the change.

**Secrets still don't belong here.** Nothing in this repo is encrypted and it is a git repository. Credentials belong in a password manager.

## What belongs here

- Career and growth: plans, self-reviews, promotion material, feedback received
- Compensation and performance conversations
- Interpersonal material: assessments of colleagues, communication friction, how a conversation actually landed
- `meetings/` — 1:1s and conversations that were mostly career or interpersonal
- Personal side projects

## What looks like it belongs here but doesn't

Work knowledge you don't want to share is **not** personal material — it's `kb/` with `visibility: self`. That covers open questions, mistakes recorded as lessons, and notes about who owns what.

Both are withheld from a team export, so secrecy is no longer the difference. **Retrieval** is. `kb/` is indexed and routed to, so an agent answering a work question will find what's in it. This directory has no indexes and nothing points into it, so anything filed here is invisible during normal work.

That makes misfiling expensive in one direction only. A personal note in `kb/` is untidy. A work fact in `personal/` is a fact the agent will never surface at the moment you need it.

The test: "Sam owns the CLI" is work knowledge, so it goes in `kb/`, marked `self` because it names someone. "I find Sam hard to work with" belongs here.

When a 1:1 produces both, split it. The technical content goes to `kb/`; the personal content stays here.

## On sharing

`kb.py export` reads only `kb/` and never looks at this directory, so a team export cannot include it by accident.

One leak path is subtler and is now enforced: a `visibility: team` note that cites a `personal/` path in `sources` would ship that path to teammates even though the file itself stays behind — and a filename like `2026-01-15-comp-conversation-with-manager.md` says plenty on its own. `kb.py check` fails on any specific `personal/` path inside a team-visible note. Cite conversations in prose instead: `1:1, September 3 2026`.

If the *system* is ever published publicly, that must be a subtree split of `kb/` rather than deleting this directory and pushing — deletion leaves the content in git history. See the root `README.md`.
