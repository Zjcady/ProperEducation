# C2 · Prompt in a workflow

**Maps to:** "Wraps generative AI prompts within applications or workflows to automate tasks such as text generation or data analysis."
**You'll have at the end:** a script that walks a folder of notes, summarizes and classifies each file, and writes a report with token counts and cost. The sample data is gecko care notes.

Setup: `pip install -r requirements.txt`. Tests are offline. Reuse your C1 functions: `pipeline.py` imports `ask`, `ask_json`, `estimate_cost` from `../C1/ask.py`.

## Step 1 · Files in, summaries out  (15 min)

You write:

- `collect_files(folder, exts=(".md", ".txt"))`: sorted list of matching files, recursive.
- `chunk_text(text, max_chars)`: split long text at paragraph boundaries into pieces no longer than `max_chars`. Short text is one chunk. Never cut a word in half.
- `summarize(client, text, max_chars=6000)`: one-sentence summary. Long text: summarize each chunk, then summarize the joined summaries (that's "map-reduce"). Don't silently truncate; that loses information and is the most common pipeline bug.

## Step 2 · Classification with a fixed label set  (15 min)

You write:

- `classify(client, text, labels)`: return exactly one of `labels`. If the reply isn't in the list, ask once more with a stricter prompt. If it's still wrong, return `"unknown"`. Normalize case and whitespace before comparing.
  - The part that never changes goes in `system`, as a **list** of text blocks: the label list (`describe_labels(labels)`, given) and the two **few-shot** examples (`FEW_SHOT`, given; edit them if you like). Put `"cache_control": {"type": "ephemeral"}` on the **last** system block.
  - The file's text goes in the user message, with "reply with only the label". Pass `system=` through C1's `ask`.

Concept: **prompt caching**. The cache is a prefix match over `tools`, then `system`, then `messages`, up to the block with `cache_control`. The first call writes the prefix (1.25x input price), every later call with the byte-identical prefix reads it (0.1x, 0.05x on Opus 5.5). That's why the per-file text must stay *after* the breakpoint: one changed character in the prefix and nothing matches. Check it in `response.usage`: `cache_creation_input_tokens` on the first call, `cache_read_input_tokens` after; both 0 means not cached. Catch: there's a model-dependent minimum prefix size (512 tokens on Opus 5.5 at the time of writing; see the [prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). Shorter prefixes silently don't cache, no error. This one is about 200 tokens, so live you'll likely see zeros; the fake client caches anything. Cached entries last 5 minutes, refreshed on each hit.

Try live: does the few-shot prompt make the labels more consistent? Write what you observe in NOTES.md.

## Step 3 · The report  (15 min)

You write:

- `run(client, folder, labels)`: one row per file: `{"file", "summary", "label", "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"}`. Sum tokens across every call made for that file. (Hint: `_UsageTap` already wraps `client.messages.create` and adds all four up.)
- `render_report(rows, model)`: a markdown table plus total tokens, estimated cost from `estimate_cost`, and a `cached input: N%` line (cache reads / all input: uncached + written + read). Rows without the cache keys count them as 0.

Then run it live on `data/`: `python3 pipeline.py data` and read your own report. Then `python3 coach.py done C2` after the rubric review.
