# ProperEducation roadmap

Goal: replace a zyBooks subscription, prep for any LeetCode problem, and land an
AI / autonomy software engineer role (the Lockheed Martin "autonomy and AI
algorithms for mission systems" posting). One system, one daily ritual, built
for ADHD and leaky memory.

## 1. Honest read of the job posting

The "responsibilities" paragraph sounds like robotics (perception, motion
planning, controls). The **basic qualifications** tell the real story: this is
an early-career **GenAI integration** role.

| What they list | What it actually means | Evidence that gets you the interview |
|---|---|---|
| Python / TypeScript, learn tools and workflows | Comfortable writing and testing Python | Clean repos with tests, this one included |
| GenAI fundamentals, applied in simple cases | Tokens, prompts, structured output, embeddings | A small CLI that calls an LLM and does something useful |
| Wrap prompts in apps / workflows | Scripted pipelines around an LLM | A pipeline that takes files in, returns summaries or classifications |
| Tool calling / MCP, auth and authz | Build an MCP server, understand API keys, OAuth, scopes | An MCP server you wrote, with one protected tool |
| AI dev accelerators (Cursor, Cline, etc.) | Use Claude Code, Cursor and friends deliberately | CLAUDE.md, hooks and a skill in a repo of yours, plus a short write-up |
| Desired: agentic frameworks | An agent loop with tools, then a framework | One agent that does a multi-step task |
| Desired: document processing for LLMs | Chunking, embeddings, retrieval (RAG) | A RAG demo over a real document set |
| Desired: meeting summarizers, AWS | Transcription + summary; S3, Lambda, Bedrock basics | The summarizer deployed as a Lambda |
| LM Navigator, Genesis | Internal Lockheed tools | Not learnable outside. Ignore. |

**What this means for LeetCode**: it gets you through the coding screen. It does
not get you the job. The portfolio projects do. So the plan runs both in
parallel rather than LeetCode first, projects later.

**Two things to check before investing months**: Lockheed roles usually
require US citizenship and the ability to get a clearance. Confirm you're
eligible. And the posting says "foundational" programming, so an associate's
or bootcamp-level background plus a strong portfolio is realistic.

## 2. How we beat zyBooks

zyBooks sells four things: short readings, participation activities (click
through an animation, answer a quick check), challenge activities (auto-graded
exercises in escalating levels), and labs. Its weaknesses: passive, no spaced
repetition, no real projects, nothing to show an employer afterwards.

| zyBooks | Here |
|---|---|
| Reading section | `read.md`, under 5 minutes, one idea |
| Participation activity | `checks.json`, 3 to 5 auto-graded quick questions, terminal or phone |
| Challenge activity, levels 1 to 3 | `challenge_N.py` with tests, each level adds a constraint |
| Lab | A folder with a starter, tests, and a rubric Claude grades against |
| Progress bar | Spaced repetition. Things you got wrong come back. |
| Due dates | One thing per day. 25 minutes. No backlog. |
| Nothing after you finish | A GitHub repo with real projects, and resume bullets generated from them |

## 3. The tracks

### Track A · Python foundations (replaces the zyBooks course)
12 chapters. Each is one day: read (5 min), checks (5 min), one challenge (15 min).
A placement check at the start lets you skip chapters you already own.

1. Values, types, variables, f-strings
2. Conditionals and loops
3. Functions, scope, default args
4. Strings and slicing
5. Lists, tuples, and iteration patterns
6. Dicts and sets (feeds straight into LeetCode pattern 01)
7. Files, with-blocks, exceptions
8. Classes and dataclasses
9. Modules, packages, virtual environments, pip
10. Testing with pytest, and reading a traceback
11. Type hints, iterators, generators, comprehensions
12. Big-O in plain words, and the standard library you'll actually use (collections, itertools, heapq, bisect)

Labs: ch 7 (a log parser), ch 10 (test an existing module), ch 12 (benchmark two implementations).

### Track B · LeetCode (exists, expands)
"All of LeetCode" is about 3,600 problems. The honest version of "prep for
all of them" is: own the patterns, then drill without limit.

| Tier | Problems | What it is | Status |
|---|---|---|---|
| 1 | 83 | 17 patterns, one curated set | **built** |
| 2 | +60 = 143 | The rest of the standard 150 interview set, minus premium | **built** |
| 3 | +188 = 331 | Depth: 8 to 16 more per pattern, more hards | **built** |
| 4 | any | `coach.py add <leetcode-slug>` scaffolds any problem on demand, same hints and tests format, enters the same review rotation, jumps the queue | **built** |

Tier 4 is what makes "all of LeetCode" true: any problem you meet in a mock
interview or a company's tagged list can be pulled in and drilled.

Also: a weekly **mock interview** mode where Claude plays interviewer for one
problem, with a timer, and grades communication as well as code.

### Track C · GenAI engineering (the job's basic qualifications, in order)
Each lab is a folder: `README.md` (what and why), `starter/`, `tests/`,
`RUBRIC.md`. Claude reviews against the rubric and the review goes in a
`REVIEW.md` you can quote on a resume. Done in 25-minute blocks across several days.

| Lab | Builds | Maps to |
|---|---|---|
| C1 · First LLM call | CLI that sends a prompt, parses structured JSON back, handles errors and retries | GenAI fundamentals |
| C2 · Prompt in a workflow | A script that walks a folder of files and summarizes or classifies each, with a cost and token report | Wrap prompts in workflows |
| C3 · MCP server | An MCP server exposing `coach.py` (next, start, check, done) as tools, one tool protected by a token, with a short doc on API keys vs OAuth, scopes, least privilege | Tool calling / MCP, auth and authz |
| C4 · Agent loop | A from-scratch agent loop with 3 tools, then the same thing in an agent framework. Compare. | Agentic frameworks |
| C5 · Document processing / RAG | Chunk, embed, store, retrieve, answer with citations, and a small eval set | Document processing for LLMs |
| C6 · Meeting summarizer | Audio in, transcript, summary, action items, decisions. Then: your gecko videos in, captions and voiceover script out. Same pipeline. | Meeting summarizers, plus your social media goal |
| C7 · AI dev accelerators | Write up how this repo uses CLAUDE.md, hooks, a skill, and the daily task. Try the same in Cursor. One page, with screenshots. | AI-enabled development accelerators |
| C8 · AWS | Put C6 behind a Lambda with S3 in and out. Bedrock call optional. Free tier. | AWS |

The gecko content pipeline (C6) is the portfolio centerpiece on purpose. A
project you actually want to use is the one you finish.

### Track D · Autonomy flavor (the responsibilities paragraph)
Short, optional, differentiating for this specific employer.

**No C++ in this plan, on purpose.** Autonomy teams use C++ heavily, but the
basic qualifications say Python or TypeScript, and splitting attention across
two languages costs more than it buys at this stage. Python first, all the way.
Revisit C++ after an offer, or if a specific posting requires it.

- D1 · State machines: a mission broken into tasks with transitions (their "break missions into tasks")
- D2 · Path planning: BFS, then A*, on a grid with obstacles (reuses LeetCode graph patterns)
- D3 · A PID controller on a simulated 1-D system, with a plot
- D4 · Perception basics with OpenCV: detect a colored object in a frame (your geckos, again)
- D5 · A tiny human-machine interface: a web page that shows mission state and lets a person approve a task (their "HMI scenarios")

### Track E · Interview readiness
- Behavioral stories in STAR format, generated from your actual labs, rehearsed with Claude
- Resume bullets generated from completed labs and reviewed against the posting
- Systems-design lite: explain C3 or C5 on a whiteboard in 10 minutes
- Weekly mock from Track B

## 4. The daily ritual, expanded

Work-day shape: 15-minute blocks spread through the day. The first one counts; the rest are bonus.

```
Block 1 (15, up to 30 min)  LeetCode: review if due, else the next new problem
Block 2 (15 min)            Build: the next step of the current chapter or lab
Floor   (5 min)             a checks review or a pattern card, on bad days
```

`coach.py next` returns both. The phone page shows both. Reviews for
foundations checks you got wrong come back on the same spaced schedule as
LeetCode problems. Weekends: a lab block only, or nothing.

Honest calendar, from the actual numbers: one new problem per weekday (5 a
week) and one build step per weekday. Reviews and bonus blocks don't change
these dates; missed days push them back, and that's fine.

| Weeks | Block 1 (LeetCode) | Block 2 (build) |
|---|---|---|
| 1 to 3 | Tier 1 begins: arrays, two pointers, sliding window | Python foundations A01 to A12 (skip what placement clears) |
| 4 to 9 | Tier 1 continues; weekly mocks start after 5 solves | Labs C1 to C8 (27 steps) |
| 10 to 12 | Tier 1 continues | Labs D1 to D5, then E1 to E3 |
| **12** | **Apply.** | |
| 13 to 17 | Tier 1 finishes (83 problems is about 17 weeks) | Re-do the lab you'd demo; keep rehearsing E1 and E3 |
| 18 to 29 | Tier 2 (the 150 finishes around week 29) | Interviews |
| after | Tier 3 and `add` drills for each company's list | |

**Why apply at week 12, not when tier 1 is done.** By week 12 the build track
is finished: tested Python, an MCP server, an agent, RAG, a deployed Lambda,
the autonomy labs and rehearsed stories. That's the application. LeetCode keeps
going during the hiring process, which takes weeks anyway. And for a cleared
role the government's clock only starts after an offer: an initial Secret
averages about 197 days (ClearanceJobs, Q3 FY2026). Every week of waiting to
apply is a week added to that.

The old version of this table assumed 3 to 5 new problems a day. It would have
said "behind" by week 13, which is the thing this system promises never to do.

## 5. Build plan (what Claude builds, in order)

| Phase | What | Size |
|---|---|---|
| 0 | LeetCode coach, phone page, daily task | **done** |
| 1 | Tracks in `coach.py`: the daily plan holds a LeetCode item and a build item. `checks` command for quizzes. Phone page shows both blocks and runs checks. | **done** (work-day shape: 15-minute blocks, first one counts, floor, more) |
| 2 | Track A, chapters 1 to 12, generated one chapter ahead by the daily task, same as problems | 2 sessions + daily |
| 3 | Track C lab folders C1 to C8 with starters, tests, rubrics. C3 doubles as the coach's own MCP server. | **done** |
| 4 | Track B tiers 2 and 3 entries, `coach.py add <slug>`, mock interview mode | **done** |
| 5 | Track D and Track E | **done** |
| 6 | Phone page polish: quizzes, lab progress, streak calendar | 1 session |

## 6. Costs

| Item | Cost |
|---|---|
| zyBooks (for comparison) | roughly $60 to $90 per course |
| This system | $0 |
| Claude API for labs C1 to C6 | a few dollars a month at hobby volume |
| AWS for C8 | free tier |
| LeetCode Premium | optional. Tier 1 avoids premium problems. |

## 7. Decisions needed from you

1. Daily budget: one 25-minute block or two? The calendar above assumes two.
2. Python foundations: do all 12 chapters, or take the placement check and skip what you pass?
3. Gecko content pipeline as the portfolio centerpiece (C6): yes or pick something else?
4. Citizenship and clearance eligibility for Lockheed: confirmed?
