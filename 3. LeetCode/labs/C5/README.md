# C5 · Document processing and RAG

**Maps to:** "Processes documents for LLM consumption and integrates document processing with related AI tasks."
**You'll have at the end:** a retrieval-augmented question answerer over your own `patterns/` folder, with citations and a measured retrieval hit rate. No vector database, no numpy: the point is to see every moving part.

Setup: `pip install -r requirements.txt`. Tests are offline. The corpus is `../../patterns/*.md` (your 17 pattern cards).

**RAG in one sentence.** Split documents into chunks, turn each chunk into a vector, find the chunks whose vectors are closest to the question's vector, and hand only those chunks to the model with the question.

## Step 1 · Chunking  (15 min)

You write `chunk_markdown(text, source, max_chars=600, overlap=80)`:

- Split on headings (lines starting with `#`). Each chunk remembers its heading.
- Within a section, pack words into chunks no longer than `max_chars`.
- Each chunk after the first in a section starts with the last `overlap` characters' worth of whole words from the previous chunk, so a sentence cut at a boundary survives in one of them.
- Return `[{"source", "heading", "text"}]`.

Why overlap: the answer to a question is often one sentence, and a hard cut can split it.

## Step 2 · Embeddings and a store  (15 min)

Real systems call an embedding model (Anthropic recommends Voyage AI's). Here you build a tiny one so you can see what an embedding *is*: a vector where similar texts land close together.

- `tokenize(text)`: lowercase words, `\w+`, drop `STOPWORDS` and single characters.
- `BagOfWordsEmbedder.fit(texts)`: compute **idf** per word: `log(N / (1 + df))`. `embed(text)`: a dict `{word: tf * idf}`, L2-normalized. Rare words count more.
- `cosine(a, b)`: dot product over shared keys divided by the norms.
- `VectorStore.add(chunks, vectors)` and `.search(vector, k)`: the top-k `(score, chunk)` pairs, best first.

## Step 3 · Answer with citations  (15 min)

- `build_prompt(question, chunks)`: number the chunks `[1]`, `[2]`, ... with their source and heading, then the question, then "cite sources as [n]; if the sources don't contain the answer, say so".
- `answer(client, question, store, embedder, k=3)`: embed, search, prompt, ask. Return `{"answer", "sources": [chunks]}`.

Try live: `python3 rag.py "How do I find the next greater element for each item?"`.

## Step 4 · Measure it  (15 min)

- `evaluate(store, embedder, cases, k=3)`: for each case `{"q", "expect_source"}`, a hit is when any top-k chunk comes from the expected file. Return the hit rate.

`eval_cases.json` has 12 questions. Run `python3 rag.py --eval`. The bag-of-words embedder should reach 0.75 or better. Write in NOTES.md which questions miss and why, then try one change (chunk size, k, stopwords) and record what it did. That loop is the actual job. Then `python3 coach.py done C5` after the rubric review.
