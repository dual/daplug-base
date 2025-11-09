from daplug_base import dict_merger


def test_merge_updates_nested_dicts_and_adds_unique_items():
    original = {
        "details": {"count": 1},
        "tags": ["existing"],
        "value": "old",
    }
    new_data = {
        "details": {"count": 2},
        "tags": ["new"],
        "value": "updated",
    }

    merged = dict_merger.merge(original, new_data)

    assert merged["details"]["count"] == 2
    assert merged["tags"] == ["existing", "new"]
    assert merged["value"] == "updated"
    assert original == {
        "details": {"count": 1},
        "tags": ["existing"],
        "value": "old",
    }


def test_merge_remove_operations():
    original = {
        "details": {"remove_me": 1, "keep_me": 2},
        "items": [{"id": 1}, {"id": 2}],
    }
    new_data = {
        "details": {"remove_me": None},
        "items": [{"id": 1}],
    }

    merged = dict_merger.merge(
        original,
        new_data,
        update_dict_operation="remove",
        update_list_operation="remove",
    )

    assert "remove_me" not in merged["details"]
    assert merged["items"] == [{"id": 2}]


def test_merge_replace_operation():
    original = {"items": [1, 2, 3]}
    new_data = {"items": [9]}

    merged = dict_merger.merge(original, new_data, update_list_operation="replace")

    assert merged["items"] == [9]
