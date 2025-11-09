from daplug_base import schema_loader


def test_load_schema_reads_file(tmp_path):
    schema_file = tmp_path / "schema.yml"
    schema_file.write_text(
        """
components:
  schemas:
    Sample:
      type: object
      properties:
        name:
          type: string
"""
    )

    schema = schema_loader.load_schema(str(schema_file), "Sample")

    assert schema["type"] == "object"
    assert "name" in schema["properties"]
