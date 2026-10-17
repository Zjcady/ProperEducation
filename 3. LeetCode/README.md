# LeetCode, built for a brain that forgets

~80 problems. 17 patterns. One problem a day. Spaced repetition so it sticks.

## The ritual (15 to 30 minutes)

```
cd "3. LeetCode"
python3 coach.py                  # what's the one thing today?
python3 coach.py start 001        # set a 25 min timer. Really.
#   ... read PROBLEM.md (top part only), code in solution.py ...
python3 coach.py check 001        # run the tests
python3 coach.py hint 001 1       # stuck 5+ min? one hint. then 2. then 3.
python3 coach.py done 001 2       # rate it: 1 struggled, 2 hints, 3 clean + explained
```

Then stop. Tomorrow has its own problem.

## The rules, and why

| Rule | Why |
|------|-----|
| One new problem per day, max | Two days of one problem beats one day of six. Volume doesn't stick. |
| 25 minute timer, stop at the bell | A stuck brain at minute 40 learns nothing. Rate it 1, see it tomorrow. |
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

Problems move `new → learning → review → mastered`. `python3 coach.py status` shows the map.

## Working with Claude

Open a session in this repo and say "leetcode". Claude reads `COACHING.md` and runs `next`. It will not hand you solutions. It will ask you what the brute force is. That's on purpose. If you want the answer anyway, ask for it after hint 3, then close it and re-type from memory.

## Layout

```
coach.py            the brain: next / start / check / hint / done / status / list
harness.py          tiny test runner + ListNode/TreeNode helpers
curriculum.json     the 83 problems, pattern-ordered
progress.json       your spaced-repetition state (coach.py owns this)
patterns/           one 2-minute explainer per pattern
problems/NNN-slug/  PROBLEM.md (plain words + hints), solution.py (stub + tests), NOTES.md
_template/          what a fresh problem folder starts from
```

Only Python 3 is needed. No packages.
