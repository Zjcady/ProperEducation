# Study coach, built for a brain that forgets

LeetCode (83 problems, 17 patterns, growing) plus a build track (Python foundations, then GenAI labs). 15-minute blocks. Spaced repetition so it sticks. See `../ROADMAP.md` for where this goes.

## The ritual (15 to 45 minutes, in blocks)

```
cd "3. LeetCode"
python3 coach.py                  # today's blocks. Block 1 counts, the rest is bonus.
python3 coach.py start 001        # 15 min timer. A problem may take two blocks. Hard stop at 30.
#   ... read PROBLEM.md (top part only), code in solution.py ...
python3 coach.py check 001        # run the tests
python3 coach.py hint 001 1       # stuck 5+ min? one hint. then 2. then 3.
python3 coach.py done 001 2       # rate it: 1 struggled, 2 hints, 3 clean + explained

python3 coach.py start A01        # build block: a chapter. read.md, then
python3 coach.py checks A01       # 5 quick questions, then challenge.py, then
python3 coach.py done A01

python3 coach.py floor            # bad day? the 5-minute thing that still counts
python3 coach.py touch "note"     # "I did 5 minutes." Counts.
python3 coach.py more             # hyperfocus? one extra review or build step. Never a 2nd new problem.
python3 coach.py skip A03         # placement: already know a chapter? skip it.
```

Block 1 done means today counts. Stopping there is correct. Tomorrow has its own.

## The rules, and why

| Rule | Why |
|------|-----|
| One new problem per day, max | Two days of one problem beats one day of six. Volume doesn't stick. |
| 15 minute blocks, hard stop at 30 on a problem | A stuck brain at minute 40 learns nothing. Rate it 1, see it tomorrow. |
| First block counts, the rest is bonus | More sittings beat longer sittings. Bonus never becomes an obligation. |
| A 5-minute floor | Touch it every day. Streaks survive bad days, which is what keeps them alive. |
| Reviews before new material | Protecting what you already learned is worth more than new stuff. |
| Reviews are re-solves from a blank function | Reading old code feels like knowing. It isn't. Retrieval is. |
| Hints in order, one at a time | Each hint you *don't* need is a thing you figured out yourself, which is the thing you'll remember. |
| Explain it back before rating 3 | If you can't say the trick in one sentence, you'll lose it by Thursday. |
| Missed days don't pile up | At most 2 reviews a day. No backlog, no guilt. Just run `next`. |

## How the spacing works

| You rate it | Next time you see it |
|-------------|----------------------|
| 1 struggled / peeked at answer | tomorrow |
| 2 solved with hints | 3 days |
| 3 clean solve + explained | 3 days, then 8, then 19, then 47, then it's mastered |

Problems move `new → learning → review → mastered`. Chapter checks come back in 3 days if you missed any, once at 7 days if perfect, then clear. `python3 coach.py status` shows the maps.

## On your phone

`site/` is a static page that shows today's problem, its hints (collapsed, one at a time), the pattern card and your progress map. It's deployed on Vercel from this repo and refreshes every morning and after each session. The page is read-only on purpose: you solve in a Claude session, the page tells you what and why.

## Every morning, automatically

A scheduled task (`DAILY_TASK.md`) runs at 7:54 Eastern, scaffolds the next problem's folder if it's still a bare template, rebuilds the page, and pushes. You wake up to a ready problem.

## Working with Claude

Open a session in this repo and say "leetcode". Claude reads `COACHING.md` and runs `next`. It will not hand you solutions. It will ask you what the brute force is. That's on purpose. If you want the answer anyway, ask for it after hint 3, then close it and re-type from memory.

## Layout

```
coach.py            the brain: next / floor / start / check / hint / checks / done / touch / more / skip / status / list
harness.py          tiny test runner + ListNode/TreeNode helpers + run_levels for chapters
curriculum.json     83 problems pattern-ordered, plus build items (A01..A12 chapters, C1..C8 and D1..D5 labs)
foundations/NN-Axx/ a chapter: read.md, checks.json, CHALLENGE.md, challenge.py, NOTES.md
labs/Cx, labs/Dx    a lab: README.md with steps, starter/, tests/, RUBRIC.md (built in phase 3)
_chapter_template/  what a fresh chapter starts from
progress.json       your spaced-repetition state (coach.py owns this)
patterns/           one 2-minute explainer per pattern
problems/NNN-slug/  PROBLEM.md (plain words + hints), solution.py (stub + tests), NOTES.md
_template/          what a fresh problem folder starts from
site/               the phone page: index.html + data.json (built by site/build.py)
DAILY_TASK.md       the prompt the morning scheduled task runs
```

Only Python 3 is needed. No packages.
