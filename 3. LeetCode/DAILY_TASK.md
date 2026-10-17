# Daily scheduled task

A Claude scheduled task fires every morning at 7:54 Eastern (a few minutes early
to dodge the on-the-hour rush) in a fresh cloud session. This is the prompt it
runs, kept here so it can be read and edited. Changing this file does not change
the task; ask Claude to update the scheduled task's prompt.

---

You are preparing today's LeetCode problem in the repository zjcady/ProperEducation.

Branch: `claude/cloud-remote-work-setup-qklwnn`. If that branch has been merged and `3. LeetCode/` exists on `main`, use `main` instead.

1. Fetch and check out the branch, then pull so you have the latest progress.
2. Read `3. LeetCode/COACHING.md`. You are scaffolding, not coaching, but its rules on never writing solutions still apply.
3. In `3. LeetCode/`, run `python3 coach.py next`.
4. For each problem in today's plan whose folder under `problems/` is missing, or is a bare template (its `solution.py` contains `TODO_METHOD_NAME`, or its `PROBLEM.md` contains `_(Claude fills this in`):
   - If the folder is missing, run `python3 coach.py start <id>`. On a missing folder this only scaffolds from `_template/` and exits without starting the timer.
   - Fill in `PROBLEM.md`, the `Solution` method signature in `solution.py`, 5 to 7 `TESTS`, and `NOTES.md`, matching the format of `problems/001-two-sum/` exactly: plain-words description under 4 sentences, one example, two "before you code" bullets, three hints in order (nudge, idea, skeleton with a blank), three explain-it-back questions.
   - Verify the tests: write a reference solution in a scratch file outside the repository, run it against the TESTS the same way `harness.run` does, fix any wrong test, delete the scratch file. The reference solution must never be committed or pasted into the repository.
5. Never edit `progress.json` by hand. Never run `coach.py start` on a problem whose folder already exists (that starts the learner's timer). Never run `coach.py done`.
6. Run `python3 site/build.py`.
7. Commit everything with a message like `Daily: scaffold 009 Valid Palindrome` (or `Daily: refresh site data` if nothing needed scaffolding) and push with `git push -u origin <branch>`. Do not create a pull request.
8. Reply with one line: which problem is up today and whether you scaffolded it.
