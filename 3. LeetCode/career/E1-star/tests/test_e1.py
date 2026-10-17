import re
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
TEXT = (LAB / "STORIES.md").read_text()


def stories():
    parts = re.split(r"^## Story \d+", TEXT, flags=re.M)[1:]
    out = []
    for part in parts:
        part = part.split("## Rehearsal log")[0]
        sections = {}
        for name in ("Situation", "Task", "Action", "Result"):
            m = re.search(rf"### {name}\n(.*?)(?=\n### |\Z)", part, re.S)
            sections[name] = (m.group(1).strip() if m else "")
        rehearse = re.search(r"rehearse:\s*(\S+)", part)
        out.append({"rehearse": (rehearse.group(1).lower() if rehearse else ""), **sections})
    return out


def words(text):
    return 0 if "_(you)_" in text else len(text.split())


def test_step1_situation_and_task_written_for_all_six():
    s = stories()
    assert len(s) == 6
    for story in s:
        assert words(story["Situation"]) >= 15, "two sentences of Situation per story"
        assert words(story["Task"]) >= 10, "two sentences of Task per story"


def test_step1_three_stories_marked_for_rehearsal():
    s = stories()
    assert sum(1 for st in s if st["rehearse"] == "yes") == 3
    assert s[5]["rehearse"] == "yes", "Story 6 (why defense, why this company) is always one of the three"


def test_step2_action_and_result_written_for_the_three():
    chosen = [st for st in stories() if st["rehearse"] == "yes"]
    assert len(chosen) == 3
    for st in chosen:
        assert words(st["Action"]) >= 60, "Action is the longest part"
        assert words(st["Result"]) >= 25
        assert re.search(r"\d", st["Result"]), "a number in every Result"


def test_step3_rehearsal_log_has_three_rows():
    log = TEXT.split("## Rehearsal log")[1]
    rows = [l for l in log.splitlines() if l.startswith("|") and not l.startswith("| date") and not set(l) <= set("|- ")]
    assert len(rows) >= 3
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        assert len(cells) >= 7 and cells[3].isdigit() and int(cells[3]) <= 150, "time in seconds, under 150"
        assert cells[2], "name the imperative the story showed"
