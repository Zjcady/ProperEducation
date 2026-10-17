import json
from pathlib import Path

import pytest

import summarize
from fake_llm import FakeClient

LAB = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- step 1

def test_step1_summarize_transcript_shapes():
    client = FakeClient([json.dumps({"summary": "S.", "action_items": [{"owner": "Sam", "task": "order bugs"}],
                                     "decisions": ["glass tank", "12h UVB"]})])
    out = summarize.summarize_transcript(client, "transcript text")
    assert out == {"summary": "S.", "action_items": [{"owner": "Sam", "task": "order bugs"}],
                   "decisions": ["glass tank", "12h UVB"]}
    prompt = client.calls[0]["messages"][0]["content"]
    assert "transcript text" in prompt and "action" in prompt.lower() and "decision" in prompt.lower()


def test_step1_summarize_transcript_rejects_wrong_shapes():
    client = FakeClient([json.dumps({"summary": "S.", "action_items": "none", "decisions": []})] * 2)
    with pytest.raises(ValueError):
        summarize.summarize_transcript(client, "t")
    client = FakeClient([json.dumps({"summary": "S.", "action_items": [{"who": "x"}], "decisions": []})] * 2)
    with pytest.raises(ValueError):
        summarize.summarize_transcript(client, "t")


# ---------------------------------------------------------------- step 2

def test_step2_format_timestamp():
    assert summarize.format_timestamp(0) == "00:00:00,000"
    assert summarize.format_timestamp(2.4) == "00:00:02,400"
    assert summarize.format_timestamp(3661.007) == "01:01:01,007"


def test_step2_segments_to_srt():
    srt = summarize.segments_to_srt([{"start": 0.0, "end": 2.4, "text": " Hi "}, {"start": 2.4, "end": 5.0, "text": "There"}])
    assert srt == "1\n00:00:00,000 --> 00:00:02,400\nHi\n\n2\n00:00:02,400 --> 00:00:05,000\nThere\n"


def test_step2_transcribe_uses_backend_or_fails_helpfully(monkeypatch):
    segs = [{"start": 0, "end": 1, "text": "x"}]
    assert summarize.transcribe("clip.mp4", backend=lambda p: segs) == segs
    import builtins
    real_import = builtins.__import__
    def no_whisper(name, *a, **k):
        if name in ("faster_whisper", "whisper"):
            raise ImportError(name)
        return real_import(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", no_whisper)
    with pytest.raises(RuntimeError) as err:
        summarize.transcribe("clip.mp4")
    assert "pip install" in str(err.value)


# ---------------------------------------------------------------- step 3

def test_step3_gecko_pack_normalizes_hashtags():
    client = FakeClient([json.dumps({"captions": ["a", "b", "c"], "hashtags": ["gecko", "#Gecko", "leopard gecko", "#reptile"],
                                     "voiceover": "  script  "})])
    out = summarize.gecko_pack(client, "t")
    assert out["captions"] == ["a", "b", "c"]
    assert out["hashtags"] == ["#gecko", "#leopardgecko", "#reptile"]
    assert out["voiceover"] == "script"


def test_step3_gecko_pack_requires_three_captions():
    client = FakeClient([json.dumps({"captions": ["only one"], "hashtags": [], "voiceover": "v"})] * 2)
    with pytest.raises(ValueError):
        summarize.gecko_pack(client, "t")


# ---------------------------------------------------------------- step 4

def test_step4_cli_offline_meeting_and_gecko(tmp_path, monkeypatch):
    monkeypatch.setattr(summarize, "OUT", tmp_path)
    summarize.main(["--fake", str(LAB / "data" / "standup.txt")])
    data = json.loads((tmp_path / "standup.summary.json").read_text())
    assert data["action_items"][0]["owner"] == "Sam"
    summarize.main(["--fake", "--mode", "gecko", str(LAB / "data" / "gecko-clip.json")])
    assert (tmp_path / "gecko-clip.srt").read_text().startswith("1\n00:00:00,000 --> 00:00:02,400")
    pack = json.loads((tmp_path / "gecko-clip.pack.json").read_text())
    assert pack["hashtags"] == ["#gecko", "#leopardgecko"]
