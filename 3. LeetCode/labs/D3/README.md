# D3 · PID controller in simulation

**Maps to:** the responsibilities paragraph: "perception, motion/mission planning, controls". This lab is the controls line: the feedback loop that holds a heater, a motor speed or a heading where the planner asked for it.
**You'll have at the end:** a PID controller with output clamping and anti-windup, a simulated heater to run it against, and the three numbers engineers use to say whether a response is good: overshoot, settling time and steady-state error. Every run leaves a CSV you can plot or paste into a spreadsheet.

Setup: `pip install -r requirements.txt` (pure Python; pytest is the only dependency). Tests are offline. `python3 pid.py` runs the good gains and prints the three metrics once your functions work.

**What a PID is, in one sentence.** Every step, take the error (setpoint minus measurement) and push with three things added together: how big the error is right now (P), how long it has been there (I), and how fast it is changing (D).

Read `pid.py` first. `Heater` is the plant: each step `temp += (power*gain - (temp - ambient)*loss) * dt`, so it warms with the power you give it and always leaks heat toward ambient. `simulate` runs the loop: it computes the error, calls your `controller.update(error, dt)`, clamps the power to `[0, 1]`, steps the plant, and records one `(t, temp, power)` row per step. `clamp` and `write_csv` are done. Holding 60 C takes power 0.5 forever; keep that number in mind.

## Step 1 · The controller  (15 min)

You write `PID.reset` and `PID.update`:

- `reset()`: `self.integral = 0.0`, `self.prev_error = None`. `__init__` calls it, so this is where the state is born.
- `update(error, dt)`: four lines, in this order. Add `error * dt` to the integral, and if `integral_limit` is set clamp the integral to `[-limit, +limit]` (that is the anti-windup). Derivative is `(error - prev_error) / dt`, or `0.0` on the first call when there is no previous error. Remember this error. Return `kp*error + ki*integral + kd*derivative` clamped to `output_limits`.

Why the integral clamp: while the heater is far from 60 the output is pinned at full power anyway, but the integral keeps growing the whole time. Without a clamp it is huge by the time the error reaches zero, and the plant sails past the setpoint until the integral unwinds. The tests in this step check each term alone, with wide output limits, so the arithmetic is bare. `dt` is in both the I and D terms; the P term never sees it.

## Step 2 · Measuring the response  (15 min)

You write `overshoot`, `settling_time` and `steady_state_error`. A trace is the list `simulate` returns; the metrics only look at the `temp` column and the `t` column.

- `overshoot(trace, setpoint)`: the hottest sample minus the setpoint, floored at `0.0`. A trace that never crosses has zero overshoot, not a negative one.
- `settling_time(trace, setpoint, band=0.02)`: inside means within `band * setpoint` of the setpoint (1.2 C for 60). Walk the trace backwards; the last sample outside the band is the last excursion, and the `t` of the sample after it is the answer. If every sample is inside, it is the first sample's `t`. If the last sample is outside, the plant never settled: `None`. "First time it enters the band" is the wrong answer, and the test has a trace that proves it.
- `steady_state_error(trace, setpoint, last_n=10)`: the mean of `setpoint - temp` over the last `last_n` samples (all of them if the trace is shorter). Positive means the plant sits short of the setpoint.

Now run three things and read the numbers: `python3 pid.py`, then `python3 pid.py --kp 0.1 --ki 0 --kd 0`, then `python3 pid.py --no-integral-limit`. Be ready to say why P-only stops about 4.4 C short (at steady state `kp*error*gain` has to equal `loss*(temp - ambient)`; solve for the error), and why the same gains overshoot by more than ten degrees without the clamp. If you have time, try `--kd 0.5` and watch the power chatter between 0 and 1: at `dt=1` the derivative over-corrects a step it only sees one sample late. Then rubric review and `python3 coach.py done D3`.
