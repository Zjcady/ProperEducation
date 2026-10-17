import re
from pathlib import Path

TEXT = (Path(__file__).resolve().parents[1] / "TALKS.md").read_text()
BEATS = ("The problem", "The shape, drawn", "The key decision", "What changes at 10x", "Questions I expect")


def talk(n):
    parts = re.split(r"^## Talk \d+", TEXT, flags=re.M)[1:]
    return parts[n - 1]


def check_talk(n):
    t = talk(n)
    for beat in BEATS:
        m = re.search(rf"### {re.escape(beat)}.*?\n(.*?)(?=\n### |\Z)", t, re.S)
        body = m.group(1) if m else ""
        assert "_(you" not in body and len(body.split()) >= 30, f"talk {n}: write the '{beat}' beat"
    log = t.split("### Rehearsal log")[1]
    rows = [l for l in log.splitlines() if l.startswith("|") and not l.startswith("| date") and not set(l) <= set("|- ")]
    assert rows, f"talk {n}: log at least one rehearsal"
    cells = [c.strip() for c in rows[-1].strip("|").split("|")]
    assert float(cells[1]) <= 12, "ten minutes, give or take"


def test_step1_talk_one_written_and_rehearsed():
    check_talk(1)


def test_step2_talk_two_written_and_rehearsed():
    check_talk(2)
