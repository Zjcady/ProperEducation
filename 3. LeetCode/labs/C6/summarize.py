"""C6 · Meeting summarizer and gecko content pack.

    python3 summarize.py data/standup.txt                      meeting summary -> out/standup.summary.json
    python3 summarize.py --mode gecko data/gecko-clip.json     captions + srt   -> out/gecko-clip.*
    python3 summarize.py clip.mp4                              transcribes first (needs faster-whisper)
    add --fake for offline

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "C1"))
sys.path.insert(0, str(HERE.parent / "_common"))
from ask import ask_json, get_client  # noqa: E402

OUT = HERE / "out"


# ------------------------------------------------------------------ step 1

def summarize_transcript(client, text: str) -> dict:
    """TODO(you): {"summary": str, "action_items": [{"owner", "task"}], "decisions": [str]}."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 2

def format_timestamp(seconds: float) -> str:
    """TODO(you): HH:MM:SS,mmm"""
    raise NotImplementedError


def segments_to_srt(segments: list[dict]) -> str:
    """TODO(you): numbered SRT blocks."""
    raise NotImplementedError


def transcribe(path: str | Path, backend=None) -> list[dict]:
    """TODO(you): segments via faster_whisper, else whisper, else RuntimeError with install help."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 3

def gecko_pack(client, transcript: str) -> dict:
    """TODO(you): {"captions": [3 str], "hashtags": ["#..."], "voiceover": str}, normalized."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 4 (written for you)

FAKE_MEETING = json.dumps({"summary": "Fake summary.", "action_items": [{"owner": "Sam", "task": "order springtails"}],
                           "decisions": ["glass tank"]})
FAKE_GECKO = json.dumps({"captions": ["a", "b", "c"], "hashtags": ["#gecko", "leopardgecko"], "voiceover": "fake script"})


def main(argv: list[str]) -> None:
    fake = "--fake" in argv
    mode = "gecko" if "--mode" in argv and argv[argv.index("--mode") + 1] == "gecko" else "meeting"
    paths = [a for a in argv if not a.startswith("--") and a != "gecko"]
    if not paths:
        sys.exit(__doc__)
    src = Path(paths[0])
    OUT.mkdir(exist_ok=True)
    segments = None
    if src.suffix == ".txt":
        transcript = src.read_text()
    elif src.suffix == ".json":
        segments = json.loads(src.read_text())
        transcript = " ".join(s["text"] for s in segments)
    else:
        segments = transcribe(src)
        transcript = " ".join(s["text"] for s in segments)
    if segments:
        (OUT / f"{src.stem}.srt").write_text(segments_to_srt(segments))
        print(f"wrote out/{src.stem}.srt")
    client = get_client(fake, responses=[FAKE_GECKO if mode == "gecko" else FAKE_MEETING])
    result = gecko_pack(client, transcript) if mode == "gecko" else summarize_transcript(client, transcript)
    out = OUT / f"{src.stem}.{'pack' if mode == 'gecko' else 'summary'}.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote out/{out.name}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
