import json
import subprocess
import sys
from pathlib import Path

import pytest

LAB = Path(__file__).resolve().parents[1]
REPO = LAB.parents[2]                      # labs/C7 -> 3. LeetCode -> repo root
SKILL = REPO / ".claude" / "skills" / "leetcode" / "SKILL.md"
HOOK = REPO / ".claude" / "hooks" / "protect_solutions.py"
SETTINGS = REPO / ".claude" / "settings.json"


# ---------------------------------------------------------------- step 1

def test_step1_skill_exists_with_frontmatter():
    assert SKILL.exists(), f"write {SKILL.relative_to(REPO)}"
    text = SKILL.read_text()
    assert text.startswith("---\n")
    front = text.split("---")[1]
    assert "name: leetcode" in front
    assert "description:" in front and "_(you" not in front
    body = text.split("---", 2)[2]
    assert "COACHING.md" in body and "coach.py" in body
    assert "_(you" not in body
    assert len(body.strip().splitlines()) <= 30


# ---------------------------------------------------------------- step 2

def run_hook(tool_name, file_path):
    payload = json.dumps({"tool_name": tool_name, "tool_input": {"file_path": file_path}})
    return subprocess.run([sys.executable, str(HOOK)], input=payload, capture_output=True, text=True)


def test_step2_hook_blocks_learner_files():
    assert HOOK.exists(), f"write {HOOK.relative_to(REPO)}"
    for path in (str(REPO / "3. LeetCode/problems/001-two-sum/solution.py"),
                 str(REPO / "3. LeetCode/foundations/01-A01/challenge.py")):
        for tool in ("Edit", "Write"):
            r = run_hook(tool, path)
            assert r.returncode == 2, f"{tool} on {path} should be blocked"
            assert r.stderr.strip(), "say why on stderr"


def test_step2_hook_allows_an_untouched_template(tmp_path):
    stub = tmp_path / "problems" / "999-new" / "solution.py"
    stub.parent.mkdir(parents=True)
    stub.write_text("class Solution:\n    def TODO_METHOD_NAME(self, TODO_ARGS):\n        raise NotImplementedError\n")
    assert run_hook("Edit", str(stub)).returncode == 0, "a bare template may be filled in"
    stub.write_text("class Solution:\n    def twoSum(self, nums, target):\n        pass\n")
    assert run_hook("Edit", str(stub)).returncode == 2, "once started, it's the learner's"


def test_step2_hook_allows_everything_else():
    for path in (str(REPO / "3. LeetCode/problems/001-two-sum/NOTES.md"),
                 str(REPO / "3. LeetCode/coach.py"),
                 str(REPO / "3. LeetCode/labs/C1/ask.py")):
        assert run_hook("Edit", path).returncode == 0
    r = subprocess.run([sys.executable, str(HOOK)], input="{}", capture_output=True, text=True)
    assert r.returncode == 0, "a payload with no file_path must not block"


def test_step2_settings_register_the_hook():
    assert SETTINGS.exists()
    data = json.loads(SETTINGS.read_text())
    hooks = data.get("hooks", {})
    for kept in ("SessionStart", "PostToolUse", "Stop"):
        assert kept in hooks, f"the coach's {kept} hook went missing: add PreToolUse to the file, don't replace it"
    assert data.get("autoMemoryEnabled") is False, "keep autoMemoryEnabled: false"
    pre = hooks.get("PreToolUse")
    assert pre, 'add a "PreToolUse" entry under "hooks" (see starter/settings.json)'
    commands = [h["command"] for entry in pre for h in entry["hooks"]]
    assert any("protect_solutions.py" in c for c in commands)
    assert any("Edit" in entry["matcher"] for entry in pre)


def test_step2_writeup_is_filled_in():
    text = (LAB / "WRITEUP.md").read_text()
    assert "_(you)_" not in text
    assert len(text) > 900
