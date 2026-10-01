#!/usr/bin/env python3
"""Validate, regenerate, and export the knowledge base.

    kb.py check          verify invariants; exit 1 on any failure
    kb.py sync           rewrite generated blocks in index files
    kb.py export DIR     emit a shareable copy containing only team-visible notes

`check` also validates projects/, which follows a lighter contract of its own:
each project directory needs a README.md with front matter and a lifecycle
status. Directories prefixed with `_` are ignored.

Generated blocks are delimited by `<!-- kb:generated:NAME -->` and
`<!-- kb:generated:end -->`. Everything outside them is hand-written and
never touched. `check` fails when a generated block is out of date, so a
forgotten `sync` surfaces at commit time rather than silently degrading
retrieval.

Visibility has three tiers, only two of which live here:

    visibility: team    shareable with the team; the default
    visibility: self    stays in this repo, excluded from every export
    personal/           career and personal material, never in kb/ at all

`export` filters to team notes, regenerates every index from the filtered
set, and drops table rows pointing at excluded files, so the result has no
dangling links and never names a file it doesn't contain.

No third-party dependencies: this has to keep working years from now
without a virtualenv.
"""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KB = REPO / "kb"
PROJECTS = REPO / "projects"

PROJECT_STATUSES = {"exploring", "designing", "implementing", "shipped", "abandoned"}
PROJECT_REQUIRED = {"title", "status", "domain", "visibility", "started", "updated", "summary"}

STATUSES = {"verified", "reported", "stale"}
VISIBILITIES = {"team", "self"}
REQUIRED = {"title", "domain", "tags", "summary", "status", "updated", "visibility"}
MAX_LINES = 150
STRUCTURAL = {"INDEX.md", "CONVENTIONS.md"}

# Decay is opt-in per note via `half_life` (days) and renders as a marker in the
# generated index rows, which is the only surface retrieval actually reads. It is
# deliberately a label and never a warning: the six-month re-verification check
# that preceded it failed because the cheapest way to clear a warning is to edit
# `updated`, which leaves a note equally stale while making it look checked. A
# label asks for nothing, so there is nothing to satisfy dishonestly. Nothing is
# ever deleted or errored on by age.
DECAY_MARKS = ((2.0, " _(may be stale)_"), (1.0, " _(aging)_"))
DECAY_MARK_RE = re.compile(r" _\((?:aging|may be stale)\)_")

# A summary is copied verbatim into the generated index, which the agent reads as
# the note's description. A placeholder there is not merely unhelpful: it becomes
# the note's apparent content on every later pass, so the mistake compounds.
PLACEHOLDER_SUMMARIES = frozenset(
    {
        "unchanged", "no change", "no changes", "no changes needed", "nothing to update",
        "none", "n/a", "na", "empty", "same", "same as before", "as before", "see above",
        "tbd", "todo", "to do", "content unchanged", "file unchanged", "summary",
        "description", "notes", "this note", "placeholder", "wip",
    }
)

# Written into an export directory so a later export can tell its own output from
# whatever else might be sitting at that path.
EXPORT_MARKER = ".kb-export"

# Too common in a lesson's phrasing to distinguish one rule from another.
OVERLAP_STOPWORDS = frozenset(
    """
    the and but for from into with without not never always only just also more
    most much very when what which who whose why how you your they them their
    then there here such before after during while against about above below
    over under again once does did done have has had having will would should
    could can may might must shall are was were been being its it's this that
    these those something anything nothing thing things something's
    """.split()
)

# Containment above this between two lessons means they're competing, not complementary.
OVERLAP_THRESHOLD = 0.5

# Case-sensitive on "I" so that "i.e." doesn't trip it.
FIRST_PERSON = re.compile(r"\b(I|I'm|I'd|I've|my|My|me|Me|myself|Myself|mine)\b")

# Inline code is stripped before the first-person check: endpoints like
# `/1.1/users/me` and identifiers containing "my" are not first-person prose.
CODE_SPAN = re.compile(r"`[^`]*`")

# A specific path under personal/, as opposed to prose naming the directory.
# Requires a path character after the slash, so "`personal/`" doesn't trip it.
PERSONAL_PATH = re.compile(r"(?<![\w-])personal/[\w][\w./-]*")


# --------------------------------------------------------------------------
# minimal front-matter parsing
# --------------------------------------------------------------------------

def parse_front_matter(text: str) -> dict[str, object] | None:
    """Parse the YAML subset we actually use: scalars, inline lists, block lists."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None

    data: dict[str, object] = {}
    key = None
    for raw in text[4:end].splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  - ") or raw.startswith("- "):
            if key:
                data.setdefault(key, [])
                if isinstance(data[key], list):
                    data[key].append(raw.split("- ", 1)[1].strip())
            continue
        m = re.match(r"^(\w+):\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            data[key] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        elif val:
            data[key] = val
        else:
            data[key] = []
    return data


def body_lines(text: str):
    """Yield prose lines only: no front matter, code fences, or blockquotes."""
    parts = text.split("\n---", 1)
    body = parts[1] if text.startswith("---\n") and len(parts) > 1 else text
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.lstrip().startswith(">"):
            continue
        yield line


@dataclass
class Note:
    path: Path
    root: Path
    fm: dict[str, object]
    text: str

    @property
    def rel(self) -> str:
        return str(self.path.relative_to(self.root.parent))

    @property
    def visibility(self) -> str:
        return str(self.fm.get("visibility", "team"))

    @property
    def is_lesson(self) -> bool:
        return self.path.parent.name == "lessons"

    @property
    def is_meeting(self) -> bool:
        return self.path.parent.name == "meetings"

    def get(self, k: str, default=None):
        return self.fm.get(k, default)


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notices: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def notice(self, msg: str) -> None:
        """Worth saying, never worth failing on. Does not affect the exit code."""
        self.notices.append(msg)


# --------------------------------------------------------------------------
# collection
# --------------------------------------------------------------------------

def domains(kb: Path) -> list[str]:
    d = kb / "domains"
    return sorted(p.name for p in d.iterdir() if p.is_dir()) if d.exists() else []


def load_notes(kb: Path, res: Result) -> list[Note]:
    notes = []
    for p in sorted(kb.rglob("*.md")):
        if p.name in STRUCTURAL:
            continue
        text = p.read_text()
        fm = parse_front_matter(text)
        if fm is None:
            res.error(f"{p.relative_to(kb.parent)}: missing YAML front matter")
            continue
        notes.append(Note(p, kb, fm, text))
    return notes


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def _bare(text: str) -> str:
    """Strip the decoration a placeholder might be wearing."""
    return text.strip().lower().strip(" \t\"'`*_~.,!()[]")


def check_front_matter(kb: Path, notes: list[Note], res: Result) -> None:
    valid_domains = set(domains(kb)) | {"cross-cutting"}
    for n in notes:
        missing = REQUIRED - set(n.fm)
        if missing:
            res.error(f"{n.rel}: front matter missing {sorted(missing)}")

        dom = n.get("domain")
        if dom and dom not in valid_domains:
            res.error(f"{n.rel}: domain '{dom}' is not a domain directory or 'cross-cutting'")

        st = n.get("status")
        if st and st not in STATUSES:
            res.error(f"{n.rel}: status '{st}' not in {sorted(STATUSES)}")
        if st == "verified" and not n.get("sources"):
            res.error(f"{n.rel}: status is 'verified' but 'sources' is empty")

        if n.visibility not in VISIBILITIES:
            res.error(f"{n.rel}: visibility '{n.visibility}' not in {sorted(VISIBILITIES)}")

        summary = n.get("summary")
        if isinstance(summary, str):
            bare = _bare(summary)
            if bare in PLACEHOLDER_SUMMARIES:
                res.error(
                    f"{n.rel}: summary '{summary.strip()}' is a placeholder, and the "
                    f"generated index would carry it as this note's description"
                )
            elif bare and bare == _bare(str(n.get("title", ""))):
                res.warn(
                    f"{n.rel}: summary only restates the title, so the index row it "
                    f"generates adds nothing to routing"
                )

        # Dates are recorded so a contradiction can be adjudicated later, not to
        # drive a review schedule. Validated, never nagged about.
        hl = n.get("half_life")
        if hl is not None:
            try:
                if int(hl) <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                res.error(f"{n.rel}: half_life '{hl}' is not a positive number of days")

        upd = n.get("updated")
        if isinstance(upd, str):
            try:
                date.fromisoformat(upd)
            except ValueError:
                res.error(f"{n.rel}: updated '{upd}' is not an ISO date")

        if len(n.text.splitlines()) > MAX_LINES and str(n.get("size_exempt", "")).lower() != "true":
            res.warn(
                f"{n.rel}: {len(n.text.splitlines())} lines exceeds {MAX_LINES}; "
                f"split it or set 'size_exempt: true' with a reason in the body"
            )


def check_shareability(notes: list[Note], res: Result) -> None:
    """Team-visible notes shouldn't carry personal framing or name colleagues."""
    for n in notes:
        if n.is_meeting and n.visibility == "team":
            res.warn(
                f"{n.rel}: meeting notes record who said what and are 'team' — "
                f"set 'visibility: self' unless you've written it as a shareable summary"
            )
        if n.visibility != "team":
            continue
        if "people" in (n.get("tags") or []):
            res.warn(
                f"{n.rel}: tagged 'people' but visibility is 'team' — "
                f"colleague names would be included in an export"
            )
        hits = [
            line.strip()
            for line in body_lines(n.text)
            if FIRST_PERSON.search(CODE_SPAN.sub("", line))
        ]
        if hits:
            res.warn(
                f"{n.rel}: {len(hits)} first-person line(s) in a team-visible note; "
                f"rewrite impersonally or set 'visibility: self'\n"
                f"          first: {hits[0][:88]}"
            )
        leaks = sorted({m.group(0) for m in PERSONAL_PATH.finditer(n.text)})
        if leaks:
            res.error(
                f"{n.rel}: team-visible note cites '{leaks[0]}' — personal/ is never "
                f"exported, so the path ships to teammates while the file doesn't; "
                f"cite it in prose (\"1:1, September 3 2026\") instead"
            )


def check_registration(kb: Path, res: Result) -> None:
    top = (kb / "INDEX.md").read_text()
    for d in domains(kb):
        if d not in top:
            res.error(f"domain '{d}' is not registered in kb/INDEX.md")
        if not (kb / "domains" / d / "INDEX.md").exists():
            res.error(f"domain '{d}' has no INDEX.md")


def _significant_words(text: str) -> set[str]:
    words = re.findall(r"[a-z][a-z0-9_-]{2,}", text.lower())
    return {w for w in words if w not in OVERLAP_STOPWORDS}


def check_lesson_overlap(notes: list[Note], res: Result) -> None:
    """Two lessons saying nearly the same thing dilute both.

    Measured as containment rather than Jaccard: the case worth catching is one
    lesson being a subset of a broader one, which a symmetric score dilutes as
    the longer text grows. Reported, never auto-merged — collapsing two pieces
    of reasoning into one is a judgement call about which framing survives.
    """
    lessons = [n for n in notes if n.is_lesson]
    keyed = [(n, _significant_words(f"{n.get('title', '')} {n.get('summary', '')}")) for n in lessons]
    for i, (a, aw) in enumerate(keyed):
        for b, bw in keyed[i + 1:]:
            if not aw or not bw:
                continue
            overlap = len(aw & bw) / min(len(aw), len(bw))
            if overlap >= OVERLAP_THRESHOLD:
                shared = ", ".join(sorted(aw & bw)[:6])
                res.warn(
                    f"{a.rel} and {b.rel}: {overlap:.0%} keyword overlap "
                    f"({shared}) — merge into the more general rule, or sharpen both"
                )


def check_lessons(kb: Path, notes: list[Note], res: Result) -> None:
    valid = set(domains(kb))
    for n in notes:
        if not n.is_lesson:
            continue
        applies = n.get("applies_to")
        if not applies:
            res.error(
                f"{n.rel}: lessons need 'applies_to' listing domains (or ['all']), "
                f"otherwise the lesson is unreachable from any domain"
            )
            continue
        if isinstance(applies, list):
            for a in applies:
                if a != "all" and a not in valid:
                    res.error(f"{n.rel}: applies_to '{a}' is not a domain")


@dataclass
class Project:
    path: Path
    fm: dict[str, object]

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def visibility(self) -> str:
        return str(self.fm.get("visibility", "self"))

    def get(self, k: str, default=None):
        return self.fm.get(k, default)


def load_projects(res: Result) -> list[Project]:
    """Projects sit outside kb/ and follow their own, lighter contract."""
    if not PROJECTS.exists():
        return []
    valid_domains = set(domains(KB)) | {"cross-cutting"}
    found = []
    for d in sorted(p for p in PROJECTS.iterdir() if p.is_dir()):
        if d.name.startswith("_"):
            continue
        readme = d / "README.md"
        rel = f"projects/{d.name}"
        if not readme.exists():
            res.error(f"{rel}: no README.md — every project needs a spec")
            continue
        fm = parse_front_matter(readme.read_text())
        if fm is None:
            res.error(f"{rel}/README.md: missing YAML front matter")
            continue
        found.append(Project(d, fm))

        missing = PROJECT_REQUIRED - set(fm)
        if missing:
            res.error(f"{rel}/README.md: front matter missing {sorted(missing)}")
        st = fm.get("status")
        if st and st not in PROJECT_STATUSES:
            res.error(f"{rel}/README.md: status '{st}' not in {sorted(PROJECT_STATUSES)}")
        dom = fm.get("domain")
        if dom and dom not in valid_domains:
            res.error(f"{rel}/README.md: domain '{dom}' is not a domain or 'cross-cutting'")
        vis = fm.get("visibility")
        if vis and vis not in VISIBILITIES:
            res.error(f"{rel}/README.md: visibility '{vis}' not in {sorted(VISIBILITIES)}")
        for field_name in ("started", "updated"):
            val = fm.get(field_name)
            if isinstance(val, str):
                try:
                    date.fromisoformat(val)
                except ValueError:
                    res.error(f"{rel}/README.md: {field_name} '{val}' is not an ISO date")

        if st in {"shipped", "abandoned"}:
            res.warn(
                f"{rel}: status is '{st}' — extract what it taught into kb/ "
                f"(how it works, why the approach won, or why it was dropped)"
            )
    return found


def check_links(root: Path, res: Result, label: str = "") -> int:
    broken = 0
    for p in sorted(root.rglob("*.md")):
        if ".git" in p.parts:
            continue
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", p.read_text()):
            target = m.group(2)
            if target.startswith(("http://", "https://", "#", "/", "mailto:")):
                continue
            if not (p.parent / target.split("#")[0]).resolve().exists():
                res.error(f"{label}{p.relative_to(root)}: broken link -> {target}")
                broken += 1
    return broken


# --------------------------------------------------------------------------
# generation
# --------------------------------------------------------------------------

BLOCK = re.compile(
    r"(<!-- kb:generated:(?P<name>[\w-]+) -->\n)(?P<body>.*?)(<!-- kb:generated:end -->)",
    re.S,
)


def render_blocks(
    kb: Path,
    notes: list[Note],
    mark_self: bool,
    projects: list["Project"] | None = None,
) -> dict[Path, dict[str, str]]:
    """Desired content of every generated block, keyed by file."""
    out: dict[Path, dict[str, str]] = {}
    by_domain: dict[str, list[Note]] = {d: [] for d in domains(kb)}
    lessons: list[Note] = []
    meetings: list[Note] = []

    for n in notes:
        if n.is_lesson:
            lessons.append(n)
        elif n.is_meeting:
            meetings.append(n)
        elif n.path.parent.parent.name == "domains":
            by_domain.setdefault(n.path.parent.name, []).append(n)

    def decay_mark(n: Note) -> str:
        """How many half-lives past `updated` this note is, as a reader-visible label."""
        hl = n.get("half_life")
        upd = n.get("updated")
        if not hl or not upd:
            return ""
        try:
            age = (date.today() - date.fromisoformat(str(upd))).days
            lives = age / int(hl)
        except (TypeError, ValueError):
            return ""
        for threshold, mark in DECAY_MARKS:
            if lives >= threshold:
                return mark
        return ""

    def tag(n: Note) -> str:
        self_mark = " _(yours only)_" if mark_self and n.visibility == "self" else ""
        return decay_mark(n) + self_mark

    for dom, items in by_domain.items():
        idx = kb / "domains" / dom / "INDEX.md"
        rows = ["| File | What it covers |", "|---|---|"]
        for n in sorted(items, key=lambda x: x.path.name):
            rows.append(f"| [{n.path.name}]({n.path.name}) | {n.get('summary', '')}{tag(n)} |")

        related = [
            les for les in lessons
            if dom in (les.get("applies_to") or []) or "all" in (les.get("applies_to") or [])
        ]
        if related:
            lines = ["| Lesson | Rule |", "|---|---|"]
            for les in sorted(related, key=lambda x: x.path.name):
                lines.append(
                    f"| [{les.get('title', les.path.name)}](../../lessons/{les.path.name}) "
                    f"| {les.get('summary', '')}{tag(les)} |"
                )
            lesson_block = "\n".join(lines) + "\n"
        else:
            lesson_block = "_No lessons recorded for this domain yet._\n"

        # Specs live outside kb/, so a domain index is the only place they surface.
        # The heading lives inside the block: with no projects the section vanishes
        # entirely, which is also what makes the export come out clean.
        related_projects = [p for p in (projects or []) if p.get("domain") == dom]
        if related_projects:
            plines = ["### Related project specs", "", "| Project | Status | What it is |", "|---|---|---|"]
            for proj in sorted(related_projects, key=lambda x: x.name):
                mark = " _(yours only)_" if mark_self and proj.visibility == "self" else ""
                plines.append(
                    f"| [{proj.get('title', proj.name)}](../../../projects/{proj.name}/README.md) "
                    f"| {proj.get('status', '')} | {proj.get('summary', '')}{mark} |"
                )
            project_block = "\n".join(plines) + "\n"
        else:
            project_block = ""

        out[idx] = {
            "files": "\n".join(rows) + "\n",
            "lessons": lesson_block,
            "projects": project_block,
        }

    if (kb / "lessons" / "INDEX.md").exists():
        rows = ["| Date | Lesson | Applies to |", "|---|---|---|"]
        for les in sorted(lessons, key=lambda x: x.path.name, reverse=True):
            applies = ", ".join(les.get("applies_to") or [])
            rows.append(
                f"| {les.path.name[:10]} | [{les.get('title', les.path.name)}]({les.path.name}) "
                f"| {applies}{tag(les)} |"
            )
        out[kb / "lessons" / "INDEX.md"] = {"lessons": "\n".join(rows) + "\n"}

    if (kb / "meetings" / "INDEX.md").exists():
        rows = ["| Date | Notes | Domain |", "|---|---|---|"]
        for m in sorted(meetings, key=lambda x: x.path.name, reverse=True):
            rows.append(
                f"| {m.path.name[:10]} | [{m.get('title', m.path.name)}]({m.path.name}) "
                f"| {m.get('domain', '')}{tag(m)} |"
            )
        if not meetings:
            rows = ["_No meetings recorded yet._"]
        out[kb / "meetings" / "INDEX.md"] = {"meetings": "\n".join(rows) + "\n"}

    if (kb / "tags.md").exists():
        tags: dict[str, list[Note]] = {}
        for n in notes:
            for t in n.get("tags") or []:
                tags.setdefault(t, []).append(n)
        rows = ["| Tag | Notes |", "|---|---|"]
        for t in sorted(tags):
            links = ", ".join(
                f"[{n.path.name}]({n.path.relative_to(kb)})"
                for n in sorted(tags[t], key=lambda x: x.path.name)
            )
            rows.append(f"| `{t}` | {links} |")
        out[kb / "tags.md"] = {"tags": "\n".join(rows) + "\n"}

    return out


def apply_blocks(root: Path, path: Path, blocks: dict[str, str], write: bool, res: Result) -> bool:
    if not path.exists():
        res.error(f"{path.relative_to(root)}: expected file does not exist (run: kb.py sync)")
        return False
    original = path.read_text()
    seen = set()

    def sub(m):
        seen.add(m.group("name"))
        return m.group(1) + blocks.get(m.group("name"), m.group("body")) + m.group(4)

    updated = BLOCK.sub(sub, original)
    # A decay marker changes with the calendar, not with an edit, so comparing it
    # would make `check` fail on a day nobody touched the repo — and a pre-commit
    # hook that fails for no authored reason is one people learn to bypass. Drift
    # in the marker alone is ignored here; the next `sync` refreshes it.
    for name in blocks:
        if name not in seen:
            res.error(
                f"{path.relative_to(root)}: missing block '<!-- kb:generated:{name} -->'"
            )

    if updated == original:
        return False
    if write:
        path.write_text(updated)
    elif DECAY_MARK_RE.sub("", updated) != DECAY_MARK_RE.sub("", original):
        res.error(f"{path.relative_to(root)}: generated block out of date (run: kb.py sync)")
    else:
        # Only an aging marker moved. Never a failure — but say so, or the label
        # silently lags however long it has been since the last sync.
        res.notice(f"{path.relative_to(root)}: an aging marker has moved (run: kb.py sync)")
    return True


# --------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------

def prune_dangling_rows(root: Path) -> tuple[int, int]:
    """Remove references the export excludes, in two passes.

    A table row whose *only* link points at a withheld note is dropped whole,
    since the row exists to carry that link. But a row can also carry several
    links — `tags.md` lists every note sharing a tag — and dropping it would
    lose the notes that did ship while keeping it leaks the ones that didn't.
    So any surviving link to a missing target is unwrapped to its plain text.
    The same unwrapping handles hand-written prose links in note bodies.

    Returns (rows dropped, links unwrapped).
    """
    dropped = unlinked = 0

    def is_dead(target: str, base: Path) -> bool:
        if target.startswith(("http", "#", "/", "mailto:")):
            return False
        return not (base / target.split("#")[0]).resolve().exists()

    for p in sorted(root.rglob("*.md")):
        lines = p.read_text().splitlines(keepends=True)
        keep = []
        for line in lines:
            if line.lstrip().startswith("|"):
                targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", line)
                rel = [t for t in targets if not t.startswith(("http", "#", "/", "mailto:"))]
                if rel and all(is_dead(t, p.parent) for t in rel):
                    dropped += 1
                    continue
            keep.append(line)

        text = "".join(keep)

        def unwrap(m: "re.Match[str]") -> str:
            nonlocal unlinked
            if is_dead(m.group(2), p.parent):
                unlinked += 1
                return m.group(1)
            return m.group(0)

        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", unwrap, text)
        if text != "".join(lines):
            p.write_text(text)
    return dropped, unlinked


def export_target_is_safe(target: Path, res: Result) -> bool:
    """Refuse to recursively delete anything this command didn't create.

    Export replaces its destination wholesale, so a mistyped path is a silent
    `rm -rf` of whatever was there. Only three destinations are safe to clobber:
    one that doesn't exist, one that is empty, and one carrying the marker from a
    previous export.
    """
    resolved = target.resolve()
    if resolved == REPO or resolved in REPO.parents:
        res.error(f"export target {resolved} contains this repo; refusing")
        return False
    if not resolved.exists():
        return True
    if not resolved.is_dir():
        res.error(f"export target {resolved} exists and is not a directory")
        return False
    if (resolved / EXPORT_MARKER).exists() or not any(resolved.iterdir()):
        return True
    res.error(
        f"export target {resolved} is not empty and holds no {EXPORT_MARKER} marker, "
        f"so it was not created by a previous export; refusing to delete it"
    )
    return False


def export(target: Path, res: Result) -> int:
    src_notes = load_notes(KB, res)
    check_front_matter(KB, src_notes, res)
    export_target_is_safe(target, res)
    if res.errors:
        # The caller prints the collected errors; printing them here too was the
        # source of every failure appearing twice.
        print("Refusing to export:")
        return 1

    shared = [n for n in src_notes if n.visibility == "team"]
    held = [n for n in src_notes if n.visibility != "team"]

    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / EXPORT_MARKER).write_text(
        "Generated by scripts/kb.py export. Safe to delete; this file is what lets a\n"
        "later export overwrite this directory without asking.\n"
    )

    for name in ("INDEX.md", "CONVENTIONS.md"):
        if (KB / name).exists():
            shutil.copy2(KB / name, target / name)
    for n in shared:
        dest = target / n.path.relative_to(KB)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(n.path, dest)

    for d in domains(KB):
        src_idx = KB / "domains" / d / "INDEX.md"
        if src_idx.exists() and (target / "domains" / d).exists():
            shutil.copy2(src_idx, target / "domains" / d / "INDEX.md")
    for area in ("lessons", "meetings"):
        if (target / area).exists() and (KB / area / "INDEX.md").exists():
            shutil.copy2(KB / area / "INDEX.md", target / area / "INDEX.md")

    out_res = Result()
    out_notes = load_notes(target, out_res)
    for path, blocks in render_blocks(target, out_notes, mark_self=False).items():
        apply_blocks(target, path, blocks, write=True, res=out_res)

    dropped, unlinked = prune_dangling_rows(target)

    print(f"kb export -> {target}")
    print(f"  included  {len(shared)} team note(s)")
    print(f"  withheld  {len(held)} note(s) marked 'self':")
    for n in sorted(held, key=lambda x: x.rel):
        print(f"              {n.rel}")
    if dropped:
        print(f"  pruned    {dropped} index row(s) referencing withheld notes")
    if unlinked:
        print(f"  unlinked  {unlinked} reference(s) to withheld notes")

    leaks = [n.path.name for n in held if any(
        n.path.name in p.read_text() for p in target.rglob("*.md")
    )]
    if leaks:
        for name in sorted(set(leaks)):
            res.error(f"export leaks a reference to withheld note '{name}'")

    broken = check_links(target, res, label="export: ")
    if not leaks and not broken:
        print("  verified  no dangling links, no references to withheld notes")
    return 1 if res.errors else 0


# --------------------------------------------------------------------------
# entry points
# --------------------------------------------------------------------------

def run(write: bool) -> int:
    res = Result()
    notes = load_notes(KB, res)

    check_front_matter(KB, notes, res)
    check_shareability(notes, res)
    check_registration(KB, res)
    check_lessons(KB, notes, res)
    check_lesson_overlap(notes, res)
    projects = load_projects(res)

    changed = []
    for path, blocks in render_blocks(KB, notes, mark_self=True, projects=projects).items():
        if apply_blocks(KB, path, blocks, write, res):
            changed.append(path)

    check_links(REPO, res)

    shared = sum(1 for n in notes if n.visibility == "team")
    print(
        f"kb {'sync' if write else 'check'}: {len(notes)} notes "
        f"({shared} team, {len(notes) - shared} self), {len(domains(KB))} domains, "
        f"{len(projects)} project(s)"
    )
    if write:
        for p in changed:
            print(f"  updated  {p.relative_to(REPO)}")
        if not changed:
            print("  all generated blocks already current")

    for n_ in res.notices:
        print(f"  note  {n_}")
    for w in res.warnings:
        print(f"  warn  {w}")
    for e in res.errors:
        print(f"  FAIL  {e}")

    if res.errors:
        print(f"\n{len(res.errors)} error(s)")
        return 1
    print(f"\nOK{f' ({len(res.warnings)} warning(s))' if res.warnings else ''}")
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "export":
        if len(sys.argv) < 3:
            print("usage: kb.py export DIR")
            return 2
        res = Result()
        code = export(Path(sys.argv[2]).expanduser().resolve(), res)
        for e in res.errors:
            print(f"  FAIL  {e}")
        return code
    if cmd not in {"check", "sync"}:
        print(__doc__)
        return 2
    return run(write=(cmd == "sync"))


if __name__ == "__main__":
    sys.exit(main())
