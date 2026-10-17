# Improvements backlog

Researched 2026-10-17 by six parallel researchers (ADHD learning science, interview prep, the target role, GenAI skills, competitor platforms, tooling), merged, then put through three adversarial critics (is the evidence real, is it already built, is it worth its cost) and ranked by impact over effort. 46 raw findings, 18 shortlisted, 14 survived, 4 rejected. Built on 2026-10-17: rank 1 (scheduler), rank 2 (routine + PHONE.md; the Shortcut is yours to build), rank 3's four roadmap edits, rank 4 (hooks, LEARNER.md), rank 5's interleaving reorder, rank 6 kernel (bell times), rank 7 (imperatives, Story 6, roadmap row), rank 8 kernel (worked-example mode), rank 9 kernel (installable page), and the streak kernel from the first rejected bundle (weekends, one freeze, active N of 7). Also fixed: the coach now runs on Eastern time instead of the container's UTC. Everything else is still open.

# What to build next

Fourteen improvements survived the critics. This ranks them by impact for you divided by effort. Where the critics cut a bundle down to a kernel, the rank is for the kernel and the caveat says what was cut.

Where you stand: no block logged yet (streak 0), next problem 001 Two Sum, next chapter A01. That is why starting, truth-keeping and before-day-3 correctness come first, and lab content comes later.

Effort scale: small = under an hour of Claude's build time, medium = one session, large = several.

## Ranked

| # | Build | Effort | Impact | Caveat |
|---|---|---|---|---|
| 1 | Scheduler fixes (Hard grows, overdue credit, fuzz, soft reset, leech flag, 90-day confirm) | small | high | none |
| 2 | One-tap Start block (routine + API trigger + phone Shortcut) | small + 20 min of yours | high | none |
| 3 | Roadmap kernel: honest calendar, apply at week 12, no C++, graphs ahead of tries | small (kernel) | high | E4 lab, apply item, apply_ready, drill mode deferred |
| 4 | Three hooks in .claude/settings.json + LEARNER.md | small | medium | none |
| 5 | Interleave kernel: rotate new problems across opened patterns after two each | small (kernel) | high | sort-key bug fixed; hide-pattern and `which` deferred |
| 6 | Print 'Bell at HH:MM. Hard stop HH:MM.' | tiny | medium | goal flag, hint gate, page countdown dropped |
| 7 | STAR imperatives + 'why Lockheed' facts | small | medium | none; not needed until Track E |
| 8 | Completion-mode flag: skeleton up front on a pattern's first problem | small (kernel) | medium | 17 worked examples, re-type gate, hint 4 deferred |
| 9 | Phone page installable (manifest, icons, standalone) | small (kernel) | medium | push, badge, crons deferred; use a 3 pm alarm |
| 10 | C3 auth on the transport (HTTP + bearer verifier) | medium | high | none; land before week 7 |
| 11 | C4 real safety step (injection, JSON tool results, screen, SAFETY.md) | medium | high | none; land before week 9 |
| 12 | C2 prompt caching slice + cached-input report line | small (kernel) | medium | Bedrock/IAM swap deferred; structured-outputs claim disputed |
| 13 | Predict-first lines in chapter template | small (kernel) | low-med | pretest and placement run rejected |
| 14 | C9 evals and traces lab | large | high | right lab, wrong week; after C8 |

## Do first

**1. Scheduler fixes.** The code confirms every claim: a hints-only solve never advances, a recall 12 days late counts as on time, a problem leaves forever at about day 47, a stuck problem loops daily with no exit. Six small edits in `cmd_done`, `due_reviews` and `plan`. No reservations. Nothing bites until the first review on day 3, so do it this week, not next month. Add the two 'Bell at HH:MM' lines in the same session.

**2. One-tap Start block.** You have not logged a block yet. Today a phone block is five taps and a wait. Each tap is a place to bounce off. A 'Start block' routine with an API trigger, fired from a Home Screen Shortcut, lands you in a session already saying 'Block 1: 001 Two Sum, 15 minutes', with the timer running. Claude writes the recipe into `PHONE.md`. You spend about 20 minutes building the Shortcut once.

**3. Roadmap kernel.** Four edits. The calendar says tier 1 fits in 12 weeks; at one new problem per weekday it is 17. Left alone, the plan itself calls you 'behind' at week 13. Move 'apply' to week 12, because the clearance clock (about 197 days for a Secret) starts only after an offer. Add the no-C++ line. Move graphs ahead of tries in `curriculum.json` while you are still on pattern 1. The E4 lab and the weekly apply item wait for a later session.

**4. Hooks plus LEARNER.md.** Steps 7 and 8 of the session ritual keep the phone page true, and they happen at the bell, when they are most likely skipped. A `PostToolUse` hook reruns `build.py` after any `coach.py` state change. A `Stop` hook refuses to end with uncommitted progress. A `SessionStart` hook puts block 1 in context before you type. A 40-line `LEARNER.md`, one line per session in your words, gives fresh cloud sessions a memory of you.

**5. Interleave reorder, kernel only.** After the first two problems of a pattern, rotate new problems across the patterns you have opened. About 10 lines in `next_new_problem()`, with the critics' fix: never serve problem 1 of all 17 patterns up front. Hiding the pattern on reviews and the `which` drill wait until there are solved problems to draw from. Without this, days 3 to 8 are six more arrays-hashing problems in a row.

## Rejected

Killed by the critics. Each has a small piece worth keeping.

| Finding | Why killed | Keep |
|---|---|---|
| Streak freezes, calendar, badges, micro-rewards | Five reward surfaces for a page with zero history; clean spree punishes honest rating 1 | Weekend-safe `bump_streak`, one freeze, 'N of last 7' |
| Honest coding mock bundle | 8 retrofits, longer block, new command, monthly hour-long peer mock; burns tier-2 problems | `mock_pick` from unsolved covered patterns, reweighted rubric, one twist |
| Lockheed loop rehearsal (A13, 45-min panel mock, HireVue mode) | Nine topics in one chapter; 45 minutes on a weekend in a 15-minute system; secondary evidence | Move Track E earlier (one ROADMAP line) |
| Phone buttons for touch/done/checks/skip via GitHub Action | Done-3 from a phone skips explain-it-back; `done C3` skips tests; three front ends; push race on progress.json | touch and checks only, one front end, pull before write |

Trimmed from survivors, not killed: the `which` drill and pattern hiding (5), the 17 worked examples and re-type gate (8), the goal flag, hint gate and countdown (6), push notifications and badge (9), the Bedrock/IAM swap (12), the pretest and placement run (13), the E4 lab and apply item (3).

## Sources

1. Anki Manual FAQ, algorithm (Hard x1.2, fuzz, leeches): https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm
2. FSRS algorithm wiki (retrievability-based stability): https://github.com/open-spaced-repetition/awesome-fsrs/wiki/The-Algorithm
3. Claude Code docs, routines and API triggers: https://code.claude.com/docs/en/routines
4. Claude API, trigger a routine: https://platform.claude.com/docs/en/api/claude-code/routines-fire
5. ClearanceJobs, clearance processing times Q3 FY2026: https://news.clearancejobs.com/2026/09/02/how-long-does-it-take-to-process-a-security-clearance-q3-2026-fy-update/
6. AlgoMonster ROI table: https://algo.monster/problems/stats
7. Claude Code docs, memory (context, not enforcement): https://code.claude.com/docs/en/memory
8. Claude Code docs, hooks reference: https://code.claude.com/docs/en/hooks
9. WWC review of Rohrer et al. 2020 (interleaving, d = 0.83): https://ies.ed.gov/ncee/wwc/Study/88770
10. Brunmair & Richter 2019 meta-analysis: https://www.psychologie.uni-wuerzburg.de/fileadmin/06020400/2019/Brunmair_Richter_in_press__2019_META-ANALYSIS_OF_INTERLEAVED_LEARNING.pdf
11. Ptacek et al. 2019, time perception in ADHD: https://pmc.ncbi.nlm.nih.gov/articles/PMC6556068
12. Lockheed Martin, Full Spectrum Leadership: https://lockheedmartin.com/en-us/who-we-are/leadership-governance/full-spectrum-leadership.html
13. Lockheed Martin RFI response (Navigator, Genesis, Jiminy): https://files.nitrd.gov/90-fr-9088/LMCO-AI-RFI-2025.pdf
14. Kalyuga 2007, expertise reversal: https://www.uky.edu/~gmswan3/EDC608/Kalyuga2007_Article_ExpertiseReversalEffectAndItsI.pdf
15. WebKit, Web Push for Home Screen web apps: https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/
16. MCP spec 2026-07-28, Authorization: https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/docs/specification/2026-07-28/basic/authorization/index.mdx
17. Claude docs, mitigate jailbreaks and prompt injections: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks.md
18. OWASP LLM01 Prompt Injection: https://raw.githubusercontent.com/OWASP/www-project-top-10-for-large-language-model-applications/main/2_0_vulns/LLM01_PromptInjection.md
19. Claude docs, prompt caching: https://platform.claude.com/docs/en/build-with-claude/prompt-caching.md
20. Richland, Kornell & Kao 2009, pretesting effect: https://learninglab.uchicago.edu/Pre-Testing_files/RichlandKornellKao.pdf
21. Anthropic Engineering, evals for agents: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
22. Rawson & Dunlosky, successive relearning: https://www.retrievalpractice.org/archive/2018/successive-relearning
