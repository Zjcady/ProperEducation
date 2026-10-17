"""D1 · A survey drone's mission: a state machine, then a list of tasks flown through it.

    python3 mission.py                 plan the demo mission on a full battery and fly it
    python3 mission.py --battery 40    the same plan flown on a pack that only had 40%: watch it abort
    python3 mission.py --abort         a human presses abort mid-flight (step 1 only)

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum


# ------------------------------------------------------------------ step 1 scaffolding

class State(Enum):
    IDLE = "idle"
    TAKEOFF = "takeoff"
    TRANSIT = "transit"
    SURVEY = "survey"
    RETURN = "return"
    LANDED = "landed"
    ABORTED = "aborted"


AIRBORNE = {State.TAKEOFF, State.TRANSIT, State.SURVEY, State.RETURN}
TERMINAL = {State.LANDED, State.ABORTED}

# (current state, event) -> next state. A pair that is not in the table is not allowed.
TRANSITIONS: dict[tuple[State, str], State] = {
    (State.IDLE, "launch"): State.TAKEOFF,
    (State.TAKEOFF, "depart"): State.TRANSIT,         # climb done, head for the first waypoint
    (State.TRANSIT, "arrived"): State.SURVEY,
    (State.SURVEY, "depart"): State.TRANSIT,          # on to the next waypoint
    (State.TAKEOFF, "return_home"): State.RETURN,     # nothing to survey
    (State.TRANSIT, "return_home"): State.RETURN,     # a human redirects mid-leg
    (State.SURVEY, "return_home"): State.RETURN,
    (State.RETURN, "landed"): State.LANDED,
}
for _airborne in AIRBORNE:
    TRANSITIONS[(_airborne, "abort")] = State.ABORTED  # a human can abort any time in the air


class IllegalTransition(Exception):
    """Raised by Mission.fire when (state, event) is not in TRANSITIONS."""


class Mission:
    """One drone mission: where it is now, and every transition it has taken so far."""

    def __init__(self, state: State = State.IDLE):
        self.state = state
        self.history: list[tuple[State, str, State]] = []

    def fire(self, event: str) -> State:
        """TODO(you): apply the transition for (self.state, event) and return the new state.

        Look the pair up in TRANSITIONS. If it is not there, raise IllegalTransition with a
        message that names the state and the event, and change nothing. Otherwise append
        (old_state, event, new_state) to self.history, set self.state, and return it.
        """
        raise NotImplementedError

    def is_terminal(self) -> bool:
        """TODO(you): True once the mission is LANDED or ABORTED (nothing can fire after that)."""
        raise NotImplementedError


def can_fire(state: State, event: str) -> bool:
    """TODO(you): True when TRANSITIONS has an entry for (state, event). Never raises."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 2 scaffolding

KINDS = ("takeoff", "transit", "survey", "return", "land")
EVENT_FOR_KIND = {"takeoff": "launch", "transit": "depart", "survey": "arrived",
                  "return": "return_home", "land": "landed"}
COST_PER_LEG = 15        # battery percent for one transit leg, one survey, or the return leg


@dataclass(frozen=True)
class Task:
    name: str
    kind: str                       # one of KINDS
    waypoint: str | None = None     # transit and survey tasks name their waypoint


def task_cost(task: Task, cost_per_leg: int = COST_PER_LEG) -> int:
    """Battery a task drains: one leg for transit, survey and return; takeoff and land are free."""
    return cost_per_leg if task.kind in ("transit", "survey", "return") else 0


def plan_tasks(waypoints: list[str], battery_pct: int, reserve_pct: int = 20,
               cost_per_leg: int = COST_PER_LEG) -> list[Task]:
    """TODO(you): break a mission into tasks the battery can cover, in waypoint order.

    Spendable battery is battery_pct - reserve_pct - cost_per_leg (the last leg is the
    return home). Each waypoint costs two legs: Task(f"transit to {wp}", "transit", wp) then
    Task(f"survey {wp}", "survey", wp). Take waypoints in order while the next pair still
    fits; stop at the first one that does not. Always start with Task("takeoff", "takeoff")
    and always end with Task("return", "return"), Task("land", "land"), even with no waypoints.
    """
    raise NotImplementedError


def run(mission: Mission, tasks: list[Task], battery_pct: int, reserve_pct: int = 20,
        cost_per_leg: int = COST_PER_LEG) -> dict:
    """TODO(you): fly the tasks through the mission's state machine, draining battery as you go.

    For each task in order: before a transit or survey task, if battery - task_cost(...)
    would drop below reserve_pct, fire "abort" and stop. Otherwise fire EVENT_FOR_KIND[kind]
    (an out-of-order plan raises IllegalTransition; let it), subtract the task's cost, and add
    the task name to completed. return and land always run; the reserve exists for them.
    Return {"completed": [names], "final_state": mission.state, "battery": battery_left}.
    """
    raise NotImplementedError


# ------------------------------------------------------------------ CLI

DEMO_WAYPOINTS = ["north field", "pond", "ridge"]


def _print_history(mission: Mission) -> None:
    for old, event, new in mission.history:
        print(f"  {old.name:>8} --{event}--> {new.name}")


def main(argv: list[str]) -> None:
    if "--abort" in argv:
        mission = Mission()
        for event in ("launch", "depart", "abort"):
            mission.fire(event)
        _print_history(mission)
        print(f"terminal: {mission.is_terminal()}   can still launch: {can_fire(mission.state, 'launch')}")
        return
    battery = int(argv[argv.index("--battery") + 1]) if "--battery" in argv else 100
    tasks = plan_tasks(DEMO_WAYPOINTS, 100)          # planned on the ground with a full pack
    print("plan:", ", ".join(t.name for t in tasks))
    mission = Mission()
    result = run(mission, tasks, battery)            # flown with whatever the pack really had
    _print_history(mission)
    print(f"completed {len(result['completed'])}/{len(tasks)} tasks, "
          f"final state {result['final_state'].name}, battery {result['battery']}%")


if __name__ == "__main__":
    main(sys.argv[1:])
