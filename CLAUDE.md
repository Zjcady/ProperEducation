# ProperEducation

A personal learning repo. Folders are numbered in the order they were started.

- `1. HelloWorld`, `2. Calculator`: early C++ (Visual Studio).
- `ROADMAP.md`: the plan (zyBooks replacement, LeetCode prep, GenAI job track). Read it before adding content.
- `3. LeetCode`: the active project. Python. LeetCode track plus a build track (foundations chapters, labs). **Read `3. LeetCode/COACHING.md` before doing anything in it.** It is a coaching protocol for a learner with ADHD, and the short version is: run `coach.py next`, never hand over solutions, hints in order, one thing at a time.

When the user says "leetcode" or anything close, go straight to the coaching protocol.

What the coach has learned about this learner (read it before coaching):
@3.\ LeetCode/LEARNER.md

Hooks in `.claude/settings.json` put today's plan in context at session start, rebuild the phone page after any progress-writing `coach.py` command, and stop a session from ending with unsaved or unpushed progress. Auto memory is off on purpose: cloud sessions can't keep it, so `LEARNER.md` is the memory.
