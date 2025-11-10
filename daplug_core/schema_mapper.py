from __future__ import annotations

from typing import Any, Dict, List

from . import schema_loader


def map_to_schema(data: Dict[str, Any] | None, schema_file: str, schema_key: str) -> Dict[str, Any]:
    model_data: Dict[str, Any] = {}
    model_schema = schema_loader.load_schema(schema_file, schema_key)
    schemas: List[Dict[str, Any]] = model_schema["allOf"] if model_schema.get("allOf") else [model_schema]
    for model in schemas:
        if model.get("type") == "object":
            _populate_model_data(model.get("properties", {}), data, model_data)
    return model_data


def _populate_model_data(properties: Dict[str, Any], data: Dict[str, Any] | None, model_data: Dict[str, Any]) -> Dict[str, Any]:
    if data and isinstance(data, dict):
        _populate_model_dict(properties, data, model_data)
    return model_data


def _populate_model_dict(properties: Dict[str, Any], data: Dict[str, Any], model_data: Dict[str, Any]) -> None:
    for property_key, property_value in properties.items():
        model_data[property_key] = {}
        if property_value.get("properties"):
            _populate_model_data(
                property_value["properties"], data.get(property_key), model_data[property_key]
            )
        elif property_value.get("items", {}).get("properties"):
            _populate_model_list(model_data, property_key, property_value, data)
        else:
            model_data[property_key] = data.get(property_key)


def _populate_model_list(
    model_data: Dict[str, Any], property_key: str, property_value: Dict[str, Any], data: Dict[str, Any]
) -> None:
    model_data[property_key] = []
    items = data.get(property_key, [])
    for index in range(len(items)):  # pylint: disable=consider-using-enumerate
        if data.get(property_key) and isinstance(items, list) and index < len(items):
            pop = _populate_model_data(
                property_value["items"]["properties"], items[index], {}
            )
            model_data[property_key].append(pop)
