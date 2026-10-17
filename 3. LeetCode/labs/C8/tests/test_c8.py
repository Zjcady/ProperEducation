import io
import json
from pathlib import Path

import pytest

import handler
import storage
from fake_llm import FakeClient

LAB = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- step 1

def test_step1_local_storage_roundtrip_and_list(tmp_path):
    s = storage.LocalStorage(tmp_path)
    s.put("incoming/a.txt", b"hello")
    s.put("incoming/b.txt", b"world")
    s.put("other/c.txt", b"!")
    assert s.get("incoming/a.txt") == b"hello"
    assert s.list("incoming/") == ["incoming/a.txt", "incoming/b.txt"]
    assert s.list() == ["incoming/a.txt", "incoming/b.txt", "other/c.txt"]
    with pytest.raises(KeyError):
        s.get("missing.txt")


class FakeS3:
    def __init__(self):
        self.objects = {}
    def put_object(self, Bucket, Key, Body):
        self.objects[(Bucket, Key)] = Body
    def get_object(self, Bucket, Key):
        return {"Body": io.BytesIO(self.objects[(Bucket, Key)])}
    def list_objects_v2(self, Bucket, Prefix=""):
        keys = [k for (b, k) in self.objects if b == Bucket and k.startswith(Prefix)]
        return {"Contents": [{"Key": k} for k in keys]} if keys else {}


def test_step1_s3_storage_over_an_injected_client():
    fake = FakeS3()
    s = storage.S3Storage("bkt", client=fake)
    s.put("x/1.txt", b"one")
    assert s.get("x/1.txt") == b"one"
    assert s.list("x/") == ["x/1.txt"]
    assert s.list("nothing/") == []


def test_step1_importing_storage_does_not_need_boto3():
    s = storage.S3Storage("bkt")
    assert s._client is None            # boto3 only loads when .client is touched


# ---------------------------------------------------------------- step 2

def test_step2_parse_s3_event_decodes_keys():
    event = json.loads((LAB / "events" / "s3_put.json").read_text())
    assert handler.parse_s3_event(event) == [("my-transcripts-bucket", "incoming/standup 2026-09.txt")]
    assert handler.parse_s3_event({"Records": []}) == []


def test_step2_handler_writes_summary_next_to_transcript(tmp_path):
    store = storage.LocalStorage(tmp_path)
    store.put("incoming/standup.txt", b"Zach: decision, glass tank. Sam: I will order bugs.")
    client = FakeClient([json.dumps({"summary": "S", "action_items": [{"owner": "Sam", "task": "order bugs"}],
                                     "decisions": ["glass tank"]})])
    event = {"Records": [{"s3": {"bucket": {"name": "b"}, "object": {"key": "incoming/standup.txt"}}}]}
    out = handler.handler(event, None, storage=store, client=client)
    assert out == {"statusCode": 200, "processed": ["incoming/standup.txt"]}
    summary = json.loads(store.get("incoming/standup.txt.summary.json"))
    assert summary["decisions"] == ["glass tank"]
    assert "order bugs" in client.calls[0]["messages"][0]["content"]


# ---------------------------------------------------------------- step 3

def test_step3_template_and_deploy_notes():
    assert (LAB / "template.yaml").exists()
    text = (LAB / "DEPLOY.md").read_text()
    assert "_(you)_" not in text, "fill in DEPLOY.md after deploying"
