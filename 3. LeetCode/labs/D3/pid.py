"""D3 · A PID controller against a simulated heater.

    python3 pid.py                              the good gains: the three metrics, trace in out/trace.csv
    python3 pid.py --kp 0.1 --ki 0 --kd 0       P-only: watch the steady-state error
    python3 pid.py --no-integral-limit          the good gains without anti-windup: watch the overshoot
    python3 pid.py --kp 0.3 --ki 0.02 --kd 0.5  your own gains (this set chatters; see why in the README)

Pure Python, no numpy. The plant is a heater: every step its temperature rises with the power
you apply and falls toward ambient. Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
Trace = list[tuple[float, float, float]]        # one (t, temp, power) row per step

AMBIENT = 20.0
SETPOINT = 60.0
# Gains the tests use. The integral clamp matters: run --no-integral-limit and compare.
GOOD_GAINS = {"kp": 0.1, "ki": 0.01, "kd": 0.05, "integral_limit": 60.0}
P_ONLY_GAINS = {"kp": 0.1, "ki": 0.0, "kd": 0.0}


# ------------------------------------------------------------------ scaffolding

def clamp(x: float, lo: float, hi: float) -> float:
    """x limited to [lo, hi]."""
    return max(lo, min(hi, x))


class Heater:
    """A first-order plant. power in [0, 1] heats it; it always cools toward ambient.

        temp += (power * gain - (temp - ambient) * loss) * dt

    Holding 60 C with ambient 20, gain 4 and loss 0.05 takes power 0.5 forever. That 0.5 is the
    number the integral term has to find, because at zero error the P term asks for nothing.
    """

    def __init__(self, gain: float = 4.0, loss: float = 0.05, ambient: float = AMBIENT,
                 temp: float = AMBIENT):
        self.gain = gain
        self.loss = loss
        self.ambient = ambient
        self.temp = temp

    def step(self, power: float, dt: float) -> float:
        """Advance one step with this much power applied; return the new temperature."""
        self.temp += (power * self.gain - (self.temp - self.ambient) * self.loss) * dt
        return self.temp


def simulate(controller, plant, setpoint: float, steps: int, dt: float = 1.0) -> Trace:
    """Run the loop: error -> controller.update(error, dt) -> clamp power to [0, 1] -> plant.step.

    Row i is (t, temp, power): the time after step i (t = (i + 1) * dt), the temperature the plant
    reached, and the power that was applied to get there.
    """
    trace: Trace = []
    for i in range(steps):
        error = setpoint - plant.temp
        power = clamp(controller.update(error, dt), 0.0, 1.0)
        plant.step(power, dt)
        trace.append(((i + 1) * dt, plant.temp, power))
    return trace


def write_csv(trace: Trace, path: str | Path) -> None:
    """The trace as CSV with a t,temp,power header. Creates the folder if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t", "temp", "power"])
        writer.writerows(trace)


# ------------------------------------------------------------------ step 1

class PID:
    """Proportional, integral, derivative: output = kp*e + ki*sum(e*dt) + kd*de/dt, then clamped.

    State lives in two attributes that reset() creates: `integral` (the running sum of error*dt)
    and `prev_error` (the error from the last update, None before the first one).
    """

    def __init__(self, kp: float, ki: float, kd: float,
                 output_limits: tuple[float, float] = (0.0, 1.0),
                 integral_limit: float | None = None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        self.integral_limit = integral_limit
        self.reset()

    def reset(self) -> None:
        """TODO(you): forget the past: self.integral = 0.0 and self.prev_error = None."""
        raise NotImplementedError

    def update(self, error: float, dt: float) -> float:
        """TODO(you): one controller step; return the clamped output.

        1. integral += error * dt. If integral_limit is set, clamp the integral to
           [-integral_limit, +integral_limit]. That clamp is the anti-windup.
        2. derivative = (error - prev_error) / dt, or 0.0 on the first call (prev_error is None).
        3. Remember this error as prev_error.
        4. output = kp * error + ki * integral + kd * derivative, clamped to output_limits.
        """
        raise NotImplementedError


# ------------------------------------------------------------------ step 2

def overshoot(trace: Trace, setpoint: float) -> float:
    """TODO(you): how far the hottest sample went above the setpoint; 0.0 if it never did."""
    raise NotImplementedError


def settling_time(trace: Trace, setpoint: float, band: float = 0.02) -> float | None:
    """TODO(you): the t of the first sample from which every later sample (that one included) stays
    within band * setpoint of the setpoint. None if the last sample is outside: it never settled.

    Walk the trace backwards. The last sample outside the band is the last excursion; the sample
    after it is where the plant settled. If no sample is ever outside, that is the first sample's t.
    """
    raise NotImplementedError


def steady_state_error(trace: Trace, setpoint: float, last_n: int = 10) -> float:
    """TODO(you): the mean of (setpoint - temp) over the last last_n samples (all of them if the
    trace is shorter). Positive means the plant sits below the setpoint."""
    raise NotImplementedError


# ------------------------------------------------------------------ CLI

def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kp", type=float, default=GOOD_GAINS["kp"])
    ap.add_argument("--ki", type=float, default=GOOD_GAINS["ki"])
    ap.add_argument("--kd", type=float, default=GOOD_GAINS["kd"])
    ap.add_argument("--integral-limit", type=float, default=GOOD_GAINS["integral_limit"])
    ap.add_argument("--no-integral-limit", action="store_true", help="switch the anti-windup clamp off")
    ap.add_argument("--setpoint", type=float, default=SETPOINT)
    ap.add_argument("--steps", type=int, default=120)
    ap.add_argument("--dt", type=float, default=1.0)
    ap.add_argument("--out", default=str(HERE / "out" / "trace.csv"), help="where the CSV goes")
    args = ap.parse_args(argv)

    limit = None if args.no_integral_limit else args.integral_limit
    controller = PID(args.kp, args.ki, args.kd, integral_limit=limit)
    trace = simulate(controller, Heater(), args.setpoint, args.steps, args.dt)
    write_csv(trace, args.out)
    print(f"gains: kp={args.kp:g} ki={args.ki:g} kd={args.kd:g} integral_limit={limit}")
    print(f"final temp {trace[-1][1]:.2f} C at power {trace[-1][2]:.2f}; {len(trace)} rows -> {args.out}")
    try:
        settled = settling_time(trace, args.setpoint)
        print(f"overshoot:           {overshoot(trace, args.setpoint):.2f} C")
        print(f"settling_time:       {'never' if settled is None else f'{settled:g} s'}")
        print(f"steady_state_error:  {steady_state_error(trace, args.setpoint):.3f} C")
    except NotImplementedError:
        print("metrics: finish step 2 to see overshoot, settling_time and steady_state_error")


if __name__ == "__main__":
    main(sys.argv[1:])
