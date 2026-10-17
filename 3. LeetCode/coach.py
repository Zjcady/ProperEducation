#!/usr/bin/env python3
"""coach.py - the LeetCode coach. Built for ADHD and leaky memory.

Rules it enforces:
  * One new problem per day, max. Reviews come before new material.
  * At most 2 reviews per day. Missed days never pile up into a backlog.
  * A problem is only "done" after you rate how it went, which schedules
    the next review (spaced repetition).
  * Reviews are re-solves from a blank function. Reading your old code is
    not a review.

Commands:
  python3 coach.py                 same as `next`
  python3 coach.py next            what is the one thing to do right now
  python3 coach.py start <id>      begin a problem (creates folder, starts timer)
  python3 coach.py check <id>      run its tests, show elapsed time
  python3 coach.py hint <id> <n>   show hint number n (1, 2, 3) from PROBLEM.md
  python3 coach.py done <id> <r>   finish: r = 1 struggled, 2 needed hints, 3 clean
  python3 coach.py status          streak, progress by pattern, what is due
  python3 coach.py list [pattern]  the curriculum

<id> can be a number (1, 001) or a slug (two-sum).
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CURRICULUM = ROOT / "curriculum.json"
PROGRESS = ROOT / "progress.json"
PROBLEMS = ROOT / "problems"
TEMPLATE = ROOT / "_template"

MAX_REVIEWS_PER_DAY = 2
MAX_NEW_PER_DAY = 1
TIMEBOX_MINUTES = 25

# Spaced repetition. Rating -> what happens to the review interval (days).
#   1  struggled / looked at the answer  -> see it again tomorrow
#   2  solved with hints                 -> 3 days (or keep the current interval)
#   3  clean solve + explained it back   -> interval grows x2.5, starting at 3
FIRST_INTERVAL = 3
GROWTH = 2.5
MASTERED_AT_INTERVAL = 30  # days. Past this with a clean solve => mastered.


# ---------------------------------------------------------------- storage

def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open() as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    with path.open("w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
        f.write("\n")


def curriculum():
    return load_json(CURRICULUM, {"patterns": [], "problems": []})


def progress():
    data = load_json(PROGRESS, {})
    data.setdefault("problems", {})
    data.setdefault("streak", {"count": 0, "last_day": None})
    data.setdefault("history", [])
    return data


def today() -> date:
    return date.today()


def iso(d: date) -> str:
    return d.isoformat()


def parse_day(text: str | None) -> date | None:
    return date.fromisoformat(text) if text else None


# ---------------------------------------------------------------- lookups

def find_problem(ident: str) -> dict:
    ident = ident.strip().lower()
    for p in curriculum()["problems"]:
        if ident == p["slug"] or ident.lstrip("0") == p["id"].lstrip("0"):
            return p
    sys.exit(f"No problem matches '{ident}'. Try: python3 coach.py list")


def pattern_name(pattern_id: str) -> str:
    for pat in curriculum()["patterns"]:
        if pat["id"] == pattern_id:
            return pat["name"]
    return pattern_id


def pattern_file(pattern_id: str) -> str:
    for pat in curriculum()["patterns"]:
        if pat["id"] == pattern_id:
            return pat["file"]
    return ""


def folder_for(p: dict) -> Path:
    return PROBLEMS / f"{p['id']}-{p['slug']}"


def state_of(p: dict, prog=None) -> dict:
    prog = prog or progress()
    return prog["problems"].get(p["id"], {"status": "new"})


# ---------------------------------------------------------------- planning

def due_reviews(prog) -> list[dict]:
    """Problems whose review date is today or earlier, oldest first."""
    out = []
    for p in curriculum()["problems"]:
        st = prog["problems"].get(p["id"])
        if not st or st["status"] not in ("learning", "review"):
            continue
        due = parse_day(st.get("due"))
        if due and due <= today():
            out.append((due, p))
    out.sort(key=lambda pair: pair[0])
    return [p for _, p in out]


def in_progress(prog) -> list[dict]:
    return [p for p in curriculum()["problems"]
            if prog["problems"].get(p["id"], {}).get("started_at")
            and not prog["problems"][p["id"]].get("finished_today")]


def next_new(prog) -> dict | None:
    for p in curriculum()["problems"]:
        if p["id"] not in prog["problems"]:
            return p
    return None


def new_started_today(prog) -> int:
    return sum(1 for h in prog["history"]
               if h["day"] == iso(today()) and h["kind"] == "new")


def reviews_done_today(prog) -> int:
    return sum(1 for h in prog["history"]
               if h["day"] == iso(today()) and h["kind"] == "review")


def plan(prog) -> list[tuple[str, dict]]:
    """Return [(kind, problem)] for today. kind is 'continue', 'review' or 'new'."""
    active = in_progress(prog)
    if active:
        return [("continue", active[0])]

    items: list[tuple[str, dict]] = []
    reviews_left = MAX_REVIEWS_PER_DAY - reviews_done_today(prog)
    for p in due_reviews(prog)[:max(0, reviews_left)]:
        items.append(("review", p))
    if not items and new_started_today(prog) < MAX_NEW_PER_DAY:
        p = next_new(prog)
        if p:
            items.append(("new", p))
    return items


# ---------------------------------------------------------------- display

def banner(text: str) -> None:
    print("\n" + text)
    print("-" * len(text))


def describe(kind: str, p: dict, prog) -> None:
    st = state_of(p, prog)
    label = {"continue": "IN PROGRESS", "review": "REVIEW (re-solve from blank)",
             "new": "NEW"}[kind]
    print(f"[{label}]  {p['id']}  {p['title']}  ({p['difficulty']})")
    print(f"  pattern : {pattern_name(p['pattern'])}   ->  {pattern_file(p['pattern'])}")
    print(f"  folder  : problems/{p['id']}-{p['slug']}/")
    print(f"  leetcode: {p['url']}")
    if kind == "review":
        print(f"  last    : rated {st.get('last_rating')} on {st.get('last_done')}, "
              f"interval {st.get('interval')} days")
    if st.get("started_at"):
        print(f"  timer   : {elapsed_text(st['started_at'])} elapsed of {TIMEBOX_MINUTES} min")
    print(f"\n  start it:  python3 coach.py start {p['id']}")


def elapsed_text(started_iso: str) -> str:
    started = datetime.fromisoformat(started_iso)
    mins = int((datetime.now() - started).total_seconds() // 60)
    if mins >= TIMEBOX_MINUTES:
        return f"{mins} min  <-- past the {TIMEBOX_MINUTES} min bell. Wrap up, rate it, stop."
    return f"{mins} min"


# ---------------------------------------------------------------- commands

def cmd_next(_args) -> None:
    prog = progress()
    items = plan(prog)
    banner(f"Today: {iso(today())}   streak: {prog['streak']['count']} day(s)")
    if not items:
        print("Nothing due and today's new problem is done. You're finished for today.")
        print("Seriously. Stop. Tomorrow has its own problem.")
        return
    if len(items) == 1:
        print("One thing to do:\n")
    else:
        print(f"{len(items)} things today, in this order. Reviews first, they protect what you already learned.\n")
    for kind, p in items:
        describe(kind, p, prog)
        print()


def cmd_start(args) -> None:
    if not args:
        sys.exit("usage: python3 coach.py start <id>")
    p = find_problem(args[0])
    prog = progress()
    st = prog["problems"].setdefault(p["id"], {"status": "new"})
    folder = folder_for(p)

    kind = "new" if st["status"] == "new" else "review"
    if kind == "new" and new_started_today(prog) >= MAX_NEW_PER_DAY and not st.get("started_at"):
        print("You already started a new problem today. One new problem per day is the rule.")
        print("Do a review if one is due, or stop for today. This is the system working.")
        return

    if not folder.exists():
        scaffold(p, folder)
        print(f"Created problems/{folder.name}/ from the template.")
        print(f"Timer not started. Run `start {p['id']}` again once the folder is filled in.")
        return

    if kind == "review" and not st.get("started_at"):
        blanked = blank_solution(folder / "solution.py", p)
        if blanked:
            print("Archived your previous solution under attempts/ and blanked the function.")
            print("Re-solve it without looking. That is the whole point of a review.")

    if not st.get("started_at"):
        st["started_at"] = datetime.now().isoformat(timespec="seconds")
        st.pop("finished_today", None)
        if kind == "new":
            st["status"] = "learning"
            prog["history"].append({"day": iso(today()), "kind": "new", "id": p["id"], "event": "start"})
        save_json(PROGRESS, prog)

    banner(f"Started {p['id']} {p['title']}")
    print(f"Set a {TIMEBOX_MINUTES} minute timer on your phone right now. When it rings you stop,")
    print("solved or not. Partial work still counts and still gets rated.\n")
    print(f"  1. Read   problems/{folder.name}/PROBLEM.md  (just the top, not the hints)")
    print(f"  2. Skim   {pattern_file(p['pattern'])}  if the pattern is new to you")
    print(f"  3. Code   problems/{folder.name}/solution.py")
    print(f"  4. Test   python3 coach.py check {p['id']}")
    print(f"  5. Stuck for 5+ min?   python3 coach.py hint {p['id']} 1")
    print(f"  6. Done   python3 coach.py done {p['id']} <1|2|3>")


def scaffold(p: dict, folder: Path) -> None:
    folder.mkdir(parents=True)
    for name in ("PROBLEM.md", "solution.py", "NOTES.md"):
        text = (TEMPLATE / name).read_text()
        text = (text.replace("{{ID}}", p["id"])
                    .replace("{{TITLE}}", p["title"])
                    .replace("{{SLUG}}", p["slug"])
                    .replace("{{URL}}", p["url"])
                    .replace("{{DIFFICULTY}}", p["difficulty"])
                    .replace("{{PATTERN}}", pattern_name(p["pattern"]))
                    .replace("{{PATTERN_FILE}}", pattern_file(p["pattern"])))
        (folder / name).write_text(text)
    print("This folder is a bare template. Ask Claude to fill in PROBLEM.md, the")
    print("function stub and the tests before you start (see COACHING.md).")
    print(f"Sample to copy the format from: problems/001-two-sum/")


def blank_solution(path: Path, p: dict) -> bool:
    """Archive solution.py and replace the body of every Solution method with
    `raise NotImplementedError`. Returns False if nothing could be blanked."""
    if not path.exists():
        return False
    source = path.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    lines = source.splitlines(keepends=True)
    edits = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Solution":
            for fn in node.body:
                if isinstance(fn, ast.FunctionDef) and fn.body:
                    first, last = fn.body[0], fn.body[-1]
                    # keep a leading docstring if there is one
                    if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                            and isinstance(first.value.value, str) and len(fn.body) > 1):
                        first = fn.body[1]
                    indent = " " * first.col_offset
                    edits.append((first.lineno - 1, last.end_lineno,
                                  f"{indent}raise NotImplementedError  # re-solve from blank\n"))
    if not edits:
        return False
    attempts = path.parent / "attempts"
    attempts.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    shutil.copy(path, attempts / f"{stamp}-before-review.py")
    for start, end, replacement in sorted(edits, reverse=True):
        lines[start:end] = [replacement]
    path.write_text("".join(lines))
    return True


def cmd_check(args) -> None:
    if not args:
        sys.exit("usage: python3 coach.py check <id>")
    p = find_problem(args[0])
    folder = folder_for(p)
    solution = folder / "solution.py"
    if not solution.exists():
        sys.exit(f"No solution.py yet. Run: python3 coach.py start {p['id']}")
    st = state_of(p)
    if st.get("started_at"):
        print(f"timer: {elapsed_text(st['started_at'])}\n")
    result = subprocess.run([sys.executable, str(solution)])
    sys.exit(result.returncode)


def cmd_hint(args) -> None:
    if len(args) < 2:
        sys.exit("usage: python3 coach.py hint <id> <1|2|3>")
    p = find_problem(args[0])
    n = int(args[1])
    text = (folder_for(p) / "PROBLEM.md").read_text()
    hints = re.findall(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", text, re.S)
    if not hints:
        sys.exit("PROBLEM.md has no hints yet. Ask Claude for hint 1, not the answer.")
    if n < 1 or n > len(hints):
        sys.exit(f"Hints available: 1 to {len(hints)}")
    title, body = hints[n - 1]
    banner(title.strip())
    print(body.strip())
    if n < len(hints):
        print(f"\nStill stuck after 5 more minutes?  python3 coach.py hint {p['id']} {n + 1}")
    else:
        print("\nThat was the last hint. If it's still not clicking, rate it 1 and let the")
        print("review tomorrow do its job. Struggling then seeing it again is how it sticks.")


def cmd_done(args) -> None:
    if len(args) < 2 or args[1] not in ("1", "2", "3"):
        sys.exit("usage: python3 coach.py done <id> <1|2|3>\n"
                 "  1 = struggled or looked at the answer\n"
                 "  2 = solved it, needed hints\n"
                 "  3 = clean solve AND explained it back")
    p = find_problem(args[0])
    rating = int(args[1])
    prog = progress()
    st = prog["problems"].setdefault(p["id"], {"status": "learning"})
    was_review = st.get("reps", 0) > 0          # anything after the first attempt is a review
    kind = "review" if was_review else "new"

    interval = st.get("interval", 0)
    if rating == 1:
        interval = 1
        status = "learning"
    elif rating == 2:
        interval = max(FIRST_INTERVAL, interval) if interval else FIRST_INTERVAL
        status = "review"
    else:
        interval = FIRST_INTERVAL if interval < FIRST_INTERVAL else round(interval * GROWTH)
        status = "mastered" if interval > MASTERED_AT_INTERVAL and was_review else "review"

    due = today() + timedelta(days=interval)
    minutes = None
    if st.get("started_at"):
        minutes = int((datetime.now() - datetime.fromisoformat(st["started_at"])).total_seconds() // 60)

    st.update({"status": status, "interval": interval, "due": iso(due),
               "last_rating": rating, "last_done": iso(today()),
               "finished_today": True,
               "reps": st.get("reps", 0) + 1})
    st.pop("started_at", None)
    prog["history"].append({"day": iso(today()), "kind": kind, "id": p["id"],
                            "event": "done", "rating": rating, "minutes": minutes})
    bump_streak(prog)
    save_json(PROGRESS, prog)
    log_attempt(p, kind, rating, minutes)

    banner(f"Logged {p['id']} {p['title']}: rating {rating}")
    msg = {1: "Tomorrow you see it again. Struggle plus a retry is where memory forms.",
           2: f"Good. Back in {interval} days to prove it stuck.",
           3: f"Clean. Next review in {interval} days." if status != "mastered"
              else "Mastered. It leaves the review queue."}[rating]
    print(msg)
    if minutes is not None:
        print(f"Time on it: {minutes} min.")
    print(f"Streak: {prog['streak']['count']} day(s).")
    remaining = plan(prog)
    if remaining:
        print(f"\nStill on today's list: {len(remaining)}. Run: python3 coach.py next")
    else:
        print("\nThat's today. Close the laptop. Really.")


def log_attempt(p: dict, kind: str, rating: int, minutes) -> None:
    notes = folder_for(p) / "NOTES.md"
    if not notes.exists():
        return
    line = (f"| {iso(today())} | {kind} | {rating} | "
            f"{'' if minutes is None else minutes} |  |\n")
    text = notes.read_text()
    if "| date |" in text:
        notes.write_text(text.rstrip("\n") + "\n" + line)


def bump_streak(prog) -> None:
    streak = prog["streak"]
    last = parse_day(streak.get("last_day"))
    if last == today():
        return
    if last == today() - timedelta(days=1):
        streak["count"] += 1
    else:
        streak["count"] = 1
    streak["last_day"] = iso(today())


def cmd_status(_args) -> None:
    prog = progress()
    cur = curriculum()
    banner(f"Status  {iso(today())}   streak {prog['streak']['count']} day(s)")
    counts = {"new": 0, "learning": 0, "review": 0, "mastered": 0}
    for p in cur["problems"]:
        counts[state_of(p, prog)["status"]] += 1
    print("  " + "   ".join(f"{k}: {v}" for k, v in counts.items()))
    print(f"  due for review today: {len(due_reviews(prog))}\n")
    for pat in cur["patterns"]:
        ps = [p for p in cur["problems"] if p["pattern"] == pat["id"]]
        marks = ""
        for p in ps:
            s = state_of(p, prog)["status"]
            marks += {"new": ".", "learning": "o", "review": "O", "mastered": "#"}[s]
        print(f"  {pat['name']:<28} {marks}")
    print("\n  . not started   o learning   O in review rotation   # mastered")


def cmd_list(args) -> None:
    prog = progress()
    cur = curriculum()
    want = args[0] if args else None
    for pat in cur["patterns"]:
        if want and want not in (pat["id"], pat["name"].lower()):
            continue
        banner(f"{pat['name']}   ({pat['file']})")
        for p in cur["problems"]:
            if p["pattern"] != pat["id"]:
                continue
            st = state_of(p, prog)
            extra = "" if st["status"] == "new" else f"  [{st['status']}, due {st.get('due')}]"
            print(f"  {p['id']}  {p['title']:<52} {p['difficulty']:<7}{extra}")


COMMANDS = {"next": cmd_next, "start": cmd_start, "check": cmd_check, "hint": cmd_hint,
            "done": cmd_done, "status": cmd_status, "list": cmd_list}


def main(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help", "help"):
        if argv:
            print(__doc__)
            return
        cmd_next([])
        return
    cmd = COMMANDS.get(argv[0])
    if not cmd:
        sys.exit(f"Unknown command '{argv[0]}'.\n{__doc__}")
    cmd(argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
