# C6 · Meeting summarizer, then the gecko pipeline

**Maps to:** "Experience with AI meeting summarizers" in the posting, and it's the first half of your social media pipeline.
**You'll have at the end:** transcript in, structured summary out (summary, action items with owners, decisions), subtitles as `.srt`, and a "gecko mode" that turns a clip's transcript into captions, hashtags and a voiceover script.

Setup: `pip install -r requirements.txt`. Tests are offline. Real audio transcription needs `pip install faster-whisper` and a few hundred MB of model download; the lab works without it using the sample transcript and sample segments.

## Step 1 · Structured summary  (15 min)

You write `summarize_transcript(client, text)` using `ask_json` from C1. Required keys: `summary` (string), `action_items` (list of `{"owner", "task"}`), `decisions` (list of strings). Validate the shapes; raise `ValueError` if the model returns the wrong types even after `ask_json`'s retry.

Prompt design matters here. Say who the audience is (someone who missed the meeting), say what an action item is (a person and a thing they'll do), and give the exact JSON shape.

## Step 2 · Subtitles and transcription  (15 min)

- `format_timestamp(seconds)`: `HH:MM:SS,mmm`. SRT uses a comma before milliseconds.
- `segments_to_srt(segments)`: numbered blocks, `start --> end`, text, blank line.
- `transcribe(path, backend=None)`: try `faster_whisper`, then `whisper`; return `[{"start", "end", "text"}]`. If neither is installed, raise `RuntimeError` with the install command in the message. `backend` lets a test inject a fake.

## Step 3 · Gecko mode  (15 min)

You write `gecko_pack(client, transcript)`: `ask_json` for `captions` (exactly 3 strings, different tones), `hashtags` (list), `voiceover` (a 40 to 60 word script). Normalize: every hashtag starts with `#` and has no spaces; dedupe; raise `ValueError` if not exactly 3 captions.

## Step 4 · The CLI  (15 min)

`main()` is written. Read it. It handles `.txt` (transcript), `.json` (segments) and audio (via `transcribe`). Run:

```
python3 summarize.py --fake data/standup.txt
python3 summarize.py --fake --mode gecko data/gecko-clip.json
```

then live without `--fake`. Check the outputs in `out/`. Then rubric review and `python3 coach.py done C6`.

Where this goes next: C8 puts step 1 behind an AWS Lambda. Your video pipeline adds ffmpeg to burn the `.srt` into the clip and a TTS voice for the voiceover script.
