import json

from daplug_core import logger


def test_log_prints_payload_when_not_unittest(monkeypatch, capsys):
    monkeypatch.setenv("RUN_MODE", "production")

    logger.log(level="DEBUG", log={"message": "hello"})

    captured = capsys.readouterr().out.strip()
    assert json.loads(captured) == {"level": "DEBUG", "log": {"message": "hello"}}


def test_log_suppressed_in_unittest(monkeypatch, capsys):
    monkeypatch.setenv("RUN_MODE", "unittest")

    logger.log(level="INFO", log={"message": "ignored"})

    assert capsys.readouterr().out == ""
