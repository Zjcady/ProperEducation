#!/usr/bin/env python3
"""Build site/data.json from curriculum.json, progress.json and the content folders.

    python3 site/build.py

Run after coach.py done / checks / touch, then commit. The daily task does it too.
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


def problem_payload(entry: dict, prog) -> dict:
    p = entry["item"]
    folder = coach.folder_for(p)
    st = coach.state_of(p, prog)
    return {
        "kind": entry["kind"], "type": "problem",
        "id": p["id"], "title": p["title"], "slug": p["slug"], "difficulty": p["difficulty"], "url": p["url"],
        "pattern": coach.pattern_name(p["pattern"]),
        "pattern_md": read(ROOT / coach.pattern_file(p["pattern"])),
        "problem_md": read(folder / "PROBLEM.md"),
        "scaffolded": coach.is_scaffolded("problem", p),
        "state": {k: st.get(k) for k in ("status", "interval", "due", "last_rating", "last_done", "reps")},
        "started_at": st.get("started_at"),
        "bell": coach.LEETCODE_BELL_MINUTES,
    }


def build_payload(entry: dict, prog) -> dict:
    b = entry["item"]
    folder = coach.build_folder(b)
    st = coach.build_state(b, prog)
    out = {
        "kind": entry["kind"], "type": "build",
        "id": b["id"], "title": b["title"], "track": coach.track_name(b["track"]), "item_kind": b["kind"],
        "folder": b["folder"], "steps": b["steps"], "step": st.get("step", 0),
        "scaffolded": coach.is_scaffolded("build", b),
        "state": {k: st.get(k) for k in ("status", "checks_score", "checks_due", "checks_last", "last_done")},
        "started_at": st.get("started_at"),
        "bell": 5 if entry["kind"] == "checks" else coach.BLOCK_MINUTES,
    }
    if b["kind"] == "chapter":
        checks = coach.load_json(folder / "checks.json", {}).get("questions", [])
        if "{{" in read(folder / "checks.json"):
            checks = []
        out.update({"read_md": read(folder / "read.md"), "challenge_md": read(folder / "CHALLENGE.md"),
                    "checks": checks})
    else:
        out["readme_md"] = read(folder / "README.md")
    return out


def floor_text(prog) -> str:
    due = coach.checks_due(prog)
    if due:
        return f"Checks review for {due[0]['id']} {due[0]['title']}. About 5 minutes."
    b = coach.next_build(prog)
    if b and b["kind"] == "chapter" and coach.is_scaffolded("build", b) \
            and not prog["build"].get(b["id"], {}).get("checks_score"):
        return f"Take the checks for {b['id']} {b['title']} below. About 5 minutes."
    taken = [b for b in coach.curriculum()["build"] if prog["build"].get(b["id"], {}).get("checks_score")]
    if taken:
        return f"Retake the checks for {taken[-1]['id']} {taken[-1]['title']}. Retrieval practice, 5 minutes."
    return "Read today's pattern card for two minutes, then in a session: python3 coach.py touch"


def main() -> None:
    prog = coach.progress()
    cur = coach.curriculum()

    plan = []
    for entry in coach.plan(prog):
        plan.append(problem_payload(entry, prog) if entry["type"] == "problem" else build_payload(entry, prog))

    counts = {"new": 0, "learning": 0, "review": 0, "mastered": 0}
    patterns = []
    for pat in cur["patterns"]:
        cells = []
        for p in cur["problems"]:
            if p["pattern"] != pat["id"]:
                continue
            status = coach.state_of(p, prog)["status"]
            counts[status] += 1
            cells.append({"id": p["id"], "title": p["title"], "status": status, "url": p["url"]})
        patterns.append({"name": pat["name"], "problems": cells})

    tracks = []
    for t in cur["tracks"]:
        if t["id"] == "leetcode":
            continue
        cells = [{"id": b["id"], "title": b["title"], "status": coach.build_state(b, prog)["status"],
                  "kind": b["kind"]} for b in cur["build"] if b["track"] == t["id"]]
        tracks.append({"name": t["name"], "items": cells})

    titles = {p["id"]: p["title"] for p in cur["problems"]}
    titles.update({b["id"]: b["title"] for b in cur["build"]})
    upcoming = []
    for p in cur["problems"]:
        st = prog["problems"].get(p["id"])
        if st and st.get("due") and st["status"] in ("learning", "review"):
            upcoming.append({"id": p["id"], "title": p["title"], "due": st["due"], "what": "re-solve"})
    for b in cur["build"]:
        st = prog["build"].get(b["id"], {})
        if st.get("checks_due"):
            upcoming.append({"id": b["id"], "title": b["title"], "due": st["checks_due"], "what": "checks"})
    upcoming.sort(key=lambda u: u["due"])

    recent = []
    for h in prog["history"][-40:]:
        if h.get("event") in ("done", "checks", "touch"):
            recent.append({**h, "title": titles.get(h.get("id", ""), h.get("note", ""))})

    data = {
        "generated_at": datetime.now().isoformat(timespec="minutes"),
        "today": coach.iso(coach.today()),
        "streak": prog["streak"]["count"],
        "counted_today": coach.counted_today(prog),
        "bonus_used": coach.bonus_today(prog), "bonus_cap": coach.BONUS_CAP,
        "block_minutes": coach.BLOCK_MINUTES, "leetcode_bell": coach.LEETCODE_BELL_MINUTES,
        "floor": floor_text(prog),
        "plan": plan,
        "counts": counts, "patterns": patterns, "tracks": tracks,
        "upcoming": upcoming[:10], "recent": list(reversed(recent))[:10],
    }
    out = HERE / "data.json"
    out.write_text(json.dumps(data, indent=1) + "\n")
    print(f"wrote {out.relative_to(ROOT)}  ({len(plan)} block(s) today)")


if __name__ == "__main__":
    main()
