# D1 · State machines: a mission as tasks

**Maps to:** the responsibilities paragraph: "perception, motion/mission planning, controls", "breaking missions into tasks" and "human-machine interfaces". This lab is the mission-planning line, done by hand.
**You'll have at the end:** a survey drone's mission as an explicit state machine (every legal move in one table, every illegal one an exception, every move taken written to a history), a planner that breaks a list of waypoints into the tasks the battery can cover, and a runner that flies the tasks through the machine and aborts when the battery says so. The history it records is what the D5 HMI will display.

Setup: `pip install -r requirements.txt` (only pytest). Pure Python, offline, no display.

**What a state machine is, in one sentence.** A thing that is always in exactly one state, and a table that says, for each (state, event) pair, which state comes next; anything not in the table cannot happen.

## Step 1 · The state machine  (15 min)

Read `mission.py` down to the step 2 marker. `State` (seven states), `TRANSITIONS` (the table; "abort" is allowed from every airborne state) and `IllegalTransition` are given. You write:

- `Mission.fire(event)`: look up `(self.state, event)` in the table. Not there: raise `IllegalTransition` whose message names the state by its `.name` (like `IDLE`) and the event, and change nothing. There: append `(old, event, new)` to `self.history`, set `self.state`, return the new state.
- `Mission.is_terminal()`: `True` once the mission is `LANDED` or `ABORTED`.
- `can_fire(state, event)`: `True` when the table has that pair. Never raises.

Try it: `python3 mission.py --abort` flies two legs, then a human presses abort. Read the printed history and say which line of the table each arrow came from.

## Step 2 · Break the mission into tasks and fly it  (15 min)

`Task`, `EVENT_FOR_KIND` (each task kind fires one event) and `task_cost` (transit, survey and return each cost one leg; takeoff and land are free) are given. You write:

- `plan_tasks(waypoints, battery_pct, reserve_pct=20, cost_per_leg=15)`: spendable battery is `battery - reserve - one leg for the return`. Each waypoint costs two legs (transit to it, survey it). Take waypoints in order while the next pair fits. Always `takeoff` first and `return`, `land` last, even if nothing fits. Do the demo numbers on paper first: 100 - 20 - 15 = 65, a waypoint is 30, so two fit and a third does not.
- `run(mission, tasks, battery_pct, reserve_pct=20)`: for each task, fire its event, subtract its cost, record its name. Before a transit or survey, if the battery would drop below the reserve, fire `"abort"` and stop instead. `return` and `land` always run; the reserve is for them. Return `{"completed": [...], "final_state": ..., "battery": ...}`.

Run `python3 mission.py`, then `python3 mission.py --battery 40` and explain why it aborted where it did. Then rubric review and `python3 coach.py done D1`.
