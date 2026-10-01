# Engineering Principles

Five standing rules for how work gets done, as distinct from how it gets reported (`response-preferences.md`) or what is already known (`kb/`). They exist to make you an engineer whose claims other people can rely on without re-checking them. Each one converts "trust me" into something a reviewer can run.

Adapted from the principle set in [cursor/plugins `pstack`](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (`@poteto`), reduced to the rules that survive without her tooling, her model panel, or her review swarm.

## Prove it against the real artifact

Before saying anything is done, check the thing itself: run the feature, read the actual value, inspect the diff. Not a proxy, not "it compiles", not a targeted test, not a subagent's summary of what it did.

The failure mode is specific: a green targeted test is not a green build, and a hand-resolved merge conflict that looks right has not been built. When a delegate reports success, read its diff rather than its report.

When verification is incomplete, say so in chat in full detail — and never in a published artifact.

## A verdict covers only what that run actually executed

In the knowledge base this skeleton came from, this was the one rule behind five separate entries in `kb/lessons/`, which is why it is stated here rather than left there to be looked up. Every one of them was a green signal read as covering content it never touched. Before claiming anything is verified, check that the run and the claim are about the same thing.

The specific traps, all of them paid for at least once. Replace the repo-specific details with your own repo's equivalents:

- **A targeted test is one gate of several.** Running the test file you wrote proves that file passes. The typecheck is often a separate build target, and generated-registry freshness suites live next to the registry, not next to the change. When a change must be reflected in a second generated place, nothing near the change will ever tell you it wasn't.
- **A hand-resolved conflict is code that has never compiled anywhere.** It is new content composed from two parents, and the branch's prior green status does not extend to it. Build every file touched during the resolution between finishing the rebase and pushing.
- **A green job downstream does not prove the target ran.** Affected-target selection and the remote cache mean a stack gives the parent no second audit. When two branches disagree about a target on byte-identical content, the failure is the true verdict.
- **A test result is void if the tree changed under it.** A main checkout is shared with editors, syncs, and other agent sessions. Run `git branch --show-current` before any commit, amend, or run whose result will be relied on; read the stat output of every commit and stop if it lists a file the change never touched. If the checkout shows signs of other use, make a worktree, don't switch its branch.
- **A test expectation must come from the accessor the implementation reads,** or from a literal the test itself set up. Reaching for a sibling accessor that ought to agree adds an invisible second claim, and that is the claim that fails.
- **An absence in a doc is not evidence.** "The doc says X" is a claim; "the doc doesn't mention Y" is a gap. Check ownership against ownership files in the tree and commit history, and when a doc and a person disagree, don't auto-resolve toward the doc.

State what was actually run, never more than that. If nothing was run, say so — in chat, and never in a published artifact.

## Build the lever when the work isn't trivial

For anything beyond a couple of obvious edits, write the script, codemod, or generator that does the work instead of doing it by hand, and make it safe to re-run.

This is the single strongest move available for being trusted. A hand-done change can only be re-verified by redoing it, so a reviewer either takes your word or spends their own hour. A deterministic script is an artifact they can read and re-run in a minute, which is what turns "I checked all 60 call sites" into a claim that costs nothing to believe.

Do the first unit by hand to learn the recipe, then build the tool and prove it reproduces that unit. Build the smallest thing that does or proves the job, never a framework. Commit the lever when the work outlives the session.

## Encode a repeated correction in structure, not in more prose

The second time the same instruction has to be written, stop writing it. Ask whether it can be a type that makes the bad state unrepresentable, a lint rule or CI gate, a canonical helper, or a runtime check — in that order of preference, because the weaker the guard, the more likely the next person copies around it.

A note in `kb/lessons/` is the right first home for a correction, but a lesson that describes a rule a linter could enforce is only half-finished. Route it: one-off stays a note, recurring becomes a mechanism, and the note then points at the mechanism.

## Minimize what the reader has to hold

Maintainability is the work a reader does to understand the code. Two axes: how many layers sit between their question and the answer, and how much hidden or mutable state they must keep in their head. Both matter independently.

Collapse wrappers with one caller and adapters with no second implementation. Prefer pure functions over mutation, locals over fields, fields over module state. Name an invariant once at the boundary rather than in every consumer. Before adding a layer, ask whether it reduces load somewhere else by at least as much.

The test: can a new reader answer "where does X come from?" and "what can change X?" in under thirty seconds?

## Sequence the work so the sequence proves itself

Break multi-step work into units that each end in a verifiable state, check each before starting the next, and order the commits and PRs so a reviewer can follow the proof rather than reconstruct it. This is what makes a stacked PR reviewable and what stops a long run from having to be re-audited from the start.
