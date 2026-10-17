"""C8 · Lambda handler: transcript in S3 -> summary JSON next to it.

Local run:  python3 handler.py events/s3_put.json --fake     (LocalStorage under local-bucket/)
Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import unquote_plus

HERE = Path(__file__).resolve().parent
for sub in ("C1", "C6", "_common"):
    sys.path.insert(0, str(HERE.parent / sub))
from ask import get_client  # noqa: E402
from summarize import summarize_transcript  # noqa: E402
from storage import LocalStorage, S3Storage  # noqa: E402


def parse_s3_event(event: dict) -> list[tuple[str, str]]:
    """TODO(you): (bucket, key) per record, key URL-decoded."""
    raise NotImplementedError


def handler(event: dict, context=None, storage=None, client=None) -> dict:
    """TODO(you): summarize each transcript in the event and write <key>.summary.json."""
    raise NotImplementedError


def main(argv: list[str]) -> None:
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        sys.exit(__doc__)
    event = json.loads(Path(paths[0]).read_text())
    local = LocalStorage(HERE / "local-bucket")
    for _bucket, key in parse_s3_event(event):
        if key not in local.list():
            local.put(key, (HERE.parent / "C6" / "data" / "standup.txt").read_bytes())
    from summarize import FAKE_MEETING
    client = get_client("--fake" in argv, responses=[FAKE_MEETING] * 5)
    print(json.dumps(handler(event, None, storage=local, client=client), indent=2))
    print("outputs:", local.list())


if __name__ == "__main__":
    main(sys.argv[1:])
