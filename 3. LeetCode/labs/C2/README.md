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

- `classify(client, text, labels)`: return exactly one of `labels`. The prompt lists the labels and asks for only the label. If the reply isn't in the list, ask once more with a stricter prompt. If it's still wrong, return `"unknown"`. Normalize case and whitespace before comparing.

Concept: this is a **few-shot** opportunity. Add two examples to the prompt and see whether a model gets more consistent. Write what you observe in NOTES.md.

## Step 3 · The report  (15 min)

You write:

- `run(client, folder, labels)`: one row per file: `{"file", "summary", "label", "input_tokens", "output_tokens"}`. Sum tokens across every call made for that file. (Hint: count `client` calls before and after, or wrap `client.messages.create`.)
- `render_report(rows, model)`: a markdown table plus total tokens and estimated cost from `estimate_cost`.

Then run it live on `data/`: `python3 pipeline.py data` and read your own report. Then `python3 coach.py done C2` after the rubric review.
