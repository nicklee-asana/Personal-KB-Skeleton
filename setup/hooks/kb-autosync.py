#!/usr/bin/env python3
"""Refresh the knowledge base's generated blocks on a timer, from an agent hook.

Aging markers (`half_life` in a note's front matter) are written into generated
index blocks, so they only move when `kb.py sync` runs. Nothing runs it on a
schedule, and the one person who would remember to has better things to hold in
his head. This closes that loop: any agent session start is a cheap moment to
run a sync that is almost always a no-op.

Fail-open by design. It never blocks a session, never prints on the common path,
and swallows every error — a knowledge-base refresh is not worth a broken hook.

Wire-up:
  Claude Code   a SessionStart hook in ~/.claude/settings.json
  Cursor        another entry on the `stop` array in ~/.cursor/hooks.json
Both pass JSON on stdin, which this ignores; it takes no arguments.

State: STAMP records the last successful run so repeated sessions in one day do
no work. Override the location with KB_SYNC_STAMP.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INTERVAL = 12 * 3600
STAMP = Path(
    os.environ.get("KB_SYNC_STAMP", Path.home() / ".cache" / "kb-sync" / "last-run")
)


def due() -> bool:
    try:
        return (time.time() - float(STAMP.read_text().split()[0])) > INTERVAL
    except Exception:
        return True


def stamp(note: str) -> None:
    try:
        STAMP.parent.mkdir(parents=True, exist_ok=True)
        STAMP.write_text(f"{time.time():.0f} {time.strftime('%Y-%m-%dT%H:%M:%S')} {note}\n")
    except Exception:
        pass


def main() -> int:
    try:
        sys.stdin.read()
    except Exception:
        pass

    if not (REPO / "scripts" / "kb.py").exists() or not due():
        return 0

    try:
        proc = subprocess.run(
            [sys.executable, "scripts/kb.py", "sync"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception:
        # A sync that cannot run is not a reason to stamp; try again next session.
        return 0

    changed = [
        line.strip() for line in proc.stdout.splitlines() if line.strip().startswith("updated ")
    ]
    stamp("ok" if proc.returncode == 0 else f"rc={proc.returncode}")

    if changed:
        print(
            json.dumps(
                {
                    "systemMessage": (
                        f"kb: refreshed {len(changed)} generated block(s) "
                        f"(aging markers). Commit when convenient."
                    )
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
