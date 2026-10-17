# D5 · A tiny human-machine interface

**Maps to:** the responsibilities paragraph: "perception, motion/mission planning, controls", "breaking missions into tasks" and "human-machine interfaces". This lab is the human-machine interface line: the screen an operator watches, and the two buttons that matter.
**You'll have at the end:** an operator console for the D1 mission: a small HTTP API that reports the mission as JSON and takes two commands, and a web page that polls it once a second, highlights the task that is waiting, lets a human approve it, and keeps Abort one click away the whole time. Standard library only: `http.server` for the API, one page of plain HTML and JavaScript for the console, `urllib` in the tests.

Setup: `pip install -r requirements.txt` (only pytest). Pure Python, offline. The tests never open a browser; you will, once, at the end of step 2.

**What an HMI is, in one sentence.** The place where the machine shows a human what it is about to do and waits for permission, and where the human can always say stop.

Read `hmi.py` first. `Console` is the mission as the operator sees it, kept deliberately smaller than D1 so this lab stands alone: a list of task names, `current` (the index of the task waiting for approval), one `state` word (`ready`, `complete` or `aborted`), a `log`, and a lock, because the page polls while the operator clicks. `Handler` is one `BaseHTTPRequestHandler` per request; `send_json` and `send_html` write a complete response (status line, Content-Type, Content-Length, body), so your routing is an `if` on the path and nothing more. `ConsoleServer`, `start_server(port=0)` and `stop_server` are done: the tests start a server on a free port, talk to it with `urllib`, and stop it.

## Step 1 · The API  (15 min)

You write the model's three methods and the handler's two: `Console.snapshot`, `Console.approve`, `Console.abort`, `Handler.do_GET`, `Handler.do_POST`.

- `snapshot()`: the five-key dict the page is written against: `state`, `tasks` (a copy), `current`, `awaiting_approval` (True only while `state == "ready"`) and `log` (a copy). `json.dumps` must swallow it whole.
- `approve()`: under `self.lock`. Not `ready`: log `approve ignored: mission <state>` and change nothing else. Otherwise log `running: <task>` then `done: <task>` for `tasks[current]`, move `current` on by one, and if that was the last task set `state` to `complete` and log `mission complete`. Return `snapshot()` either way.
- `abort()`: under `self.lock`. `state = "aborted"`, log `ABORT by operator`, leave `current` alone so the page still shows which task was next. Return `snapshot()`. Abort always wins; there is no state in which it is ignored.
- `do_GET`: `path = self.path.split("?")[0]`. `/` serves `index.html` with `send_html`; `/state` sends `snapshot()` with `send_json(200, ...)`; anything else is `send_json(404, {"error": ...})`.
- `do_POST`: same shape. `/approve` and `/abort` call the console and send back whatever it returns; anything else is a 404. The request body is ignored; the buttons send none.

Why does the page get `awaiting_approval` when it could work that out from `state`? Because the page should be dumb: one boolean decides whether Approve is clickable, and the server owns the rule. Try it: `python3 hmi.py --demo` drives the API with `urllib` and prints each reply. Read the last log line after the abort, and after the approve that follows it.

## Step 2 · The console page  (15 min)

Open `index.html`. The HTML and CSS are done: a state badge `#state`, an empty list `#tasks`, the two buttons `#approve` (starts disabled) and `#abort`, and a `#log` box. The `<script>` block is yours; the `TODO(you)` comment inside it says what to write and must be gone when you are done.

- Look up the five elements once with `document.getElementById`.
- `render(s)`: `s` is the parsed JSON from `/state`. Put `s.state` in the badge, and set it as the badge's `className` too so the CSS colours it. Empty `#tasks` and rebuild it with one `<li>` per name: class `done` for indexes below `s.current`, class `current` for `s.current` while `s.awaiting_approval`. `approve.disabled = !s.awaiting_approval`. The log is `s.log.join("\n")`.
- `poll()`: `fetch("/state")`, `await response.json()`, `render` it. Call it once at load, then `setInterval(poll, 1000)`.
- Clicks: Approve does `fetch("/approve", {method: "POST"})` and renders the reply; Abort does the same with `/abort`. Rendering the reply straight away means the screen changes on the click, not up to a second later on the next poll.

There is no browser in the tests, so the step 2 tests are structural: `GET /` serves the file as `text/html`, the script (comments stripped) touches every element id, polls `/state` on a one-second interval, POSTs to `/approve` and `/abort`, and has no `TODO(you)` left; and the approve and abort flows, driven through the API, change what the page would show. Then look at it for real: `python3 hmi.py`, open http://127.0.0.1:8765/, approve the whole mission once. Ctrl-C, start it again, abort it halfway, and watch the log and the badge. Then rubric review and `python3 coach.py done D5`.
