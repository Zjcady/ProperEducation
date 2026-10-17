# Daily scheduled task

A Claude scheduled task fires every morning at 7:54 Eastern (a few minutes early
to dodge the on-the-hour rush) in a fresh cloud session. This is the prompt it
runs, kept here so it can be read and edited. Changing this file does not change
the task; ask Claude to update the scheduled task's prompt.

---

You are preparing today's LeetCode problem in the repository zjcady/ProperEducation.

Branch: `main`.

0. If the repository is not already checked out in your working directory, call the `add_repo` tool for owner `zjcady`, repo `ProperEducation` with push access, then run the clone command it gives you and work inside that clone.
1. Fetch and check out `main`, then pull so you have the latest progress.
2. Read `3. LeetCode/COACHING.md`. You are scaffolding, not coaching, but its rules on never writing solutions still apply.
3. In `3. LeetCode/`, run `python3 coach.py next`.
4. For each item in today's plan whose folder is missing or is a bare template:
   - A problem is a bare template when its `solution.py` contains `TODO_METHOD_NAME`. A chapter (ids A01..A12) is bare when its `read.md` or `checks.json` contains `{{`. Labs C1..C8 are already written; never modify them. A D-lab (D1..D5) with only a placeholder README is out of scope for this task; leave it and mention it in your reply.
   - If the folder is missing, run `python3 coach.py start <id>`. On a missing folder this only scaffolds from the template and exits without starting the timer.
   - Problems: fill in `PROBLEM.md`, the `Solution` method signature in `solution.py`, 5 to 7 `TESTS`, and `NOTES.md`, matching `problems/001-two-sum/` exactly: plain-words description under 4 sentences, one example, two "before you code" bullets, three hints in order (nudge, idea, skeleton with a blank), three explain-it-back questions.
   - Chapters: fill in `read.md` (under 5 minutes, one idea, one runnable example, "the two things people get wrong"), `checks.json` (5 or 6 questions, mix of choice and text, each with a `why`), `CHALLENGE.md` (three levels, each adding one constraint, plus a three-hint ladder) and `challenge.py` (three functions with 4 to 6 tests each), matching `foundations/01-A01/` exactly. The chapter's topic is its title in `curriculum.json`; `ROADMAP.md` at the repo root lists the sequence.
   - Verify every test: write a reference solution in a scratch file outside the repository, run it against the tests the same way the harness does, fix any wrong test, delete the scratch file. Reference solutions are never committed or pasted into the repository.
5. Never edit `progress.json` by hand. Never run `coach.py start` on an item whose folder already exists (that starts the learner's timer). Never run `coach.py done`, `checks`, `touch`, `more` or `skip`.
6. Run `python3 site/build.py`.
7. Commit everything with a message like `Daily: scaffold 009 Valid Palindrome, A02` (or `Daily: refresh site data` if nothing needed scaffolding) and push with `git push -u origin main`. Do not create a pull request.
8. Reply with one line: which problem is up today and whether you scaffolded it.
