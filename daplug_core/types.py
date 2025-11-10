"""Shared typing helpers for daplug_core."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, MutableMapping, Protocol, TypedDict, Union

JSONScalar = Union[str, int, float, bool, None]
JSONType = Union[JSONScalar, "JSONArray", "JSONObject"]
JSONArray = List[JSONType]
JSONObject = Dict[str, JSONType]
JSONMapping = Mapping[str, JSONScalar]
MutableJSONMapping = MutableMapping[str, JSONScalar]


class PublisherProtocol(Protocol):
    def publish(self, **kwargs: Any) -> None:  # pragma: no cover - protocol definition.
        ...


class SnsAttribute(TypedDict):
    DataType: str
    StringValue: Union[str, int, float, bool]


SnsAttributes = Dict[str, SnsAttribute]
