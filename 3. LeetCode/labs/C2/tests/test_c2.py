from pathlib import Path

import pipeline
from fake_llm import FakeClient

DATA = Path(__file__).resolve().parents[1] / "data"


# ---------------------------------------------------------------- step 1

def test_step1_collect_files_sorted_and_filtered(tmp_path):
    (tmp_path / "b.md").write_text("b")
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "skip.png").write_bytes(b"\x89")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.md").write_text("c")
    names = [p.name for p in pipeline.collect_files(tmp_path)]
    assert names == ["a.txt", "b.md", "c.md"]


def test_step1_chunk_text_short_is_one_chunk():
    assert pipeline.chunk_text("hello world", 100) == ["hello world"]


def test_step1_chunk_text_respects_limit_and_words():
    text = "\n\n".join(f"paragraph {i} " + "word " * 20 for i in range(6))
    chunks = pipeline.chunk_text(text, 150)
    assert len(chunks) > 1
    assert all(len(c) <= 150 for c in chunks)
    joined = " ".join(chunks).split()
    assert joined == text.split()                      # nothing lost, no word cut


def test_step1_chunk_text_splits_a_giant_paragraph_without_cutting_words():
    text = "supercalifragilistic " * 50
    chunks = pipeline.chunk_text(text, 60)
    assert all(len(c) <= 60 for c in chunks)
    assert all(piece == "supercalifragilistic" for c in chunks for piece in c.split())


def test_step1_summarize_short_text_is_one_call():
    client = FakeClient(["A short summary."])
    assert pipeline.summarize(client, "some text") == "A short summary."
    assert len(client.calls) == 1
    assert "some text" in client.calls[0]["messages"][0]["content"]


def test_step1_summarize_long_text_maps_then_reduces():
    long = "\n\n".join("para " + "x" * 90 for _ in range(10))     # ~1000 chars
    client = FakeClient(["s1", "s2", "s3", "s4", "combined"])
    out = pipeline.summarize(client, long, max_chars=300)
    assert out == "combined"
    assert len(client.calls) >= 3
    last = client.calls[-1]["messages"][0]["content"]
    assert "s1" in last and "s2" in last


# ---------------------------------------------------------------- step 2

def test_step2_classify_returns_a_label_from_the_set():
    client = FakeClient(["Health"])
    assert pipeline.classify(client, "vet visit", ["care-sheet", "health"]) == "health"
    assert "care-sheet" in client.calls[0]["messages"][0]["content"]


def test_step2_classify_retries_once_then_unknown():
    client = FakeClient(["I think it's about geckos", "still prose"])
    assert pipeline.classify(client, "text", ["a", "b"]) == "unknown"
    assert len(client.calls) == 2
    client = FakeClient(["nonsense", "b."])
    assert pipeline.classify(client, "text", ["a", "b"]) == "b"


# ---------------------------------------------------------------- step 3

def test_step3_run_sums_tokens_per_file(tmp_path):
    (tmp_path / "one.md").write_text("first note")
    (tmp_path / "two.md").write_text("second note")
    client = FakeClient(["sum1", "health", "sum2", "shopping"])
    rows = pipeline.run(client, tmp_path, ["health", "shopping"])
    assert [r["file"] for r in rows] == ["one.md", "two.md"]
    assert rows[0]["summary"] == "sum1" and rows[0]["label"] == "health"
    assert rows[1]["label"] == "shopping"
    assert rows[0]["input_tokens"] > 0 and rows[0]["output_tokens"] > 0
    total_in = sum(c_usage for c_usage in (r["input_tokens"] for r in rows))
    assert total_in > 0


def test_step3_render_report_has_table_totals_and_cost():
    rows = [{"file": "a.md", "summary": "s", "label": "health", "input_tokens": 1000, "output_tokens": 100},
            {"file": "b.md", "summary": "t", "label": "build", "input_tokens": 2000, "output_tokens": 200}]
    report = pipeline.render_report(rows, "claude-opus-5-5")
    assert "| a.md |" in report and "| b.md |" in report
    assert "3000" in report and "300" in report
    assert "$" in report


def test_step3_run_on_sample_data_offline():
    client = FakeClient(default="care-sheet")
    rows = pipeline.run(client, DATA)
    assert len(rows) == 5
    assert all(r["label"] == "care-sheet" for r in rows)
