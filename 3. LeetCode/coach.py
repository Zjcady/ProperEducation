#!/usr/bin/env python3
"""coach.py - the study coach. Built for ADHD and leaky memory. Work-day shape.

The shape:
  * Blocks are 15 minutes. A LeetCode problem may take two (bell at 30).
  * The first thing you finish today counts for the streak. Everything after
    that is bonus and never becomes an obligation.
  * Floor: on a scattered day, 5 minutes of checks or a touch still counts.
  * One new LeetCode problem per day, max. Reviews come before new material.
    At most 2 reviews per day unless you ask for `more`. Missed days never
    pile up into a backlog.
  * Reviews are re-solves from a blank function. Reading old code is not a review.

Two tracks share the day:
  LeetCode block   problems 001..083 (ids are numbers or slugs)
  Build block      foundations chapters A01..A12, labs C1..C8, D1..D5

Commands:
  python3 coach.py                  same as `next`
  python3 coach.py next             today's blocks, in order
  python3 coach.py floor            the smallest thing that still counts today
  python3 coach.py start <id>       begin an item (creates folder, starts timer)
  python3 coach.py check <id>       run its tests, show elapsed time
  python3 coach.py hint <id> <n>    show hint n (1, 2, 3)
  python3 coach.py checks <id>      take a chapter's quick checks in the terminal
  python3 coach.py checks <id> 4/5  record a score you got on the phone page
  python3 coach.py done <id> [r]    finish. LeetCode needs r: 1 struggled, 2 hints, 3 clean
  python3 coach.py touch [note]     "I did 5 minutes." Counts for today.
  python3 coach.py more             unlock one extra review or build step today (hyperfocus)
  python3 coach.py skip <id>        mark a chapter as already known (placement)
  python3 coach.py status           streak, maps, what is due
  python3 coach.py list [track]     the curriculum
"""
from __future__ import annotations

import ast
import json
import random
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
CHAPTER_TEMPLATE = ROOT / "_chapter_template"

BLOCK_MINUTES = 15
LEETCODE_BELL_MINUTES = 30        # a problem may take two blocks
MAX_REVIEWS_PER_DAY = 2
MAX_NEW_PER_DAY = 1
MAX_BUILD_STEPS_PER_DAY = 1
BONUS_CAP = 2                     # `more` can be used this many times a day

# Spaced repetition for problems. Rating -> interval (days).
FIRST_INTERVAL = 3
GROWTH = 2.5
MASTERED_AT_INTERVAL = 30
# Checks (quizzes): imperfect -> 3 days, perfect -> one pass at 7 days, then cleared.
CHECKS_RETRY_DAYS = 3
CHECKS_CONFIRM_DAYS = 7

# Backwards-compatible alias used by older site/build.py
TIMEBOX_MINUTES = LEETCODE_BELL_MINUTES


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
    return load_json(CURRICULUM, {"patterns": [], "problems": [], "build": [], "tracks": []})


def progress():
    data = load_json(PROGRESS, {})
    data.setdefault("problems", {})
    data.setdefault("build", {})
    data.setdefault("streak", {"count": 0, "last_day": None})
    data.setdefault("history", [])
    data.setdefault("bonus", {"day": None, "count": 0})
    return data


def today() -> date:
    return date.today()


def iso(d: date) -> str:
    return d.isoformat()


def parse_day(text: str | None) -> date | None:
    return date.fromisoformat(text) if text else None


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------- lookups

def find_item(ident: str) -> tuple[str, dict]:
    """Return ("problem", p) or ("build", b)."""
    key = ident.strip().lower()
    cur = curriculum()
    for b in cur["build"]:
        if key == b["id"].lower():
            return "build", b
    for p in cur["problems"]:
        if key == p["slug"] or (key.isdigit() and key.lstrip("0") == p["id"].lstrip("0")):
            return "problem", p
    sys.exit(f"Nothing matches '{ident}'. Try: python3 coach.py list")


def find_problem(ident: str) -> dict:
    kind, item = find_item(ident)
    if kind != "problem":
        sys.exit(f"'{ident}' is a build item, not a LeetCode problem.")
    return item


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


def track_name(track_id: str) -> str:
    for t in curriculum().get("tracks", []):
        if t["id"] == track_id:
            return t["name"]
    return track_id


def folder_for(p: dict) -> Path:
    return PROBLEMS / f"{p['id']}-{p['slug']}"


def build_folder(b: dict) -> Path:
    return ROOT / b["folder"]


def state_of(p: dict, prog=None) -> dict:
    prog = prog or progress()
    return prog["problems"].get(p["id"], {"status": "new"})


def build_state(b: dict, prog=None) -> dict:
    prog = prog or progress()
    return prog["build"].get(b["id"], {"status": "new", "step": 0})


def is_scaffolded(kind: str, item: dict) -> bool:
    if kind == "problem":
        sol = folder_for(item) / "solution.py"
        return sol.exists() and "TODO_METHOD_NAME" not in sol.read_text()
    folder = build_folder(item)
    if item["kind"] == "chapter":
        read = folder / "read.md"
        return read.exists() and "{{" not in read.read_text() and "_(Claude fills" not in read.read_text()
    return (folder / "README.md").exists()


# ---------------------------------------------------------------- today

def events_today(prog, *kinds) -> list[dict]:
    return [h for h in prog["history"] if h["day"] == iso(today()) and (not kinds or h["kind"] in kinds)]


def counted_today(prog) -> bool:
    return any(h.get("event") in ("done", "checks", "touch") for h in events_today(prog))


def bonus_today(prog) -> int:
    b = prog["bonus"]
    return b["count"] if b.get("day") == iso(today()) else 0


def due_reviews(prog) -> list[dict]:
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


def problem_in_progress(prog) -> dict | None:
    for p in curriculum()["problems"]:
        st = prog["problems"].get(p["id"], {})
        if st.get("started_at") and not st.get("finished_today"):
            return p
    return None


def next_new_problem(prog) -> dict | None:
    for p in curriculum()["problems"]:
        if p["id"] not in prog["problems"]:
            return p
    return None


def new_started_today(prog) -> int:
    return len([h for h in events_today(prog, "new") if h.get("event") == "start"])


def reviews_done_today(prog) -> int:
    return len([h for h in events_today(prog, "review") if h.get("event") == "done"])


def build_steps_today(prog) -> int:
    return len([h for h in events_today(prog, "build") if h.get("event") == "done"])


def build_in_progress(prog) -> dict | None:
    for b in curriculum()["build"]:
        st = prog["build"].get(b["id"], {})
        if st.get("started_at"):
            return b
    return None


def next_build(prog) -> dict | None:
    for b in curriculum()["build"]:
        st = prog["build"].get(b["id"], {"status": "new"})
        if st["status"] in ("new", "in_progress"):
            return b
    return None


def checks_due(prog) -> list[dict]:
    out = []
    for b in curriculum()["build"]:
        st = prog["build"].get(b["id"], {})
        due = parse_day(st.get("checks_due"))
        if due and due <= today():
            out.append(b)
    return out


def plan(prog) -> list[dict]:
    """Today's blocks in order. Each: {"kind", "type": "problem"|"build", "item"}."""
    items: list[dict] = []
    bonus = bonus_today(prog)

    # LeetCode block
    active = problem_in_progress(prog)
    if active:
        items.append({"kind": "continue", "type": "problem", "item": active})
    else:
        reviews_left = MAX_REVIEWS_PER_DAY + bonus - reviews_done_today(prog)
        for p in due_reviews(prog)[:max(0, reviews_left)]:
            items.append({"kind": "review", "type": "problem", "item": p})
        if not items and new_started_today(prog) < MAX_NEW_PER_DAY:
            p = next_new_problem(prog)
            if p:
                items.append({"kind": "new", "type": "problem", "item": p})

    # Build block
    active_b = build_in_progress(prog)
    if active_b:
        items.append({"kind": "continue", "type": "build", "item": active_b})
    elif build_steps_today(prog) < MAX_BUILD_STEPS_PER_DAY + bonus:
        b = next_build(prog)
        if b:
            items.append({"kind": "build", "type": "build", "item": b})

    # Checks reviews (the 5-minute items)
    for b in checks_due(prog):
        items.append({"kind": "checks", "type": "build", "item": b})
    return items


# ---------------------------------------------------------------- display

def banner(text: str) -> None:
    print("\n" + text)
    print("-" * len(text))


def elapsed_minutes(started_iso: str) -> int:
    return int((datetime.now() - datetime.fromisoformat(started_iso)).total_seconds() // 60)


def timer_text(started_iso: str, bell: int) -> str:
    mins = elapsed_minutes(started_iso)
    if mins >= bell:
        return f"{mins} min  <-- past the {bell} min bell. Wrap up, rate it, stop."
    return f"{mins} min of {bell}"


def describe(entry: dict, prog) -> None:
    kind, item = entry["kind"], entry["item"]
    if entry["type"] == "problem":
        st = state_of(item, prog)
        label = {"continue": "IN PROGRESS", "review": "REVIEW (re-solve from blank)", "new": "NEW"}[kind]
        print(f"[{label}]  {item['id']}  {item['title']}  ({item['difficulty']})")
        print(f"  pattern : {pattern_name(item['pattern'])}   ->  {pattern_file(item['pattern'])}")
        print(f"  folder  : problems/{item['id']}-{item['slug']}/")
        print(f"  leetcode: {item['url']}")
        if kind == "review":
            print(f"  last    : rated {st.get('last_rating')} on {st.get('last_done')}, interval {st.get('interval')} days")
        if st.get("started_at"):
            print(f"  timer   : {timer_text(st['started_at'], LEETCODE_BELL_MINUTES)}")
        print(f"  start it:  python3 coach.py start {item['id']}")
    else:
        st = build_state(item, prog)
        if kind == "checks":
            print(f"[CHECKS REVIEW · 5 min]  {item['id']}  {item['title']}")
            print(f"  last score: {st.get('checks_score')}  ->  python3 coach.py checks {item['id']}")
            return
        label = "IN PROGRESS" if kind == "continue" else ("CHAPTER" if item["kind"] == "chapter" else "LAB")
        step = f"  step {st.get('step', 0) + 1} of {item['steps']}" if item["steps"] > 1 else ""
        print(f"[{label}]  {item['id']}  {item['title']}{step}")
        print(f"  track   : {track_name(item['track'])}")
        print(f"  folder  : {item['folder']}/")
        if st.get("started_at"):
            print(f"  timer   : {timer_text(st['started_at'], BLOCK_MINUTES)}")
        if not is_scaffolded("build", item):
            print("  note    : folder not filled in yet. Open a Claude session and say \"leetcode\".")
        print(f"  start it:  python3 coach.py start {item['id']}")


# ---------------------------------------------------------------- commands

def cmd_next(_args) -> None:
    prog = progress()
    items = plan(prog)
    banner(f"Today: {iso(today())}   streak: {prog['streak']['count']} day(s)")
    if counted_today(prog):
        print("Today already counts. Everything below is bonus. Stopping is a fine choice.\n")
    if not items:
        print("Nothing left today. You're finished. Tomorrow has its own.")
        return
    for i, entry in enumerate(items, 1):
        tag = "counts for today" if (i == 1 and not counted_today(prog)) else "bonus"
        mins = (f"{BLOCK_MINUTES}, up to {LEETCODE_BELL_MINUTES}" if entry["type"] == "problem"
                else "5" if entry["kind"] == "checks" else str(BLOCK_MINUTES))
        print(f"Block {i} · {mins} min · {tag}")
        describe(entry, prog)
        print()
    print("Bad day?   python3 coach.py floor      (5 minutes still counts)")
    if bonus_today(prog) < BONUS_CAP:
        print("On fire?   python3 coach.py more       (one more review or build step, never a 2nd new problem)")


def cmd_floor(_args) -> None:
    prog = progress()
    banner("The floor: smallest thing that still counts")
    due = checks_due(prog)
    if due:
        b = due[0]
        print(f"Checks review for {b['id']} {b['title']}  (about 5 min)")
        print(f"  python3 coach.py checks {b['id']}")
        return
    cur_b = next_build(prog)
    if cur_b and cur_b["kind"] == "chapter" and is_scaffolded("build", cur_b) \
            and not prog["build"].get(cur_b["id"], {}).get("checks_score"):
        print(f"Take the checks for {cur_b['id']} {cur_b['title']}. Read the 5-minute read.md first if you haven't.")
        print(f"  python3 coach.py checks {cur_b['id']}")
        return
    taken = [b for b in curriculum()["build"] if prog["build"].get(b["id"], {}).get("checks_score")]
    if taken:
        b = random.choice(taken)
        print(f"Retake the checks for {b['id']} {b['title']}. Retrieval practice, 5 min.")
        print(f"  python3 coach.py checks {b['id']}")
        return
    items = plan(prog)
    prob = next((e for e in items if e["type"] == "problem"), None)
    if prob:
        p = prob["item"]
        print(f"Read {pattern_file(p['pattern'])} (2 minutes), then say the pattern's 'move' out loud.")
        print(f"  python3 coach.py touch \"read {pattern_name(p['pattern'])}\"")
    else:
        print("Open NOTES.md of your last solved problem and answer its three explain-it-back questions again.")
        print("  python3 coach.py touch \"explain-back\"")


def cmd_touch(args) -> None:
    prog = progress()
    note = " ".join(args) if args else "5 minutes"
    prog["history"].append({"day": iso(today()), "kind": "touch", "event": "touch", "note": note})
    bump_streak(prog)
    save_json(PROGRESS, prog)
    print(f"Logged: {note}. Today counts. Streak: {prog['streak']['count']} day(s).")


def cmd_more(_args) -> None:
    prog = progress()
    b = prog["bonus"]
    if b.get("day") != iso(today()):
        b["day"], b["count"] = iso(today()), 0
    if b["count"] >= BONUS_CAP:
        print(f"You've unlocked {BONUS_CAP} extras today already. That's the cap on purpose. Tomorrow's bar stays where it is.")
        return
    b["count"] += 1
    save_json(PROGRESS, prog)
    print(f"Unlocked: one more review and one more build step today ({b['count']}/{BONUS_CAP}). Never a second new problem.")
    cmd_next([])


def cmd_start(args) -> None:
    if not args:
        sys.exit("usage: python3 coach.py start <id>")
    kind, item = find_item(args[0])
    if kind == "build":
        return start_build(item)
    p = item
    prog = progress()
    st = prog["problems"].setdefault(p["id"], {"status": "new"})
    folder = folder_for(p)

    first_time = st["status"] == "new"
    if first_time and new_started_today(prog) >= MAX_NEW_PER_DAY and not st.get("started_at"):
        print("You already started a new problem today. One new problem per day is the rule.")
        print("Do a review if one is due, a build step, or stop. This is the system working.")
        return

    if not folder.exists():
        scaffold_problem(p, folder)
        print(f"Created problems/{folder.name}/ from the template.")
        print(f"Timer not started. Run `start {p['id']}` again once the folder is filled in.")
        return

    if not first_time and not st.get("started_at"):
        if blank_solution(folder / "solution.py"):
            print("Archived your previous solution under attempts/ and blanked the function.")
            print("Re-solve it without looking. That is the whole point of a review.")

    if not st.get("started_at"):
        st["started_at"] = now_iso()
        st.pop("finished_today", None)
        if first_time:
            st["status"] = "learning"
            prog["history"].append({"day": iso(today()), "kind": "new", "id": p["id"], "event": "start"})
        save_json(PROGRESS, prog)

    banner(f"Started {p['id']} {p['title']}")
    print(f"Set a {BLOCK_MINUTES} minute timer. If it rings mid-thought, one more block is allowed.")
    print(f"At {LEETCODE_BELL_MINUTES} minutes you stop, solved or not. Partial work gets rated too.\n")
    print(f"  1. Read   problems/{folder.name}/PROBLEM.md  (top part, not the hints)")
    print(f"  2. Skim   {pattern_file(p['pattern'])}  if the pattern is new to you")
    print(f"  3. Code   problems/{folder.name}/solution.py")
    print(f"  4. Test   python3 coach.py check {p['id']}")
    print(f"  5. Stuck for 5+ min?   python3 coach.py hint {p['id']} 1")
    print(f"  6. Done   python3 coach.py done {p['id']} <1|2|3>")


def start_build(b: dict) -> None:
    prog = progress()
    st = prog["build"].setdefault(b["id"], {"status": "new", "step": 0})
    folder = build_folder(b)
    if not folder.exists():
        if b["kind"] == "chapter":
            scaffold_chapter(b, folder)
            print(f"Created {b['folder']}/ from the chapter template.")
        else:
            folder.mkdir(parents=True)
            (folder / "README.md").write_text(f"# {b['id']} · {b['title']}\n\n_(Lab not written yet. Ask Claude to build it per ROADMAP.md.)_\n")
            print(f"Created {b['folder']}/ placeholder.")
        print(f"Timer not started. Run `start {b['id']}` again once it's filled in.")
        return
    if not st.get("started_at") and build_steps_today(prog) >= MAX_BUILD_STEPS_PER_DAY + bonus_today(prog):
        print("You've done today's build step. Run `more` if you genuinely want another, or stop.")
        return
    if not st.get("started_at"):
        st["started_at"] = now_iso()
        st["status"] = "in_progress"
        save_json(PROGRESS, prog)
    banner(f"Started {b['id']} {b['title']}")
    print(f"Set a {BLOCK_MINUTES} minute timer. Stop at the bell, mark what you finished.\n")
    if b["kind"] == "chapter":
        print(f"  1. Read    {b['folder']}/read.md          (5 min, one idea)")
        print(f"  2. Checks  python3 coach.py checks {b['id']}    (5 min, quick questions)")
        print(f"  3. Build   {b['folder']}/challenge.py     (code; tests inside)")
        print(f"  4. Test    python3 coach.py check {b['id']}")
        print(f"  5. Stuck?  python3 coach.py hint {b['id']} 1")
        print(f"  6. Done    python3 coach.py done {b['id']}")
    else:
        print(f"  1. Read    {b['folder']}/README.md   step {st.get('step', 0) + 1} of {b['steps']}")
        print(f"  2. Build   follow that step. Ask Claude to review against RUBRIC.md.")
        print(f"  3. Done    python3 coach.py done {b['id']}    (advances one step)")


def scaffold_problem(p: dict, folder: Path) -> None:
    folder.mkdir(parents=True)
    for name in ("PROBLEM.md", "solution.py", "NOTES.md"):
        text = (TEMPLATE / name).read_text()
        text = (text.replace("{{ID}}", p["id"]).replace("{{TITLE}}", p["title"]).replace("{{SLUG}}", p["slug"])
                    .replace("{{URL}}", p["url"]).replace("{{DIFFICULTY}}", p["difficulty"])
                    .replace("{{PATTERN}}", pattern_name(p["pattern"])).replace("{{PATTERN_FILE}}", pattern_file(p["pattern"])))
        (folder / name).write_text(text)
    print("This folder is a bare template. Ask Claude to fill in PROBLEM.md, the")
    print("function stub and the tests before you start (see COACHING.md).")
    print("Sample to copy the format from: problems/001-two-sum/")


def scaffold_chapter(b: dict, folder: Path) -> None:
    folder.mkdir(parents=True)
    for name in ("read.md", "checks.json", "CHALLENGE.md", "challenge.py", "NOTES.md"):
        text = (CHAPTER_TEMPLATE / name).read_text()
        text = text.replace("{{ID}}", b["id"]).replace("{{TITLE}}", b["title"]).replace("{{FOLDER}}", b["folder"])
        (folder / name).write_text(text)
    print("This chapter is a bare template. Ask Claude to write read.md, checks.json,")
    print("CHALLENGE.md and challenge.py. Sample: foundations/01-A01/")


def blank_solution(path: Path) -> bool:
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
    shutil.copy(path, attempts / f"{datetime.now().strftime('%Y-%m-%d')}-before-review.py")
    for start, end, replacement in sorted(edits, reverse=True):
        lines[start:end] = [replacement]
    path.write_text("".join(lines))
    return True


def cmd_check(args) -> None:
    if not args:
        sys.exit("usage: python3 coach.py check <id>")
    kind, item = find_item(args[0])
    if kind == "problem":
        script, st, bell = folder_for(item) / "solution.py", state_of(item), LEETCODE_BELL_MINUTES
    else:
        script, st, bell = build_folder(item) / "challenge.py", build_state(item), BLOCK_MINUTES
    if not script.exists():
        sys.exit(f"No {script.name} yet. Run: python3 coach.py start {item['id']}")
    if st.get("started_at"):
        print(f"timer: {timer_text(st['started_at'], bell)}\n")
    sys.exit(subprocess.run([sys.executable, str(script)]).returncode)


def cmd_hint(args) -> None:
    if len(args) < 2:
        sys.exit("usage: python3 coach.py hint <id> <1|2|3>")
    kind, item = find_item(args[0])
    n = int(args[1])
    md = (folder_for(item) / "PROBLEM.md") if kind == "problem" else (build_folder(item) / "CHALLENGE.md")
    if not md.exists():
        sys.exit("No hints file yet.")
    hints = re.findall(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", md.read_text(), re.S)
    if not hints:
        sys.exit("No hints written yet. Ask Claude for hint 1, not the answer.")
    if n < 1 or n > len(hints):
        sys.exit(f"Hints available: 1 to {len(hints)}")
    title, body = hints[n - 1]
    banner(title.strip())
    print(body.strip())
    if n < len(hints):
        print(f"\nStill stuck after 5 more minutes?  python3 coach.py hint {item['id']} {n + 1}")
    else:
        print("\nThat was the last hint. If it's still not clicking, rate it 1 and let the")
        print("review do its job. Struggling then seeing it again is how it sticks.")


def cmd_checks(args) -> None:
    if not args:
        sys.exit("usage: python3 coach.py checks <chapter-id> [score/total]")
    kind, b = find_item(args[0])
    if kind != "build" or b["kind"] != "chapter":
        sys.exit("Checks exist for foundations chapters (A01..A12).")
    path = build_folder(b) / "checks.json"
    if not path.exists():
        sys.exit(f"No checks.json in {b['folder']}/ yet.")
    questions = load_json(path, {}).get("questions", [])
    if not questions or "{{" in path.read_text():
        sys.exit("Checks not written yet. Ask Claude.")

    if len(args) > 1 and "/" in args[1]:
        score, total = (int(x) for x in args[1].split("/"))
        wrong = []
    else:
        score, total, wrong = run_quiz(questions)

    prog = progress()
    st = prog["build"].setdefault(b["id"], {"status": "new", "step": 0})
    perfect = score == total
    if perfect and st.get("checks_score") and st["checks_score"].endswith(f"/{total}") \
            and st["checks_score"].startswith(f"{total}/"):
        st["checks_due"] = None                   # second perfect pass: cleared
        verdict = "Perfect twice. These checks leave the rotation."
    elif perfect:
        st["checks_due"] = iso(today() + timedelta(days=CHECKS_CONFIRM_DAYS))
        verdict = f"Perfect. One confirmation pass in {CHECKS_CONFIRM_DAYS} days, then they're cleared."
    else:
        st["checks_due"] = iso(today() + timedelta(days=CHECKS_RETRY_DAYS))
        verdict = f"{total - score} to revisit. They come back in {CHECKS_RETRY_DAYS} days. Missing once is how it sticks."
    st["checks_score"] = f"{score}/{total}"
    st["checks_wrong"] = wrong
    st["checks_last"] = iso(today())
    prog["history"].append({"day": iso(today()), "kind": "checks", "id": b["id"], "event": "checks",
                            "score": score, "total": total})
    bump_streak(prog)
    save_json(PROGRESS, prog)
    banner(f"Checks {b['id']}: {score}/{total}")
    print(verdict)
    print(f"Today counts. Streak: {prog['streak']['count']} day(s).")


def run_quiz(questions: list[dict]) -> tuple[int, int, list[int]]:
    score, wrong = 0, []
    print("\nQuick checks. Answer with a number for choices, or type the answer. Enter to skip.\n")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q['q']}")
        if q.get("type", "choice") == "choice":
            for j, opt in enumerate(q["options"], 1):
                print(f"   {j}) {opt}")
            raw = input("   > ").strip()
            ok = raw.isdigit() and int(raw) - 1 == q["answer"]
            correct_text = q["options"][q["answer"]]
        else:
            raw = input("   > ").strip()
            accepted = [a.strip().lower() for a in q["answers"]]
            ok = raw.lower() in accepted
            correct_text = q["answers"][0]
        if ok:
            score += 1
            print("   Right.", q.get("why", ""), "\n")
        else:
            wrong.append(i - 1)
            print(f"   Not quite. Answer: {correct_text}. {q.get('why', '')}\n")
    return score, len(questions), wrong


def cmd_done(args) -> None:
    if not args:
        sys.exit("usage: python3 coach.py done <id> [1|2|3]")
    kind, item = find_item(args[0])
    if kind == "build":
        return done_build(item)
    if len(args) < 2 or args[1] not in ("1", "2", "3"):
        sys.exit("usage: python3 coach.py done <problem-id> <1|2|3>\n"
                 "  1 = struggled or looked at the answer\n"
                 "  2 = solved it, needed hints\n"
                 "  3 = clean solve AND explained it back")
    p, rating = item, int(args[1])
    prog = progress()
    st = prog["problems"].setdefault(p["id"], {"status": "learning"})
    was_review = st.get("reps", 0) > 0
    hist_kind = "review" if was_review else "new"

    interval = st.get("interval", 0)
    if rating == 1:
        interval, status = 1, "learning"
    elif rating == 2:
        interval, status = (max(FIRST_INTERVAL, interval) if interval else FIRST_INTERVAL), "review"
    else:
        interval = FIRST_INTERVAL if interval < FIRST_INTERVAL else round(interval * GROWTH)
        status = "mastered" if interval > MASTERED_AT_INTERVAL and was_review else "review"

    minutes = elapsed_minutes(st["started_at"]) if st.get("started_at") else None
    st.update({"status": status, "interval": interval, "due": iso(today() + timedelta(days=interval)),
               "last_rating": rating, "last_done": iso(today()), "finished_today": True,
               "reps": st.get("reps", 0) + 1})
    st.pop("started_at", None)
    prog["history"].append({"day": iso(today()), "kind": hist_kind, "id": p["id"], "event": "done",
                            "rating": rating, "minutes": minutes})
    bump_streak(prog)
    save_json(PROGRESS, prog)
    log_attempt(folder_for(p) / "NOTES.md", hist_kind, rating, minutes)

    banner(f"Logged {p['id']} {p['title']}: rating {rating}")
    print({1: "Tomorrow you see it again. Struggle plus a retry is where memory forms.",
           2: f"Good. Back in {interval} days to prove it stuck.",
           3: ("Mastered. It leaves the review queue." if status == "mastered"
               else f"Clean. Next review in {interval} days.")}[rating])
    if minutes is not None:
        print(f"Time on it: {minutes} min.")
    wrap_up(prog)


def done_build(b: dict) -> None:
    prog = progress()
    st = prog["build"].setdefault(b["id"], {"status": "new", "step": 0})
    minutes = elapsed_minutes(st["started_at"]) if st.get("started_at") else None
    st["step"] = st.get("step", 0) + 1
    finished = st["step"] >= b["steps"]
    st["status"] = "done" if finished else "in_progress"
    st.pop("started_at", None)
    st["last_done"] = iso(today())
    prog["history"].append({"day": iso(today()), "kind": "build", "id": b["id"], "event": "done",
                            "step": st["step"], "minutes": minutes})
    bump_streak(prog)
    save_json(PROGRESS, prog)
    log_attempt(build_folder(b) / "NOTES.md", "build", st["step"], minutes)
    banner(f"Logged {b['id']} {b['title']}: " + ("finished" if finished else f"step {st['step']} of {b['steps']}"))
    if b["kind"] == "chapter" and not st.get("checks_score"):
        print(f"You haven't taken its checks. Five minutes: python3 coach.py checks {b['id']}")
    wrap_up(prog)


def wrap_up(prog) -> None:
    print(f"Streak: {prog['streak']['count']} day(s).")
    remaining = plan(prog)
    if remaining:
        print(f"\nBonus available ({len(remaining)}): python3 coach.py next    Stopping is also correct.")
    else:
        print("\nThat's today. Close it. Really.")


def cmd_skip(args) -> None:
    if not args:
        sys.exit("usage: python3 coach.py skip <chapter-id>")
    kind, item = find_item(args[0])
    if kind != "build":
        sys.exit("Skipping is for build items (placement). LeetCode problems don't get skipped; they get rated.")
    prog = progress()
    st = prog["build"].setdefault(item["id"], {"status": "new", "step": 0})
    st.update({"status": "skipped", "step": item["steps"]})
    st.pop("started_at", None)
    save_json(PROGRESS, prog)
    print(f"Skipped {item['id']} {item['title']} as already known. Its checks can still be taken any time.")


def log_attempt(notes: Path, kind: str, rating, minutes) -> None:
    if not notes.exists():
        return
    text = notes.read_text()
    if "| date |" in text:
        notes.write_text(text.rstrip("\n") + f"\n| {iso(today())} | {kind} | {rating} | {'' if minutes is None else minutes} |  |\n")


def bump_streak(prog) -> None:
    streak = prog["streak"]
    last = parse_day(streak.get("last_day"))
    if last == today():
        return
    streak["count"] = streak["count"] + 1 if last == today() - timedelta(days=1) else 1
    streak["last_day"] = iso(today())


MARK = {"new": ".", "learning": "o", "review": "O", "mastered": "#",
        "in_progress": "o", "done": "#", "skipped": "-"}


def cmd_status(_args) -> None:
    prog = progress()
    cur = curriculum()
    banner(f"Status  {iso(today())}   streak {prog['streak']['count']} day(s)" +
           ("   today counts" if counted_today(prog) else ""))
    counts = {"new": 0, "learning": 0, "review": 0, "mastered": 0}
    for p in cur["problems"]:
        counts[state_of(p, prog)["status"]] += 1
    print("  LeetCode  " + "   ".join(f"{k}: {v}" for k, v in counts.items()) +
          f"   due today: {len(due_reviews(prog))}")
    for pat in cur["patterns"]:
        marks = "".join(MARK[state_of(p, prog)["status"]] for p in cur["problems"] if p["pattern"] == pat["id"])
        print(f"    {pat['name']:<28} {marks}")
    print()
    for t in cur["tracks"]:
        if t["id"] == "leetcode":
            continue
        marks = "".join(MARK[build_state(b, prog)["status"]] for b in cur["build"] if b["track"] == t["id"])
        if marks:
            print(f"  {t['name']:<30} {marks}")
    due = checks_due(prog)
    if due:
        print(f"\n  checks due: {', '.join(b['id'] for b in due)}")
    print("\n  . not started   o in progress / learning   O in review rotation   # done / mastered   - skipped")


def cmd_list(args) -> None:
    prog = progress()
    cur = curriculum()
    want = args[0].lower() if args else None
    if want in (None, "leetcode"):
        for pat in cur["patterns"]:
            banner(f"{pat['name']}   ({pat['file']})")
            for p in cur["problems"]:
                if p["pattern"] != pat["id"]:
                    continue
                st = state_of(p, prog)
                extra = "" if st["status"] == "new" else f"  [{st['status']}, due {st.get('due')}]"
                print(f"  {p['id']}  {p['title']:<52} {p['difficulty']:<7}{extra}")
    for t in cur["tracks"]:
        if t["id"] == "leetcode" or (want and want not in (t["id"], t["name"].lower())):
            continue
        banner(t["name"])
        for b in cur["build"]:
            if b["track"] != t["id"]:
                continue
            st = build_state(b, prog)
            extra = "" if st["status"] == "new" else f"  [{st['status']}, step {st.get('step', 0)}/{b['steps']}]"
            print(f"  {b['id']:<4} {b['title']:<52} {b['kind']:<8}{extra}")


COMMANDS = {"next": cmd_next, "floor": cmd_floor, "start": cmd_start, "check": cmd_check, "hint": cmd_hint,
            "checks": cmd_checks, "done": cmd_done, "touch": cmd_touch, "more": cmd_more, "skip": cmd_skip,
            "status": cmd_status, "list": cmd_list}


def main(argv: list[str]) -> None:
    if not argv:
        return cmd_next([])
    if argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return
    cmd = COMMANDS.get(argv[0])
    if not cmd:
        sys.exit(f"Unknown command '{argv[0]}'.\n{__doc__}")
    cmd(argv[1:])


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except BrokenPipeError:            # e.g. `coach.py next | head`
        sys.exit(0)
