import json

from daplug_base import json_helper


def test_try_decode_json_parses_strings():
    result = json_helper.try_decode_json('{"value": 1}')
    assert result == {"value": 1}


def test_try_decode_json_returns_original_on_failure():
    payload = set([1])
    result = json_helper.try_decode_json(payload)
    assert result is payload


def test_try_encode_json_serializes_objects():
    encoded = json_helper.try_encode_json({"flag": True})
    assert json.loads(encoded) == {"flag": True}


def test_try_encode_json_returns_input_on_failure():
    value = object()
    result = json_helper.try_encode_json(value)
    assert result is value
