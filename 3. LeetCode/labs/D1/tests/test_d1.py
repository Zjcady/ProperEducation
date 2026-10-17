import pytest

import mission
from mission import AIRBORNE, TRANSITIONS, IllegalTransition, Mission, State, Task

EVENTS = ("launch", "depart", "arrived", "return_home", "landed", "abort")
FULL_FLIGHT = [("launch", State.TAKEOFF), ("depart", State.TRANSIT), ("arrived", State.SURVEY),
               ("depart", State.TRANSIT), ("arrived", State.SURVEY),
               ("return_home", State.RETURN), ("landed", State.LANDED)]


# ---------------------------------------------------------------- step 1

def test_step1_fire_walks_the_table_through_a_full_flight():
    m = Mission()
    assert m.state is State.IDLE
    for event, expected in FULL_FLIGHT:
        assert m.fire(event) is expected
        assert m.state is expected
    assert m.state is State.LANDED


def test_step1_abort_is_allowed_from_every_airborne_state_and_nowhere_else():
    for state in AIRBORNE:
        assert mission.can_fire(state, "abort"), f"abort must be legal from {state.name}"
        m = Mission(state)
        assert m.fire("abort") is State.ABORTED
    for state in (State.IDLE, State.LANDED, State.ABORTED):
        assert not mission.can_fire(state, "abort"), f"nothing to abort in {state.name}"
        with pytest.raises(IllegalTransition):
            Mission(state).fire("abort")


def test_step1_illegal_transition_raises_and_changes_nothing():
    m = Mission()
    with pytest.raises(IllegalTransition) as exc:
        m.fire("arrived")                      # can't arrive before launching
    assert "IDLE" in str(exc.value) and "arrived" in str(exc.value)
    assert m.state is State.IDLE and m.history == []
    m.fire("launch")
    with pytest.raises(IllegalTransition):
        m.fire("landed")                       # can't land straight out of takeoff
    assert m.state is State.TAKEOFF and len(m.history) == 1
    with pytest.raises(IllegalTransition):
        m.fire("liftoff")                      # not an event at all


def test_step1_history_records_every_transition_in_order():
    m = Mission()
    for event in ("launch", "depart", "arrived"):
        m.fire(event)
    assert m.history == [(State.IDLE, "launch", State.TAKEOFF),
                         (State.TAKEOFF, "depart", State.TRANSIT),
                         (State.TRANSIT, "arrived", State.SURVEY)]
    m.fire("abort")
    assert m.history[-1] == (State.SURVEY, "abort", State.ABORTED)
    assert len(m.history) == 4


def test_step1_is_terminal_and_nothing_fires_after_it():
    m = Mission()
    assert not m.is_terminal()
    for event, _ in FULL_FLIGHT:
        assert not m.is_terminal()
        m.fire(event)
    assert m.is_terminal()
    for event in EVENTS:
        with pytest.raises(IllegalTransition):
            m.fire(event)
    aborted = Mission(State.TRANSIT)
    aborted.fire("abort")
    assert aborted.is_terminal()
    assert not Mission(State.RETURN).is_terminal()


def test_step1_can_fire_agrees_with_the_table_for_every_pair():
    for state in State:
        for event in EVENTS + ("liftoff",):
            assert mission.can_fire(state, event) == ((state, event) in TRANSITIONS)
    assert mission.can_fire(State.SURVEY, "depart")           # next waypoint
    assert mission.can_fire(State.SURVEY, "return_home")      # or go home
    assert not mission.can_fire(State.RETURN, "arrived")      # no survey on the way home
    assert not mission.can_fire(State.IDLE, "landed")


# ---------------------------------------------------------------- step 2

def names(tasks):
    return [t.name for t in tasks]


def test_step2_plan_covers_two_waypoints_on_a_full_battery():
    tasks = mission.plan_tasks(["A", "B"], 100)
    assert all(isinstance(t, Task) for t in tasks)
    assert names(tasks) == ["takeoff", "transit to A", "survey A", "transit to B", "survey B",
                            "return", "land"]
    assert [t.kind for t in tasks] == ["takeoff", "transit", "survey", "transit", "survey",
                                       "return", "land"]
    assert [t.waypoint for t in tasks] == [None, "A", "A", "B", "B", None, None]


def test_step2_plan_drops_waypoints_the_battery_cannot_cover():
    # 100 - 20 reserve - 15 return leg = 65 spendable; each waypoint is 30, so two fit, not three
    tasks = mission.plan_tasks(["A", "B", "C"], 100)
    assert names(tasks) == ["takeoff", "transit to A", "survey A", "transit to B", "survey B",
                            "return", "land"]
    assert mission.plan_tasks(["A", "B", "C", "D", "E"], 100) == tasks


def test_step2_plan_respects_the_exact_budget_boundary():
    # 65 - 20 - 15 = 30: exactly one waypoint fits. One percent less and none does.
    assert names(mission.plan_tasks(["A", "B"], 65)) == ["takeoff", "transit to A", "survey A",
                                                         "return", "land"]
    assert names(mission.plan_tasks(["A", "B"], 64)) == ["takeoff", "return", "land"]
    # the reserve is real battery you may not spend
    assert len(mission.plan_tasks(["A", "B"], 80, reserve_pct=20)) == 5    # one waypoint
    assert len(mission.plan_tasks(["A", "B"], 80, reserve_pct=5)) == 7     # two waypoints
    # cheaper legs, more waypoints: 100 - 20 - 10 = 70, each waypoint 20 -> three of four
    assert names(mission.plan_tasks(["A", "B", "C", "D"], 100, cost_per_leg=10))[1:-2] == [
        "transit to A", "survey A", "transit to B", "survey B", "transit to C", "survey C"]


def test_step2_plan_always_starts_with_takeoff_and_ends_with_return_then_land():
    for battery in (0, 30, 50, 100):
        tasks = mission.plan_tasks(["A", "B", "C"], battery)
        assert tasks[0] == Task("takeoff", "takeoff")
        assert tasks[-2:] == [Task("return", "return"), Task("land", "land")]
        assert len(tasks) % 2 == 1          # takeoff + pairs + return + land
    assert names(mission.plan_tasks([], 100)) == ["takeoff", "return", "land"]


def test_step2_run_completes_a_two_waypoint_mission_with_ample_battery():
    tasks = mission.plan_tasks(["A", "B"], 100)
    m = Mission()
    result = mission.run(m, tasks, 100)
    assert result == {"completed": names(tasks), "final_state": State.LANDED, "battery": 25}
    assert m.state is State.LANDED and m.is_terminal()
    assert [h[1] for h in m.history] == ["launch", "depart", "arrived", "depart", "arrived",
                                         "return_home", "landed"]


def test_step2_run_aborts_with_scarce_battery_before_eating_the_reserve():
    tasks = mission.plan_tasks(["A", "B"], 100)        # planned for a full pack...
    m = Mission()
    result = mission.run(m, tasks, 40)                   # ...flown on 40%
    # takeoff is free (40), transit to A costs 15 (25), survey A would leave 10 < 20: abort
    assert result == {"completed": ["takeoff", "transit to A"], "final_state": State.ABORTED,
                      "battery": 25}
    assert m.history[-1] == (State.TRANSIT, "abort", State.ABORTED)
    assert len(m.history) == 3
    # on 10% it aborts right after takeoff: the first leg itself would go below reserve
    result = mission.run(Mission(), tasks, 10)
    assert result["completed"] == ["takeoff"] and result["final_state"] is State.ABORTED
    assert result["battery"] == 10


def test_step2_run_never_aborts_a_plan_made_for_the_same_battery():
    waypoints = ["A", "B", "C", "D"]
    for battery in range(35, 101, 5):
        tasks = mission.plan_tasks(waypoints, battery)
        result = mission.run(Mission(), tasks, battery)
        assert result["final_state"] is State.LANDED, battery
        assert result["battery"] >= 20, battery
        assert result["completed"] == names(tasks)


def test_step2_run_refuses_a_plan_the_machine_cannot_follow():
    m = Mission()
    with pytest.raises(IllegalTransition):
        mission.run(m, [Task("survey A", "survey", "A")], 100)   # survey before launch
    assert m.state is State.IDLE
    with pytest.raises(IllegalTransition):
        mission.run(Mission(), [Task("takeoff", "takeoff"), Task("land", "land")], 100)
