# C7 · AI dev accelerators, written up

**Maps to:** "Configures and uses AI-enabled development accelerators (Cursor, Devin, Cline...) to automate tasks, generate code, or improve workflows; has applied them to small projects."
**You'll have at the end:** a Claude Code skill and a hook in this repo that you wrote, plus a one-page write-up comparing Claude Code and Cursor configuration. This is the lab where you turn "I used Claude" into something an interviewer can look at.

This repo already uses three accelerator features: `CLAUDE.md` (project instructions), a scheduled task (`DAILY_TASK.md`), and the coaching protocol. You add two more.

## Step 1 · A skill  (15 min)

A skill is a folder with a `SKILL.md` that Claude Code loads when the user types `/name` or when the description matches. Write `.claude/skills/leetcode/SKILL.md` at the **repo root** (not in this lab folder). Start from `starter/SKILL.md`.

It needs YAML frontmatter with `name: leetcode` and a one-sentence `description`, then a body that says: read `3. LeetCode/COACHING.md`, run `coach.py next`, and follow the protocol. Keep it under 30 lines. Test it: open a session and type `/leetcode`.

## Step 2 · A hook and the write-up  (15 min)

A hook is a command Claude Code runs around tool calls. Write `.claude/hooks/protect_solutions.py` at the repo root from `starter/protect_solutions.py`. It's a `PreToolUse` hook: it reads a JSON object from stdin with `tool_name` and `tool_input` (which has `file_path` for Edit and Write), and:

- exits `2` with a one-line reason on stderr when the path is a learner file: `problems/*/solution.py` or `foundations/*/challenge.py`. Exit 2 blocks the tool call and shows the reason to Claude.
- exits `0` otherwise, **and** when the learner file is still the untouched template (it contains `TODO_METHOD_NAME` or `TODO_ARGS`). That exemption is what lets the morning scheduled task fill in a fresh stub. Think about why the check has to read the file, not just the path.

Register it in `.claude/settings.json` at the repo root (the exact JSON is in `starter/settings.json`). Now the coaching rule "never type their answer" is enforced by the harness, not by good intentions.

Then fill in `WRITEUP.md`: the five features this repo uses, what each does, and the Cursor equivalent (rules files, `.cursorrules` or `.cursor/rules`, and its agent mode). One page. Then rubric review and `python3 coach.py done C7`.
