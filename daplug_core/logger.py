import os

from . import json_helper


def log(**kwargs):
    if os.getenv("RUN_MODE") != "unittest":
        payload = {
            "level": kwargs.get("level", "INFO"),
            "log": kwargs.get("log", {}),
        }
        print(json_helper.try_encode_json(payload))
