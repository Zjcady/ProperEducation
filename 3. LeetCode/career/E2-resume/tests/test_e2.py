import json
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
COACH = LAB.parents[1] / "coach.py"


def test_step1_resume_generates_and_writes():
    out = subprocess.run([sys.executable, str(COACH), "resume"], capture_output=True, text=True, cwd=COACH.parent)
    assert out.returncode == 0 and "Numbers you can defend" in out.stdout
    assert (LAB / "RESUME.md").exists(), "run: python3 coach.py resume --write"
    data = json.loads((LAB / "bullets.json").read_text())
    assert "C3" in data and "_skills" in data


def test_step2_resume_edited_by_hand():
    text = (LAB / "RESUME.md").read_text()
    assert "generated" not in text.splitlines()[0].lower(), "replace the generator's first line with your headline"
    assert "Edit the wording; don't inflate" not in text, "delete the generator's intro sentence"
    bullets = [l for l in text.splitlines() if l.startswith("- ")]
    assert len(bullets) >= 4
    for b in bullets:
        assert len(b) <= 160, f"one line each: {b[:40]}..."
        assert "(none yet" not in b and "no bullet template" not in b
    assert "passionate" not in text.lower()
