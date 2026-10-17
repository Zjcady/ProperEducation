import json
import re
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

import hmi
from hmi import DEMO_TASKS, Console

LAB = Path(__file__).resolve().parents[1]
INDEX = LAB / "index.html"
FIELDS = {"state", "tasks", "current", "awaiting_approval", "log"}
ELEMENTS = ("state", "tasks", "approve", "abort", "log")


def http(base, method, path):
    """(status, content_type, body) for one request. A 404 is a reply here, not an exception."""
    try:
        with urlopen(Request(base + path, method=method), timeout=5) as resp:
            raw, status, ctype = resp.read(), resp.status, resp.headers.get("Content-Type", "")
    except HTTPError as err:
        raw, status, ctype = err.read(), err.code, err.headers.get("Content-Type", "")
    body = json.loads(raw) if ctype.startswith("application/json") else raw.decode("utf-8")
    return status, ctype, body


@pytest.fixture
def server():
    srv, thread, port = hmi.start_server(0, ["takeoff", "survey A", "land"])
    try:
        yield f"http://127.0.0.1:{port}", srv.console
    finally:
        hmi.stop_server(srv, thread)


# ---------------------------------------------------------------- step 1

def test_step1_snapshot_is_the_five_key_contract():
    c = Console(["takeoff", "land"])
    snap = c.snapshot()
    assert set(snap) == FIELDS
    assert snap["state"] == "ready" and snap["current"] == 0 and snap["awaiting_approval"] is True
    assert snap["tasks"] == ["takeoff", "land"] and snap["log"] == ["mission loaded: 2 tasks"]
    json.dumps(snap)                                     # the page gets exactly this
    snap["tasks"].append("x")
    snap["log"].clear()
    assert c.tasks == ["takeoff", "land"] and c.log      # copies, not the live lists
    assert Console().snapshot()["tasks"] == DEMO_TASKS


def test_step1_approve_runs_the_current_task_and_moves_the_index():
    c = Console(["takeoff", "survey A", "land"])
    snap = c.approve()
    assert snap == c.snapshot()
    assert snap["current"] == 1 and snap["state"] == "ready" and snap["awaiting_approval"] is True
    assert snap["log"][-2:] == ["running: takeoff", "done: takeoff"]
    c.approve()
    snap = c.approve()
    assert snap["current"] == 3 and snap["state"] == "complete"
    assert snap["awaiting_approval"] is False
    assert snap["log"][-3:] == ["running: land", "done: land", "mission complete"]


def test_step1_approve_after_the_end_changes_nothing_but_the_log():
    c = Console(["takeoff"])
    c.approve()
    before = c.snapshot()
    after = c.approve()
    assert after["current"] == 1 and after["state"] == "complete"
    assert after["log"] == before["log"] + ["approve ignored: mission complete"]


def test_step1_abort_always_wins_and_approve_is_ignored_after_it():
    c = Console(["takeoff", "survey A", "land"])
    c.approve()
    snap = c.abort()
    assert snap["state"] == "aborted" and snap["awaiting_approval"] is False
    assert snap["current"] == 1                          # the page still shows which task was next
    assert snap["log"][-1] == "ABORT by operator"
    snap = c.approve()
    assert snap["current"] == 1 and snap["state"] == "aborted"
    assert snap["log"][-1] == "approve ignored: mission aborted"
    done = Console(["takeoff"])
    done.approve()
    assert done.abort()["state"] == "aborted"            # abort even beats complete


def test_step1_get_state_is_json_with_the_contract_fields(server):
    base, console = server
    status, ctype, body = http(base, "GET", "/state")
    assert status == 200 and ctype == "application/json"
    assert body == console.snapshot()
    assert set(body) == FIELDS and body["tasks"] == ["takeoff", "survey A", "land"]
    assert http(base, "GET", "/state?t=1")[0] == 200     # a cache-busting query string is fine


def test_step1_post_approve_and_abort_return_the_new_state(server):
    base, console = server
    status, ctype, body = http(base, "POST", "/approve")
    assert status == 200 and ctype == "application/json"
    assert body["current"] == 1 and body["log"][-1] == "done: takeoff"
    assert console.current == 1                          # the server's console moved, not a copy
    status, ctype, body = http(base, "POST", "/abort")
    assert status == 200 and ctype == "application/json"
    assert body["state"] == "aborted" and body["awaiting_approval"] is False
    assert http(base, "GET", "/state")[2] == body        # the next poll sees the same thing


def test_step1_unknown_paths_are_404_json(server):
    base, _ = server
    for method, path in (("GET", "/nope"), ("GET", "/approve"), ("POST", "/state"), ("POST", "/launch")):
        status, ctype, body = http(base, method, path)
        assert status == 404, (method, path)
        assert ctype == "application/json", (method, path)
        assert list(body) == ["error"] and isinstance(body["error"], str), (method, path)


def test_step1_many_polls_in_flight_do_not_trip_the_server(server):
    base, _ = server
    statuses = []

    def poll():
        for _ in range(5):
            statuses.append(http(base, "GET", "/state")[0])

    pollers = [threading.Thread(target=poll) for _ in range(6)]
    for t in pollers:
        t.start()
    for _ in range(3):
        assert http(base, "POST", "/approve")[0] == 200
    for t in pollers:
        t.join(timeout=5)
    assert statuses == [200] * 30
    assert http(base, "GET", "/state")[2]["state"] == "complete"


# ---------------------------------------------------------------- step 2

def script_of(page: str) -> str:
    """The code inside the <script> block, with comments removed."""
    m = re.search(r"<script>(.*?)</script>", page, re.S)
    assert m, "index.html must keep its <script> block"
    code = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    return re.sub(r"^\s*//.*$", "", code, flags=re.M)


def test_step2_page_is_served_as_html_at_root(server):
    base, _ = server
    status, ctype, body = http(base, "GET", "/")
    assert status == 200 and ctype.startswith("text/html")
    assert body == INDEX.read_text(encoding="utf-8")
    assert "TODO(you)" not in body


def test_step2_script_has_no_todo_left_and_touches_every_element():
    page = INDEX.read_text(encoding="utf-8")
    for el in ELEMENTS:
        assert f'id="{el}"' in page, f"keep the #{el} element"
    script = script_of(page)
    assert "TODO(you)" not in script
    for el in ELEMENTS:
        pattern = rf"""getElementById\(\s*["']{el}["']\s*\)|querySelector\(\s*["']#{el}["']\s*\)"""
        assert re.search(pattern, script), f"the script never looks up #{el}"


def test_step2_script_polls_state_every_second():
    script = script_of(INDEX.read_text(encoding="utf-8"))
    assert re.search(r"""fetch\(\s*["']/state["']""", script), "poll with fetch('/state')"
    assert re.search(r"setInterval\(", script), "setInterval(poll, 1000)"
    assert "1000" in script, "once a second is 1000 ms"
    assert "awaiting_approval" in script and re.search(r"\.disabled\s*=", script), \
        "Approve is enabled or disabled from awaiting_approval"


def test_step2_script_posts_approve_and_abort():
    script = script_of(INDEX.read_text(encoding="utf-8"))
    assert re.search(r"fetch\(", script)
    for path in ("/approve", "/abort"):
        assert re.search(rf"""["']{path}["']""", script), f"no request to {path}"
    assert re.search(r"""method\s*:\s*["']POST["']""", script), "approve and abort are POSTs"


def test_step2_approve_flow_changes_what_the_page_shows(server):
    base, _ = server
    seen = [http(base, "GET", "/state")[2]]
    while seen[-1]["awaiting_approval"]:
        seen.append(http(base, "POST", "/approve")[2])
        assert len(seen) <= 10, "approve never reached complete"
    assert [s["current"] for s in seen] == [0, 1, 2, 3]
    assert [s["state"] for s in seen] == ["ready", "ready", "ready", "complete"]
    # the highlighted task walks down the list, then the Approve button goes grey
    assert [s["tasks"][s["current"]] for s in seen[:-1]] == ["takeoff", "survey A", "land"]
    assert seen[-1]["awaiting_approval"] is False
    assert seen[-1]["log"][-1] == "mission complete"
    assert http(base, "GET", "/state")[2] == seen[-1]    # the next poll agrees with the last reply


def test_step2_abort_flow_greys_out_approve_for_good(server):
    base, _ = server
    http(base, "POST", "/approve")
    body = http(base, "POST", "/abort")[2]
    assert body["state"] == "aborted" and body["awaiting_approval"] is False
    assert body["current"] == 1 and body["log"][-1] == "ABORT by operator"
    # the page keeps polling; every poll says the same thing and Approve stays grey
    for _ in range(3):
        polled = http(base, "GET", "/state")[2]
        assert polled["state"] == "aborted" and polled["awaiting_approval"] is False
    assert http(base, "POST", "/approve")[2]["current"] == 1
