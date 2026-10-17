# E2 · Resume bullets, generated then edited

**Maps to:** the whole posting; this is how the work in this repo gets onto one page.
**You'll have at the end:** `RESUME.md` with numbers you can defend and one bullet per finished lab, in your words.

## Step 1 · Generate  (15 min)

Run `python3 coach.py resume`. It reads your real progress: problems solved, patterns covered, mocks, chapters, labs, and one bullet template per finished lab from `bullets.json`. Read what it printed. If a number surprises you, that's the number an interviewer will ask about.

Then `python3 coach.py resume --write` to create `RESUME.md`. Then `check`.

## Step 2 · Edit  (15 min)

Edit `RESUME.md` by hand. Rules: every bullet starts with a verb, has one number or one named artifact, and fits on one line. Cut anything you couldn't explain for two minutes. Add a one-line headline at the top. Delete the generator's intro sentence. Then rubric review and `python3 coach.py done E2`.

`bullets.json` is yours to improve too. If a lab taught you something the template doesn't capture, change the template; the next `--force` regeneration will use it.
