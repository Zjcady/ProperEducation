#!/usr/bin/env python3
"""Stop hook: don't let a finished study session end with its result unsaved.

Stop fires at the end of every turn, not just the session, so this only blocks
when something *finishing* happened and didn't reach the remote:
  - progress.json has new history entries that close work (done, checks,
    touch, mock done) compared with the last commit, or
  - commits touching progress.json haven't been pushed.
Starting a problem (just a timer) never blocks, so the coach can say "go" and
end the turn. If this stop was already triggered by this hook
(stop_hook_active), allow it, so it can never loop.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}
if isinstance(payload, dict) and payload.get("stop_hook_active"):
    sys.exit(0)

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
PROGRESS = "3. LeetCode/progress.json"
FINISHING = {"done", "checks", "touch"}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=root, timeout=20)


def finishing_events(history):
    return sum(1 for h in history if isinstance(h, dict) and h.get("event") in FINISHING)


try:
    reasons = []
    work = root / PROGRESS
    if work.exists():
        now = json.loads(work.read_text()).get("history", [])
        head = git("show", f"HEAD:{PROGRESS}")
        before = json.loads(head.stdout).get("history", []) if head.returncode == 0 else []
        if finishing_events(now) > finishing_events(before):
            reasons.append("finished study work isn't committed (progress.json)")
    unpushed = git("rev-list", "--count", "HEAD", "--not", "--remotes", "--", PROGRESS).stdout.strip()
    if unpushed.isdigit() and int(unpushed):
        reasons.append(f"{unpushed} commit(s) with study progress not pushed")
except Exception:
    sys.exit(0)

if reasons:
    print("Before stopping: " + " and ".join(reasons) + ". Run `python3 \"3. LeetCode/site/build.py\"`, "
          "commit progress.json, site/data.json and LEARNER.md, and push, so the phone page shows today's "
          "work (COACHING.md step 8).", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
