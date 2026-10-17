"""D5 · A tiny human-machine interface: an HTTP API over a mission, and a page that polls it.

    python3 hmi.py                 serve the console on http://127.0.0.1:8765/  (Ctrl-C stops it)
    python3 hmi.py --port 0        same, on a free port (printed)
    python3 hmi.py --demo          no browser: drive the API with urllib and print every reply

The mission here is the D1 plan as the operator sees it: a list of task names, which one is
next, one state word, and a log. Nothing runs by itself. Every task waits for a human to press
Approve, and Abort is always one click away.

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
INDEX_HTML = HERE / "index.html"
DEFAULT_PORT = 8765

# The D1 demo plan on a full battery, names only. The HMI never needs more than the names.
DEMO_TASKS = ["takeoff", "transit to north field", "survey north field",
              "transit to pond", "survey pond", "return", "land"]

STATES = ("ready", "complete", "aborted")     # ready = a task is waiting for Approve


# ------------------------------------------------------------------ step 1 scaffolding: the model

class Console:
    """The mission as the operator sees it. One per server; every request thread shares it."""

    def __init__(self, tasks: list[str] | None = None):
        self.tasks: list[str] = list(DEMO_TASKS if tasks is None else tasks)
        self.current: int = 0                               # index of the task waiting for approval
        self.state: str = "ready" if self.tasks else "complete"
        self.log: list[str] = [f"mission loaded: {len(self.tasks)} tasks"]
        self.lock = threading.RLock()                       # the page polls while the operator clicks

    def snapshot(self) -> dict:
        """TODO(you): the JSON the page needs, as a plain dict.

        Keys, exactly these five: "state" (self.state), "tasks" (a copy of the list), "current"
        (the index), "awaiting_approval" (True only while state is "ready") and "log" (a copy).
        Nothing else; the page is written against these five names.
        """
        raise NotImplementedError

    def approve(self) -> dict:
        """TODO(you): the operator pressed Approve. Run the current task and return snapshot().

        Hold self.lock. If state is not "ready" (complete or aborted), append
        "approve ignored: mission <state>" to the log and change nothing else. Otherwise take
        task = self.tasks[self.current], append "running: <task>" then "done: <task>" to the
        log, and move self.current forward by one. If that was the last task, set state to
        "complete" and append "mission complete". Return snapshot() either way.
        """
        raise NotImplementedError

    def abort(self) -> dict:
        """TODO(you): the operator pressed Abort. It always wins. Return snapshot().

        Hold self.lock. Set state to "aborted" and append "ABORT by operator" to the log,
        whatever the state was. self.current stays where it is, so the page still shows which
        task was next. Return snapshot().
        """
        raise NotImplementedError


# ------------------------------------------------------------------ step 1 scaffolding: the server

class Handler(BaseHTTPRequestHandler):
    """One instance per request. self.console is the Console every request shares."""

    @property
    def console(self) -> Console:
        return self.server.console

    def send_json(self, status: int, payload: dict) -> None:
        """A complete JSON response: status line, Content-Type, Content-Length, body."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, text: str) -> None:
        """A complete 200 text/html response."""
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args) -> None:
        """One line per request on stderr, only when the server was started verbose."""
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    def do_GET(self) -> None:
        """TODO(you): route a GET by path. path = self.path.split("?")[0] (the page may add ?t=...).

        "/"      -> send_html(INDEX_HTML.read_text(encoding="utf-8"))      the console page
        "/state" -> send_json(200, self.console.snapshot())
        else     -> send_json(404, {"error": f"no such path: {path}"})
        """
        raise NotImplementedError

    def do_POST(self) -> None:
        """TODO(you): route a POST by path. path = self.path.split("?")[0]. The body is ignored.

        "/approve" -> send_json(200, self.console.approve())
        "/abort"   -> send_json(200, self.console.abort())
        else       -> send_json(404, {"error": f"no such path: {path}"})
        """
        raise NotImplementedError


class ConsoleServer(ThreadingHTTPServer):
    """ThreadingHTTPServer that carries the one Console every Handler shares."""
    daemon_threads = True
    request_queue_size = 16      # the default backlog of 5 drops connections when several pollers arrive at once

    def __init__(self, address: tuple[str, int], console: Console, verbose: bool = False):
        super().__init__(address, Handler)
        self.console = console
        self.verbose = verbose


def start_server(port: int = 0, tasks: list[str] | None = None,
                 verbose: bool = False) -> tuple[ConsoleServer, threading.Thread, int]:
    """Serve on 127.0.0.1:<port> in a background thread; port 0 picks a free one.

    Returns (server, thread, port). The tests call this, talk to the port with urllib, then
    call stop_server.
    """
    server = ConsoleServer(("127.0.0.1", port), Console(tasks), verbose)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05},
                              name="hmi-server", daemon=True)
    thread.start()
    return server, thread, server.server_address[1]


def stop_server(server: ConsoleServer, thread: threading.Thread) -> None:
    """Stop serving, close the socket, wait for the thread."""
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


# ------------------------------------------------------------------ CLI

DEMO_CALLS = [("GET", "/state"), ("POST", "/approve"), ("POST", "/approve"), ("POST", "/abort"),
              ("POST", "/approve"), ("GET", "/nope")]


def call(base: str, method: str, path: str) -> dict:
    """A one-line urllib client: GET or POST base+path and parse the JSON reply, 404s included."""
    try:
        with urlopen(Request(base + path, method=method), timeout=5) as resp:
            return json.loads(resp.read())
    except HTTPError as err:
        return json.loads(err.read())


def _describe(reply: dict) -> str:
    if "error" in reply:
        return f"404 {reply['error']}"
    return (f"{reply['state']:9} current={reply['current']} "
            f"awaiting_approval={str(reply['awaiting_approval']):5} | {reply['log'][-1]}")


def main(argv: list[str]) -> None:
    port = int(argv[argv.index("--port") + 1]) if "--port" in argv else DEFAULT_PORT
    if "--demo" in argv:
        server, thread, port = start_server(0)
        base = f"http://127.0.0.1:{port}"
        try:
            for method, path in DEMO_CALLS:
                print(f"{method:4} {path:9} -> {_describe(call(base, method, path))}")
        finally:
            stop_server(server, thread)
        return
    server = ConsoleServer(("127.0.0.1", port), Console(), verbose=True)
    print(f"operator console at http://127.0.0.1:{server.server_address[1]}/   (Ctrl-C stops it)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main(sys.argv[1:])
