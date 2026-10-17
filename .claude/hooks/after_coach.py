#!/usr/bin/env python3
"""PostToolUse hook (Bash): rebuild the phone page whenever progress changed.

Reads the hook payload on stdin. If the command was a coach.py subcommand that
writes progress.json, runs site/build.py so site/data.json is never stale.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

WRITES = re.compile(r"coach\.py\s+(done|checks|touch|more|skip|add|mock\s+done)\b")

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)
command = (payload.get("tool_input") or {}).get("command", "")
if not WRITES.search(command):
    sys.exit(0)
root = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2]))
build = root / "3. LeetCode" / "site" / "build.py"
try:
    subprocess.run([sys.executable, str(build)], capture_output=True, text=True, cwd=build.parent.parent, timeout=60)
except Exception:
    pass
sys.exit(0)
