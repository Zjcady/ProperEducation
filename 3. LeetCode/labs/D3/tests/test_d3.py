import pytest

import pid
from pid import PID

WIDE = (-100.0, 100.0)      # output limits wide enough that only the term under test shows


def trace_of(temps, dt=1.0, power=0.5):
    """A hand-made trace: one (t, temp, power) row per temperature, t starting at dt."""
    return [((i + 1) * dt, float(temp), power) for i, temp in enumerate(temps)]


# ---------------------------------------------------------------- step 1

def test_step1_p_only_output_is_proportional_to_error():
    c = PID(kp=0.5, ki=0.0, kd=0.0, output_limits=WIDE)
    assert c.update(2.0, 1.0) == pytest.approx(1.0)
    assert c.update(-3.0, 1.0) == pytest.approx(-1.5)
    assert c.update(0.0, 1.0) == pytest.approx(0.0)
    assert c.update(4.0, 0.1) == pytest.approx(2.0)          # dt never touches the P term


def test_step1_integral_accumulates_error_times_dt():
    c = PID(kp=0.0, ki=0.1, kd=0.0, output_limits=WIDE)
    assert c.update(1.0, 1.0) == pytest.approx(0.1)
    assert c.update(1.0, 1.0) == pytest.approx(0.2)
    assert c.update(1.0, 0.5) == pytest.approx(0.25)         # half a second adds half as much
    assert c.update(-2.5, 1.0) == pytest.approx(0.0)         # a negative error unwinds it


def test_step1_derivative_responds_to_change_not_level():
    c = PID(kp=0.0, ki=0.0, kd=1.0, output_limits=WIDE)
    assert c.update(2.0, 1.0) == pytest.approx(0.0)          # first call: nothing to compare with
    assert c.update(5.0, 1.0) == pytest.approx(3.0)          # the error rose by 3 in one second
    assert c.update(5.0, 1.0) == pytest.approx(0.0)          # same error again: no change, no D
    assert c.update(3.0, 0.5) == pytest.approx(-4.0)         # fell by 2 in half a second


def test_step1_output_is_clamped_to_output_limits():
    c = PID(kp=1.0, ki=0.0, kd=0.0)                          # default limits are (0, 1)
    assert c.update(5.0, 1.0) == 1.0
    assert c.update(-5.0, 1.0) == 0.0
    assert c.update(0.3, 1.0) == pytest.approx(0.3)
    assert PID(kp=1.0, ki=0.0, kd=0.0, output_limits=(-2.0, 2.0)).update(-5.0, 1.0) == -2.0


def test_step1_anti_windup_clamp_holds_the_integral():
    # ki=1 so the output *is* the integral; wide output limits so only the integral clamp acts
    clamped = PID(kp=0.0, ki=1.0, kd=0.0, output_limits=WIDE, integral_limit=2.0)
    free = PID(kp=0.0, ki=1.0, kd=0.0, output_limits=WIDE)
    for _ in range(10):
        out_clamped = clamped.update(1.0, 1.0)
        out_free = free.update(1.0, 1.0)
    assert out_free == pytest.approx(10.0)
    assert out_clamped == pytest.approx(2.0)
    # when the error flips, the clamped one answers at once; the free one has 8 units of windup to burn
    assert clamped.update(-1.0, 1.0) == pytest.approx(1.0)
    assert free.update(-1.0, 1.0) == pytest.approx(9.0)
    for _ in range(10):
        clamped.update(-1.0, 1.0)
    assert clamped.update(0.0, 1.0) == pytest.approx(-2.0)   # the clamp is symmetric


def test_step1_reset_forgets_integral_and_previous_error():
    c = PID(kp=0.0, ki=1.0, kd=1.0, output_limits=WIDE)
    c.update(3.0, 1.0)
    c.update(5.0, 1.0)
    c.reset()
    fresh = PID(kp=0.0, ki=1.0, kd=1.0, output_limits=WIDE)
    assert c.update(1.0, 1.0) == pytest.approx(1.0)          # integral 1, derivative 0 (no previous)
    assert c.update(1.0, 1.0) == pytest.approx(fresh.update(1.0, 1.0) + 1.0)


def test_step1_all_three_terms_add_up():
    c = PID(kp=0.5, ki=0.1, kd=2.0, output_limits=WIDE)
    assert c.update(1.0, 1.0) == pytest.approx(0.5 + 0.1 + 0.0)
    assert c.update(2.0, 1.0) == pytest.approx(1.0 + 0.3 + 2.0)


# ---------------------------------------------------------------- step 2

def test_step2_overshoot_is_the_peak_above_setpoint_or_zero():
    assert pid.overshoot(trace_of([50, 58, 63.5, 61, 60]), 60.0) == pytest.approx(3.5)
    assert pid.overshoot(trace_of([50, 55, 58, 59.5, 59.9]), 60.0) == 0.0     # never above: 0, not negative
    assert pid.overshoot(trace_of([60, 60]), 60.0) == 0.0


def test_step2_settling_time_is_where_the_last_excursion_ends():
    # band 0.02 * 60 = 1.2: inside means 58.8 <= temp <= 61.2
    assert pid.settling_time(trace_of([50, 58, 61.5, 60.5, 59.9, 60.1, 60.0]), 60.0) == 4.0
    assert pid.settling_time(trace_of([60, 60, 65, 60, 60]), 60.0) == 4.0    # "first time inside" would say 1
    assert pid.settling_time(trace_of([60, 60.5, 59.5]), 60.0) == 1.0       # never outside: the first sample
    assert pid.settling_time(trace_of([50, 58, 61.5, 60.5], dt=0.5), 60.0) == 2.0   # t comes from the trace
    tr = trace_of([90, 102.5, 100.5, 100.0])
    assert pid.settling_time(tr, 100.0) == 3.0                              # 2.5 is outside 2% of 100
    assert pid.settling_time(tr, 100.0, band=0.05) == 2.0                   # but inside 5%


def test_step2_settling_time_is_none_when_it_never_settles():
    assert pid.settling_time(trace_of([50, 58, 61.5, 58, 61.5, 58]), 60.0) is None   # still swinging
    assert pid.settling_time(trace_of([50, 55, 57, 57.5]), 60.0) is None             # stuck short
    assert pid.settling_time(trace_of([50, 60, 60, 62]), 60.0) is None               # left the band at the end


def test_step2_steady_state_error_averages_the_tail():
    tr = trace_of([20, 30, 40, 58, 59, 60])
    assert pid.steady_state_error(tr, 60.0, last_n=3) == pytest.approx(1.0)        # mean of 2, 1, 0
    assert pid.steady_state_error(tr, 60.0, last_n=2) == pytest.approx(0.5)
    assert pid.steady_state_error(trace_of([61, 62]), 60.0) == pytest.approx(-1.5)  # above: negative; short trace: all of it


def test_step2_good_gains_settle_fast_with_little_overshoot():
    trace = pid.simulate(PID(**pid.GOOD_GAINS), pid.Heater(), pid.SETPOINT, 120, 1.0)
    assert len(trace) == 120 and all(0.0 <= power <= 1.0 for _, _, power in trace)
    assert pid.overshoot(trace, pid.SETPOINT) < 2.0
    settled = pid.settling_time(trace, pid.SETPOINT)
    assert settled is not None and settled <= 30.0
    assert abs(pid.steady_state_error(trace, pid.SETPOINT)) < 0.2


def test_step2_same_gains_without_the_integral_clamp_overshoot():
    gains = dict(pid.GOOD_GAINS, integral_limit=None)
    trace = pid.simulate(PID(**gains), pid.Heater(), pid.SETPOINT, 120, 1.0)
    assert pid.overshoot(trace, pid.SETPOINT) > 5.0


def test_step2_p_only_leaves_a_steady_state_error():
    trace = pid.simulate(PID(**pid.P_ONLY_GAINS), pid.Heater(), pid.SETPOINT, 120, 1.0)
    assert pid.steady_state_error(trace, pid.SETPOINT) > 2.0
    assert pid.settling_time(trace, pid.SETPOINT) is None
    assert pid.overshoot(trace, pid.SETPOINT) == 0.0


def test_step2_cli_writes_a_csv_and_prints_the_three_metrics(tmp_path, capsys):
    out = tmp_path / "trace.csv"
    pid.main(["--out", str(out), "--steps", "80"])
    rows = out.read_text().splitlines()
    assert rows[0] == "t,temp,power" and len(rows) == 81
    assert len(rows[1].split(",")) == 3
    printed = capsys.readouterr().out
    for word in ("overshoot", "settling_time", "steady_state_error"):
        assert word in printed
    pid.main(["--out", str(out), "--kp", "0.1", "--ki", "0", "--kd", "0"])
    assert "never" in capsys.readouterr().out
