"""C5 · Retrieval-augmented answers over the patterns folder.

    python3 rag.py "How do I find the next greater element?"      live
    python3 rag.py --fake "..."                                    offline
    python3 rag.py --eval                                          retrieval hit rate, no model calls

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "C1"))
sys.path.insert(0, str(HERE.parent / "_common"))
from ask import ask, get_client  # noqa: E402

CORPUS = HERE.parents[1] / "patterns"
STOPWORDS = set("a an the and or of to in on for with is are it this that as at by be do how i you "
                "what when which from into its each one two use".split())


# ------------------------------------------------------------------ step 1

def chunk_markdown(text: str, source: str, max_chars: int = 600, overlap: int = 80) -> list[dict]:
    """TODO(you): heading-aware chunks with word-boundary overlap. See README step 1."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 2

def tokenize(text: str) -> list[str]:
    """TODO(you): lowercase \\w+ words, minus STOPWORDS and single characters."""
    raise NotImplementedError


class BagOfWordsEmbedder:
    """A toy embedder: tf-idf vectors as sparse dicts, L2-normalized."""

    def __init__(self):
        self.idf: dict[str, float] = {}
        self.n_docs = 0

    def fit(self, texts: list[str]) -> "BagOfWordsEmbedder":
        """TODO(you): idf[word] = log(N / (1 + df))."""
        raise NotImplementedError

    def embed(self, text: str) -> dict[str, float]:
        """TODO(you): {word: tf * idf}, L2-normalized. Unknown words get idf of log(N/1)."""
        raise NotImplementedError


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    """TODO(you): dot over shared keys / (norm a * norm b). 0.0 if either is empty."""
    raise NotImplementedError


class VectorStore:
    def __init__(self):
        self.items: list[tuple[dict, dict[str, float]]] = []

    def add(self, chunks: list[dict], vectors: list[dict[str, float]]) -> None:
        """TODO(you): keep (chunk, vector) pairs."""
        raise NotImplementedError

    def search(self, vector: dict[str, float], k: int = 3) -> list[tuple[float, dict]]:
        """TODO(you): top-k (score, chunk), best first."""
        raise NotImplementedError


# ------------------------------------------------------------------ step 3

def build_prompt(question: str, chunks: list[dict]) -> str:
    """TODO(you): numbered sources, the question, and the citation instruction."""
    raise NotImplementedError


def answer(client, question: str, store: VectorStore, embedder: BagOfWordsEmbedder, k: int = 3) -> dict:
    """TODO(you): embed, search, prompt, ask. Return {"answer", "sources"}."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 4

def evaluate(store: VectorStore, embedder: BagOfWordsEmbedder, cases: list[dict], k: int = 3) -> float:
    """TODO(you): fraction of cases where a top-k chunk comes from expect_source."""
    raise NotImplementedError


# ------------------------------------------------------------------ scaffolding

def load_corpus(folder: Path = CORPUS, **chunk_kwargs) -> list[dict]:
    chunks = []
    for path in sorted(folder.glob("*.md")):
        chunks.extend(chunk_markdown(path.read_text(), path.name, **chunk_kwargs))
    return chunks


def build_index(folder: Path = CORPUS, **chunk_kwargs) -> tuple[VectorStore, BagOfWordsEmbedder]:
    chunks = load_corpus(folder, **chunk_kwargs)
    embedder = BagOfWordsEmbedder().fit([c["text"] for c in chunks])
    store = VectorStore()
    store.add(chunks, [embedder.embed(c["text"]) for c in chunks])
    return store, embedder


def main(argv: list[str]) -> None:
    store, embedder = build_index()
    if "--eval" in argv:
        cases = json.loads((HERE / "eval_cases.json").read_text())
        rate = evaluate(store, embedder, cases)
        print(f"hit@3 = {rate:.2f} over {len(cases)} questions, {len(store.items)} chunks")
        for case in cases:
            top = [c["source"] for _, c in store.search(embedder.embed(case["q"]), 3)]
            mark = "ok " if case["expect_source"] in top else "MISS"
            print(f"  {mark} {case['q'][:55]:<55} -> {top[0]}")
        return
    words = [a for a in argv if not a.startswith("--")]
    if not words:
        sys.exit(__doc__)
    client = get_client("--fake" in argv, responses=["(fake answer) see [1]"])
    out = answer(client, " ".join(words), store, embedder)
    print(out["answer"])
    print("\nsources:", ", ".join(f"{c['source']} · {c['heading']}" for c in out["sources"]))


if __name__ == "__main__":
    main(sys.argv[1:])
