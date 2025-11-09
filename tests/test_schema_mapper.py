from daplug_core import schema_mapper


def test_map_to_schema_handles_all_of(monkeypatch):
    schema = {
        "allOf": [
            {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "meta": {
                        "type": "object",
                        "properties": {"count": {"type": "number"}},
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "properties": {"value": {"type": "string"}},
                        },
                    },
                },
            }
        ]
    }
    monkeypatch.setattr(schema_mapper.schema_loader, "load_schema", lambda *_, **__: schema)

    data = {
        "id": "abc",
        "meta": {"count": 5, "extra": True},
        "items": [{"value": "one"}, {"value": "two"}],
    }

    result = schema_mapper.map_to_schema(data, "schema.yaml", "Sample")

    assert result["id"] == "abc"
    assert result["meta"] == {"count": 5}
    assert result["items"] == [{"value": "one"}, {"value": "two"}]


def test_map_to_schema_handles_simple_schema(monkeypatch):
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "details": {
                "type": "object",
                "properties": {"note": {"type": "string"}},
            },
        },
    }
    monkeypatch.setattr(schema_mapper.schema_loader, "load_schema", lambda *_, **__: schema)

    data = {"status": "ready", "details": {"note": "done"}}

    result = schema_mapper.map_to_schema(data, "schema.yaml", "Sample")

    assert result["status"] == "ready"
    assert result["details"] == {"note": "done"}
