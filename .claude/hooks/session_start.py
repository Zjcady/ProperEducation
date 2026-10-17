#!/usr/bin/env python3
"""SessionStart hook: put today's blocks in context before the first message.

Runs `coach.py next` and prints it. For SessionStart, stdout is added to
Claude's context, so the session already knows block 1 when the learner
says "leetcode". Never blocks: any failure exits 0 silently.
"""
import os
import subprocess
import sys
from pathlib import Path

root = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
coach = root / "3. LeetCode" / "coach.py"
try:
    out = subprocess.run([sys.executable, str(coach), "next"], capture_output=True, text=True,
                         cwd=coach.parent, timeout=30).stdout.strip()
except Exception:
    sys.exit(0)
if out:
    print("Today's study plan (from coach.py next, run by the SessionStart hook):\n" + out)
sys.exit(0)
