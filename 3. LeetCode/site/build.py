#!/usr/bin/env python3
"""Build site/data.json from curriculum.json, progress.json and the problem folders.

The page in site/index.html is static and reads data.json. Run this after any
change to progress (coach.py done) or to a problem folder, then commit both.
The daily scheduled task does this automatically.

    python3 site/build.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import coach  # noqa: E402


def read(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def problem_payload(kind: str, p: dict, prog) -> dict:
    folder = coach.folder_for(p)
    st = coach.state_of(p, prog)
    problem_md = read(folder / "PROBLEM.md")
    scaffolded = bool(problem_md) and "TODO_METHOD_NAME" not in read(folder / "solution.py") \
        and "_(Claude fills this in" not in problem_md
    return {
        "kind": kind,
        "id": p["id"],
        "title": p["title"],
        "slug": p["slug"],
        "difficulty": p["difficulty"],
        "url": p["url"],
        "pattern": coach.pattern_name(p["pattern"]),
        "pattern_md": read(ROOT / coach.pattern_file(p["pattern"])),
        "problem_md": problem_md,
        "notes_md": read(folder / "NOTES.md"),
        "scaffolded": scaffolded,
        "state": {k: st.get(k) for k in ("status", "interval", "due", "last_rating", "last_done", "reps")},
        "started_at": st.get("started_at"),
    }


def main() -> None:
    prog = coach.progress()
    cur = coach.curriculum()
    today = coach.today()

    plan = [problem_payload(kind, p, prog) for kind, p in coach.plan(prog)]

    counts = {"new": 0, "learning": 0, "review": 0, "mastered": 0}
    patterns = []
    for pat in cur["patterns"]:
        cells = []
        for p in cur["problems"]:
            if p["pattern"] != pat["id"]:
                continue
            status = coach.state_of(p, prog)["status"]
            counts[status] += 1
            cells.append({"id": p["id"], "title": p["title"], "difficulty": p["difficulty"],
                          "status": status, "url": p["url"]})
        patterns.append({"id": pat["id"], "name": pat["name"], "problems": cells})

    upcoming = []
    for p in cur["problems"]:
        st = prog["problems"].get(p["id"])
        if st and st.get("due") and st["status"] in ("learning", "review"):
            upcoming.append({"id": p["id"], "title": p["title"], "due": st["due"],
                             "interval": st.get("interval")})
    upcoming.sort(key=lambda u: u["due"])

    recent = [h for h in prog["history"] if h.get("event") == "done"][-10:]
    titles = {p["id"]: p["title"] for p in cur["problems"]}
    for h in recent:
        h["title"] = titles.get(h["id"], h["id"])

    data = {
        "generated_at": datetime.now().isoformat(timespec="minutes"),
        "today": today.isoformat(),
        "streak": prog["streak"]["count"],
        "timebox_minutes": coach.TIMEBOX_MINUTES,
        "plan": plan,
        "counts": counts,
        "due_today": len(coach.due_reviews(prog)),
        "patterns": patterns,
        "upcoming": upcoming[:8],
        "recent": list(reversed(recent)),
    }
    out = HERE / "data.json"
    out.write_text(json.dumps(data, indent=1) + "\n")
    print(f"wrote {out.relative_to(ROOT)}  ({len(plan)} item(s) in today's plan)")


if __name__ == "__main__":
    main()
