#!/usr/bin/env python3
"""Stop hook: don't end a session with progress that never reached the phone page.

If progress.json or site/data.json has uncommitted changes, or there are
commits not yet pushed, exit 2 with a reason (Claude sees it and finishes the
job: commit and push). If this stop was already triggered by this hook
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
if payload.get("stop_hook_active"):
    sys.exit(0)

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
WATCHED = ["3. LeetCode/progress.json", "3. LeetCode/site/data.json"]


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=root, timeout=20)


try:
    dirty = [p for p in WATCHED if git("status", "--porcelain", "--", p).stdout.strip()]
    ahead = 0
    if git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}").returncode == 0:
        out = git("rev-list", "--count", "@{u}..HEAD").stdout.strip()
        ahead = int(out) if out.isdigit() else 0
except Exception:
    sys.exit(0)

if dirty or ahead:
    why = []
    if dirty:
        why.append("uncommitted study progress (" + ", ".join(dirty) + ")")
    if ahead:
        why.append(f"{ahead} commit(s) not pushed")
    print("Before stopping: " + " and ".join(why) + ". Run `python3 \"3. LeetCode/site/build.py\"`, commit, "
          "and push so the phone page shows today's work (COACHING.md step 7).", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
