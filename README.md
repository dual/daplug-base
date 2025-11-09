# 🧩 daplug-base (da•plug)

> **Shared schema + event plumbing extracted from `daplug-ddb` and `daplug-cypher`**

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-apache%202.0-blue)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-blue)](#-local-development)

`daplug-base` is the tiny layer of glue that both [`daplug-ddb`](../daplug-ddb) and [`daplug-cypher`](../daplug-cypher) relied on in their old `common/` directories. It bundles a publisher, logging shim, schema utilities, and merge helpers so the higher-level adapters can stay laser-focused on their respective datastores. This repository is not meant to be a fully fledged adapter on its own—it simply centralizes the primitives the adapters share.

---

## 🌈 Why this exists

- **Single source of truth** – The DynamoDB and Cypher adapters used to carry duplicate copies of the same helpers. `daplug-base` keeps those modules in one place.
- **Batteries-included SNS publishing** – The base `publisher` encapsulates SNS fan-out, FIFO metadata, and logging so consuming packages can just hand it messages.
- **Schema-first tooling** – `schema_loader` and `schema_mapper` read OpenAPI/JSON schemas and project payloads to the shapes your adapters expect.
- **Deterministic merging** – `dict_merger` upgrades nested payloads with configurable list/dict strategies (add, replace, remove) so you can keep optimistic writes tight.

If you are migrating `daplug-ddb` or `daplug-cypher`, remove their legacy `common/` folder and import from `daplug_base` instead. Nothing else changes.

---

## 📦 Installation

```bash
pip install daplug-base
# or
pipenv install daplug-base
```

> Not on PyPI yet? Until release, install straight from the repo:
>
> ```bash
> pip install git+https://github.com/paulcruse3/daplug-base.git
> ```

---

## 🔁 How consuming packages use the base

1. **Declare the dependency** in the adapter package (e.g. `daplug-ddb`) via Pipfile/pyproject.
2. **Drop the duplicated modules** (`common/logger.py`, `common/publisher.py`, etc.).
3. **Import from `daplug_base`** wherever those utilities were previously referenced.

```python
# inside daplug-ddb
from daplug_base import dict_merger, json_helper, publisher, schema_mapper

merged = dict_merger.merge(original, incoming, update_list_operation="replace")
publisher.publish(arn=sns_arn, data=merged, attributes={"event": "updated"})
```

Because the API surface stayed the same, adapter code typically only needs import-path updates.

---

## 🧱 Building blocks

| Module | Purpose |
| ------ | ------- |
| `base_adapter.BaseAdapter` | Minimal SNS-aware adapter scaffold (used as a mixin by higher-level adapters). |
| `publisher.publish` | Thin wrapper over `boto3` SNS clients with FIFO group/dedupe support and structured logging. |
| `logger.log` | Consistent JSON stdout logging that honors `RUN_MODE=unittest`. |
| `json_helper` | Best-effort `try_encode_json` / `try_decode_json` helpers used by loggers and publishers. |
| `schema_loader.load_schema` | Loads an OpenAPI/JSON schema and resolves `$ref`s using `jsonref`. |
| `schema_mapper.map_to_schema` | Recursively projects payloads into schema-shaped dictionaries (supports `allOf` inheritance). |
| `dict_merger.merge` | Deep merge with per-call list/dict strategies (`add`, `remove`, `replace`, `upsert`). |

Mix and match these pieces inside datastore-specific adapters.

---

## 🧭 Example: refactoring `daplug-ddb`

```python
# before (inside daplug_ddb/common/publisher.py)
from . import logger
import boto3

# after
from daplug_base import publisher

publisher.publish(
    arn=self.sns_arn,
    data=payload,
    fifo_group_id=fifo_group,
    fifo_duplication_id=fifo_dedupe,
    attributes={"source": "daplug-ddb"},
)
```

```python
# before
from .common.dict_merger import merge

# after
from daplug_base import dict_merger

updated_item = dict_merger.merge(original, patch, update_list_operation="replace")
```

The same pattern applies inside `daplug-cypher` when merging node payloads or formatting SNS events.

---

## ⚙️ Local development

```bash
git clone https://github.com/paulcruse3/daplug-base.git
cd daplug-base
pipenv install --dev
```

### Run tests & coverage

```bash
pipenv run test       # pytest tests/
pipenv run test-cov   # pytest --cov=daplug_base --cov-report=term-missing
pipenv run lint       # pylint --fail-under 10 daplug_base
```

### Ship updates downstream

1. Bump the version in `setup.py` (and `setup.cfg` if needed).
2. Publish to PyPI or deliver a git tag.
3. Update `daplug-ddb` and `daplug-cypher` to depend on the new version.
4. Remove any residual `common/` references in those repos and re-run their suites.

---

## 🤝 Contributing

Pull requests are welcome—especially improvements that make life easier for the DynamoDB and Cypher adapters. If you add a helper here, remember to wire it up in the consuming packages as well.

```bash
git checkout -b feat/better-schema-mapper
pipenv run test-cov
pipenv run lint
git commit -am "feat: better schema mapper"
```

---

## 📄 License

Apache 2.0 – see [LICENSE](LICENSE).
