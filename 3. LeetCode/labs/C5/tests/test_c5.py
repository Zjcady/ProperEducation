import json
import re
from pathlib import Path

import pytest

import rag
from fake_llm import FakeClient

LAB = Path(__file__).resolve().parents[1]
DOC = """# Stack

Push things you haven't resolved yet. Pop when the current item resolves the top.

## Template

stack = [] and loop. Store indices when you need distances.
"""


# ---------------------------------------------------------------- step 1

def test_step1_chunks_carry_source_and_heading():
    chunks = rag.chunk_markdown(DOC, "stack.md", max_chars=600)
    assert [c["heading"] for c in chunks] == ["Stack", "Template"]
    assert all(c["source"] == "stack.md" for c in chunks)
    assert "Push things" in chunks[0]["text"]


def test_step1_chunks_respect_max_chars_and_overlap_whole_words():
    body = "# H\n\n" + " ".join(f"word{i}" for i in range(200))
    chunks = rag.chunk_markdown(body, "x.md", max_chars=100, overlap=30)
    assert len(chunks) > 2
    assert all(len(c["text"]) <= 100 for c in chunks)
    for prev, nxt in zip(chunks, chunks[1:]):
        first_word = nxt["text"].split()[0]
        assert first_word in prev["text"].split(), "next chunk should start inside the previous one"
    seen = [w for c in chunks for w in c["text"].split()]
    assert set(seen) == {f"word{i}" for i in range(200)}, "nothing lost"


# ---------------------------------------------------------------- step 2

def test_step2_tokenize_drops_stopwords_and_single_chars():
    assert rag.tokenize("The stack is a LIFO structure, i.e. it's last-in first-out") == \
        ["stack", "lifo", "structure", "last", "first", "out"]


def test_step2_embedder_identical_texts_are_identical_vectors():
    emb = rag.BagOfWordsEmbedder().fit(["stack push pop", "heap push pop", "trie prefix"])
    a, b = emb.embed("push the stack"), emb.embed("push the stack")
    assert rag.cosine(a, b) == pytest.approx(1.0)
    assert abs(sum(v * v for v in a.values()) - 1.0) < 1e-9, "L2-normalized"


def test_step2_rare_words_weigh_more_than_common():
    emb = rag.BagOfWordsEmbedder().fit(["push pop stack", "push pop heap", "push pop trie"])
    vec = emb.embed("push stack")
    assert vec["stack"] > vec["push"]


def test_step2_cosine_and_store_search():
    assert rag.cosine({}, {"a": 1.0}) == 0.0
    assert rag.cosine({"a": 1.0}, {"b": 1.0}) == 0.0
    chunks = [{"source": "s", "heading": "", "text": t} for t in
              ("stack push pop bracket", "heap k largest priority", "trie prefix autocomplete")]
    emb = rag.BagOfWordsEmbedder().fit([c["text"] for c in chunks])
    store = rag.VectorStore()
    store.add(chunks, [emb.embed(c["text"]) for c in chunks])
    top = store.search(emb.embed("prefix autocomplete words"), k=2)
    assert len(top) == 2 and top[0][1]["text"].startswith("trie")
    assert top[0][0] >= top[1][0]


# ---------------------------------------------------------------- step 3

def test_step3_build_prompt_numbers_sources_and_asks_for_citations():
    chunks = [{"source": "a.md", "heading": "A", "text": "alpha"}, {"source": "b.md", "heading": "B", "text": "beta"}]
    p = rag.build_prompt("why?", chunks)
    assert "[1]" in p and "[2]" in p and "alpha" in p and "beta" in p
    assert "a.md" in p and "why?" in p
    assert "[n]" in p and "say so" in p.lower()


def test_step3_answer_returns_text_and_sources():
    store, emb = rag.build_index()
    client = FakeClient(["Use a monotonic stack [1]."])
    out = rag.answer(client, "next greater element", store, emb, k=2)
    assert out["answer"].startswith("Use a monotonic")
    assert len(out["sources"]) == 2
    assert "next greater element" in client.calls[0]["messages"][0]["content"]


# ---------------------------------------------------------------- step 4

def test_step4_evaluate_hit_rate_on_the_patterns_corpus():
    store, emb = rag.build_index()
    cases = json.loads((LAB / "eval_cases.json").read_text())
    rate = rag.evaluate(store, emb, cases, k=3)
    assert rate >= 0.75, f"hit@3 was {rate:.2f}"


def test_step4_evaluate_empty_and_perfect():
    chunks = [{"source": "x.md", "heading": "", "text": "zebra giraffe"}]
    emb = rag.BagOfWordsEmbedder().fit([c["text"] for c in chunks])
    store = rag.VectorStore(); store.add(chunks, [emb.embed(c["text"]) for c in chunks])
    assert rag.evaluate(store, emb, [], 3) == 0.0
    assert rag.evaluate(store, emb, [{"q": "zebra", "expect_source": "x.md"}], 1) == 1.0


def test_step3_poisoned_chunk_stays_data_inside_its_source():
    """OWASP LLM01 scenario 4: a document in the corpus was edited to give the model orders.
    The prompt must present it as numbered source text, with your instructions outside the sources."""
    raw = (LAB / "tests" / "fixtures" / "poisoned.md").read_text()
    heading, body = raw.split("\n", 1)
    poison = body.strip()
    chunks = [{"source": "stack.md", "heading": "Stack", "text": "Use a monotonic stack for next greater element."},
              {"source": "poisoned.md", "heading": heading.lstrip("# "), "text": poison}]
    p = rag.build_prompt("How do I find the next greater element?", chunks)
    first, second = p.index("[1]"), p.index("[2]")
    at = p.index(poison)
    assert p.count(poison) == 1, "the chunk appears once, word for word"
    assert first < second < at and "poisoned.md" in p[second:at], "it sits under its own [2] label"
    assert "[3]" not in p[at:], "nothing after it is labelled as another source"
    outside = p[:first] + p[at + len(poison):]
    assert re.search(r"only[^\n]*sources", outside, re.I), "'use only the sources' is your instruction, outside them"
    assert "[n]" in outside, "the citation rule is outside the sources too"
