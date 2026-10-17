# Study coach, built for a brain that forgets

LeetCode in tiers (83 pattern problems, then the standard 150, then 300 with depth, then anything you add) plus a build track (Python foundations, then GenAI labs). 15-minute blocks. Spaced repetition so it sticks. Weekly mock interviews. See `../ROADMAP.md` for where this goes.

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

python3 coach.py add valid-palindrome-iii --pattern two-pointers   # any LeetCode slug, queued as next
python3 coach.py mock             # Saturdays, after 5 solves: a 30-minute mock with Claude as interviewer
python3 coach.py list tier 2      # see the other tiers
python3 coach.py resume           # resume bullets and numbers from what you've actually finished
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

## The LeetCode tiers

| tier | what | how many |
|---|---|---|
| 1 | one curated set per pattern | 83 |
| 2 | the rest of the standard 150 interview set, minus premium | 60 |
| 3 | depth: 8 to 16 more per pattern, more hards | 188 |
| 4 | drill: anything you pull in with `coach.py add` | unlimited |

New problems come in tier order; `add` jumps the queue. "All of LeetCode" means: own the patterns, then drill whatever a job's list throws at you.

## How the spacing works

| You rate it | Next time you see it |
|-------------|----------------------|
| 1 struggled, or peeked at the answer (**even if the tests pass**: peeking is a 1) | tomorrow |
| 2 solved, needed hints | the interval grows a little (×1.2, at least 3 days) |
| 3 clean solve + explained it back | 3 days, then about 8, 19, 47 (×2.5 each time) |

The fine print, borrowed from Anki:
- **Late is fine.** A clean solve 12 days after it was due counts for those 12 days, so the next gap is bigger.
- **A slip isn't a restart.** After a 1, the next clean solve jumps back to half the gap you had.
- **Long gaps wobble a day or two**, so reviews don't pile up on the same day.
- **Mastered means twice.** A clean solve after a gap of two weeks or more, when it pushes the next gap past 30 days, marks it mastered, then one confirmation re-solve 90 days later. Pass that and it's done for good. Mastered problems also come up more in mocks.
- **[LEECH]** marks a problem you've slipped on 3 times: read its pattern card first and ask for the worked example. At 5 slips an easier problem of the same pattern is queued next.

New problems interleave: each pattern's first two come back to back, then new problems rotate across the patterns you've opened. That rotation is what trains "which pattern is this?", the question every interview actually asks.

Problems move `new → learning → review → mastered`. Chapter checks come back in 3 days if you missed any, once at 7 days if perfect, then clear. `python3 coach.py status` shows the maps.

## On your phone

`site/` is a static page that shows today's problem, its hints (collapsed, one at a time), the pattern card and your progress map. It's deployed on Vercel from this repo and refreshes every morning and after each session. The page is read-only on purpose: you solve in a Claude session, the page tells you what and why.

## One tap from your home screen

`PHONE.md` walks through a Shortcut that starts the timer, opens a session, and has block 1 waiting. Set it up once, about 20 minutes.

## Every morning, automatically

A scheduled task (`DAILY_TASK.md`) runs at 7:54 Eastern, scaffolds the next problem's folder if it's still a bare template, rebuilds the page, and pushes. You wake up to a ready problem.

## Working with Claude

Open a session in this repo and say "leetcode". Claude reads `COACHING.md` and runs `next`. It will not hand you solutions. It will ask you what the brute force is. That's on purpose. If you want the answer anyway, ask for it after hint 3, then close it and re-type from memory.

## Layout

```
coach.py            the brain: next / floor / start / check / hint / checks / done / touch / more / skip / status / list
harness.py          tiny test runner + ListNode/TreeNode helpers + run_levels for chapters
curriculum.json     331 problems in 4 tiers, plus build items (A01..A12 chapters, C1..C8 and D1..D5 labs)
interviews/         one file per mock interview
foundations/NN-Axx/ a chapter: read.md, checks.json, CHALLENGE.md, challenge.py, NOTES.md
labs/C1..C8         GenAI labs: README.md (one step per block), starter with TODO(you) functions, tests/, RUBRIC.md
labs/D1..D5         autonomy labs: state machine, BFS and A*, PID, OpenCV tracking, an operator console
career/E1..E3       interview readiness: STAR stories, resume bullets (coach.py resume), design talks
_chapter_template/  what a fresh chapter starts from
progress.json       your spaced-repetition state (coach.py owns this)
patterns/           one 2-minute explainer per pattern
problems/NNN-slug/  PROBLEM.md (plain words + hints), solution.py (stub + tests), NOTES.md
_template/          what a fresh problem folder starts from
site/               the phone page: index.html + data.json (built by site/build.py)
DAILY_TASK.md       the prompt the morning scheduled task runs
```

Only Python 3 is needed. No packages.
