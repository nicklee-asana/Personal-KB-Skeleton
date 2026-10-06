# Engineering Principles

How work gets done. Reporting rules are in `response-preferences.md`; recorded knowledge is in `kb/`. Replace the generic examples below with your repo's equivalents.

## Prove it against the real artifact

Before calling anything done, check the thing itself: run the feature, read the actual value, inspect the diff. A proxy, "it compiles", a targeted test, or a subagent's report doesn't count. Read a delegate's diff, not its summary.

## A verdict covers only what the run executed

Before claiming something is verified, confirm the run and the claim are about the same content.

- **A targeted test is one gate.** Typecheck and generated-registry freshness suites are often separate targets. Run them before submitting.
- **A hand-resolved conflict has never compiled.** Build every file touched between finishing the rebase and pushing.
- **A green downstream job doesn't prove the target ran,** because of affected-target selection and the remote cache. If two branches disagree on identical content, trust the failure.
- **A result is void if the tree changed under it.** Run `git branch --show-current` before any commit, amend, or relied-on run; read each commit's stat and stop on unexpected files. If the checkout is in use, make a worktree rather than switching branches.
- **Take expectations from the accessor the implementation reads,** or from a literal the test set up, never from a sibling accessor.
- **A doc's silence is not evidence.** Check ownership against ownership files and commit history. When a doc and a person disagree, don't default to the doc.

State only what was actually run, and say plainly what wasn't checked.

## Build the lever when the work isn't trivial

Beyond a couple of obvious edits, write a re-runnable script, codemod, or generator instead of editing by hand. Do the first unit by hand, then prove the tool reproduces it. Build the smallest tool that does the job, and commit it if the work outlives the session.

## Encode a repeated correction in structure

The second time an instruction has to be written, make it a mechanism instead. In order of preference: a type, a lint or CI gate, a canonical helper, a runtime check. A `kb/lessons/` note is a correction's first home. A recurring one becomes a mechanism, and the note then points to it.

## Minimize what the reader has to hold

- Collapse wrappers with one caller and adapters with one implementation.
- Prefer pure functions to mutation, locals to fields, and fields to module state.
- Name an invariant once, at the boundary.
- Add a layer only if it removes at least as much load elsewhere.

Test: a new reader can answer "where does X come from?" and "what can change X?" in 30 seconds.

## Sequence work so it proves itself

Split multi-step work into units that each end in a verifiable state, and check each before starting the next. Order commits and PRs so a reviewer can follow the proof.
