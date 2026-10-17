# C8 · AWS deployment

**Maps to:** "Familiarity with AWS cloud services or AWS AI/ML tooling is a plus."
**You'll have at the end:** the C6 meeting summarizer running as an AWS Lambda, triggered when a transcript lands in an S3 bucket, writing the summary next to it. Everything is testable locally without an AWS account; deploying is the last step and uses the free tier.

Setup: `pip install -r requirements.txt`. Tests are offline. AWS CLI and SAM CLI are needed only for step 3.

## Step 1 · A storage interface  (15 min)

Code that talks to S3 directly is hard to test. So: a tiny interface, two implementations. You write, in `storage.py`:

- `LocalStorage(root)`: `put(key, data: bytes)`, `get(key) -> bytes`, `list(prefix) -> list[str]`. Keys are relative paths under `root`.
- `S3Storage(bucket, client=None)`: same three methods over `boto3`. `client` defaults to `boto3.client("s3")`, created lazily so importing the module never needs boto3. Use `put_object`, `get_object` (read `["Body"]`), and `list_objects_v2` (keys under `Contents`, may be absent).

The test for S3Storage passes a fake client object. That's the point: the interface is what makes the Lambda testable.

## Step 2 · The handler  (15 min)

You write, in `handler.py`:

- `parse_s3_event(event) -> list[tuple[str, str]]`: `(bucket, key)` for each record. Keys arrive URL-encoded (`+` for space); decode with `urllib.parse.unquote_plus`.
- `handler(event, context, storage=None, client=None)`: for each `(bucket, key)`, read the transcript, call `summarize_transcript` from C6, write `<key>.summary.json` back. Return `{"statusCode": 200, "processed": [keys]}`. When `storage` is `None`, build an `S3Storage` for the record's bucket; when `client` is `None`, use `get_client()`.

Run it locally: `python3 handler.py events/s3_put.json --fake` (uses LocalStorage under `local-bucket/`).

## Step 3 · Deploy  (15 min, plus waiting)

`template.yaml` is a complete SAM template: one function, one bucket, the trigger, the API key from an environment variable. Follow `DEPLOY.md` step by step and fill in its placeholders as you go: `sam build`, `sam deploy --guided`, upload `../C6/data/standup.txt`, watch the summary appear. Then tear it down (`sam delete`) so nothing bills you. Write what it cost (it should be $0) and the one thing that confused you. Then rubric review and `python3 coach.py done C8`.
