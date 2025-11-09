import json
from types import SimpleNamespace

from daplug_base import publisher
from tests.mocks.fakes import FakeSNSClient, RecordingLogger


def test_publish_sends_message(monkeypatch):
    sns_client = FakeSNSClient()
    monkeypatch.setattr(publisher, "boto3", SimpleNamespace(client=lambda *_, **__: sns_client))
    logger = RecordingLogger()
    monkeypatch.setattr(publisher, "logger", logger)

    publisher.publish(
        arn="arn:topic",
        data={"id": 123},
        attributes={"extra": "value"},
        fifo_group_id="group",
        fifo_duplication_id="dup",
        region="us-east-1",
        endpoint="https://sns.test",
    )

    assert len(sns_client.published) == 1
    payload = sns_client.published[0]
    assert payload["TopicArn"] == "arn:topic"
    assert json.loads(payload["Message"]) == {"id": 123}
    assert payload["MessageAttributes"] == {"extra": "value"}
    assert payload["MessageGroupId"] == "group"
    assert payload["MessageDeduplicationId"] == "dup"
    assert logger.entries == []


def test_publish_returns_early_without_required_args(monkeypatch):
    called = {"count": 0}

    def _client(*_, **__):
        called["count"] += 1
        raise AssertionError("client should not be invoked")

    monkeypatch.setattr(publisher, "boto3", SimpleNamespace(client=_client))

    publisher.publish(data={"id": 1})

    assert called["count"] == 0


def test_publish_logs_when_client_raises(monkeypatch):
    sns_client = FakeSNSClient(should_raise=True)
    monkeypatch.setattr(publisher, "boto3", SimpleNamespace(client=lambda *_, **__: sns_client))
    logger = RecordingLogger()
    monkeypatch.setattr(publisher, "logger", logger)

    publisher.publish(arn="arn:topic", data={"id": 1})

    assert len(logger.entries) == 1
    log_entry = logger.entries[0]
    assert log_entry["level"] == "WARN"
    assert "publish_sns_error" in log_entry["log"]["error"]
