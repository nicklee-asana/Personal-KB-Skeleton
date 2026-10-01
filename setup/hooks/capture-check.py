#!/usr/bin/env python3
"""Cursor hook: notice when a session did work but recorded nothing.

The capture triggers in the knowledge-base rule are standing instructions, and
nothing proves they fired. This closes part of that gap: detection is
deterministic (it counts what the agent actually touched), and the response is a
follow-up user turn, which lands harder than a rule loaded at session start.

Wired to three events (see hooks.json). Dispatch is on `hook_event_name`:

  afterFileEdit  {"file_path", "edits"}  -> accounting: work vs. capture
  postToolUse    {"tool_name", ...}      -> accounting: research-only sessions
  stop           {"status", "loop_count"} -> the verdict, and the nudge

State lives per conversation under ~/.cursor/kb-capture/ and is deleted at
`stop`, so accounting is per agent turn rather than per conversation.

Three deliberate limits:

1. It nudges at most once per conversation. `loop_count` counts follow-ups this
   script already triggered, and a nonzero count suppresses further ones. An
   automation that nags gets uninstalled, which costs more than a missed note.
2. `postToolUse` fires on every tool call, so leaving it out of hooks.json is a
   latency/coverage trade, not a bug. Without it, read-only research sessions --
   the ones most likely to establish a fact -- go undetected.
3. It cannot judge whether anything durable actually came up; only the model can.
   So the follow-up says outright that "nothing to record" is a valid answer.
   Without that, the nudge pressures the agent into inventing a note to satisfy
   it, and a fabricated note is worse than a missing one.

Fails open and silently: any unexpected input prints `{}` and exits 0. It is
bookkeeping, and bookkeeping must never block a turn or corrupt a response.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KB = REPO / "kb"

STATE_DIR = Path(
    os.environ.get("KB_CAPTURE_STATE") or Path.home() / ".cursor" / "kb-capture"
)
STATE_TTL_SECONDS = 14 * 24 * 3600

# Tools that indicate reading around rather than changing things.
RESEARCH_TOOLS = {"Read", "Grep", "Glob", "codebase_search", "CodebaseSearch"}
# Below this, a session was passing through rather than investigating.
RESEARCH_THRESHOLD = 12


def emit(obj: dict) -> int:
    print(json.dumps(obj))
    return 0


def within(path: Path, base: Path) -> bool:
    return path == base or base in path.parents


def in_scope(payload: dict) -> bool:
    """Stay silent in workspaces that don't contain this repo."""
    for root in payload.get("workspace_roots") or []:
        try:
            resolved = Path(root).resolve()
        except (OSError, ValueError):
            continue
        if resolved == REPO or resolved in REPO.parents:
            return True
    return False


def state_file(conversation_id: str) -> Path:
    safe = "".join(c for c in conversation_id if c.isalnum() or c in "-_")[:120]
    return STATE_DIR / f"{safe or 'unknown'}.json"


def load_state(path: Path) -> dict:
    try:
        loaded = json.loads(path.read_text())
        return loaded if isinstance(loaded, dict) else {}
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def save_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state))
    except OSError:
        pass


def prune_old_state() -> None:
    cutoff = time.time() - STATE_TTL_SECONDS
    try:
        for stale in STATE_DIR.glob("*.json"):
            try:
                if stale.stat().st_mtime < cutoff:
                    stale.unlink()
            except OSError:
                continue
    except OSError:
        pass


def record_edit(payload: dict, path: Path) -> None:
    raw = payload.get("file_path") or ""
    if not raw:
        return
    try:
        edited = Path(raw).resolve()
    except (OSError, ValueError):
        return

    state = load_state(path)
    if within(edited, KB):
        state["captured"] = True
    elif not within(edited, REPO):
        # Edits elsewhere in the repo are maintenance of the system itself, not
        # work that could have taught us something.
        state["work"] = int(state.get("work") or 0) + 1
        names = state.setdefault("names", [])
        if isinstance(names, list) and edited.name not in names and len(names) < 3:
            names.append(edited.name)
    save_state(path, state)


def record_tool(payload: dict, path: Path) -> None:
    if (payload.get("tool_name") or "") not in RESEARCH_TOOLS:
        return
    state = load_state(path)
    state["research"] = int(state.get("research") or 0) + 1
    save_state(path, state)


def followup(edits: int, names: list, research: int) -> str:
    if edits:
        sample = f" ({', '.join(names)}{'…' if edits > len(names) else ''})" if names else ""
        observed = f"edited {edits} file(s) outside the knowledge base{sample}"
    else:
        observed = f"read or searched {research} times without editing anything"

    return (
        f"Automated capture check: this turn {observed}, and wrote nothing under "
        f"`{KB}`.\n\n"
        f"Per the capture triggers in the knowledge-base rule, decide whether "
        f"anything durable was established — how something works, who owns what, "
        f"why a decision was made, or a correction to an existing note. If so, "
        f"record it per `kb/CONVENTIONS.md` and then run "
        f"`python3 scripts/kb.py sync && python3 scripts/kb.py check`.\n\n"
        f"If nothing durable came up, that is a normal and expected outcome: say "
        f"so in one line and stop. Do not write a note to satisfy this check — a "
        f"note nobody needed is worse than no note, because it dilutes the ones "
        f"that matter."
    )


def verdict(payload: dict, path: Path) -> dict:
    state = load_state(path)
    prune_old_state()
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass

    if payload.get("status") != "completed":
        return {}
    if int(payload.get("loop_count") or 0) > 0:
        return {}
    if state.get("captured"):
        return {}

    edits = int(state.get("work") or 0)
    research = int(state.get("research") or 0)
    if edits == 0 and research < RESEARCH_THRESHOLD:
        return {}

    names = state.get("names")
    return {"followup_message": followup(edits, names if isinstance(names, list) else [], research)}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, OSError):
        return emit({})
    if not isinstance(payload, dict):
        return emit({})

    conversation_id = payload.get("conversation_id") or ""
    if not conversation_id or not in_scope(payload):
        return emit({})

    path = state_file(conversation_id)
    event = payload.get("hook_event_name") or ""

    if event == "afterFileEdit":
        record_edit(payload, path)
    elif event == "postToolUse":
        record_tool(payload, path)
    elif event == "stop":
        return emit(verdict(payload, path))
    return emit({})


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Never let bookkeeping break a turn.
        sys.exit(emit({}))
