# 🤖 Agent Playbook for `daplug-core`

This mini playbook explains how to operate on the `daplug-core` repository without hunting around the tree. Treat it as your field manual whenever you need to patch shared helpers for `daplug-ddb` or `daplug-cypher`.

---

## 1. Mission Overview

`daplug-core` contains the primitives that were previously duplicated inside the `common/` folders of `daplug-ddb` and `daplug-cypher`. It exposes:

- `base_adapter.BaseAdapter` – lightweight SNS-aware adapter scaffold
- `publisher` – SNS client wrapper with FIFO support and resilient logging
- `logger` – JSON stdout logger that suppresses output under `RUN_MODE=unittest`
- `json_helper` – best-effort encode/decode helpers used by other modules
- `schema_loader` + `schema_mapper` – OpenAPI-driven projection utilities
- `dict_merger` – deep merge helper with configurable strategies

Any enhancement to these utilities will ripple into the datastore-specific adapters once they import the updated package. Keep backwards compatibility in mind when editing signatures.

---

## 2. Repository Layout

```txt
.
├── daplug_core/        # runtime package modules
├── tests/              # one-to-one test coverage for each module
│   └── mocks/          # reusable RecordingPublisher/FakeSNS/etc.
├── Pipfile             # runtime/dev dependencies + helper scripts
├── Pipfile.lock        # locked dependency graph
├── README.md           # colorful overview + downstream guidance
└── .agents/AGENTS.md   # this guide
```

Key expectation: every file inside `daplug_core/` has a twin in `tests/` (e.g., `daplug_core/logger.py` ↔ `tests/test_logger.py`). Keep that symmetry when adding modules.

---

## 3. Environment Setup

We standardize on Python 3.9 + Pipenv:

```bash
git clone https://github.com/paulcruse3/daplug-core.git
cd daplug-core
pipenv install --dev
```

Useful scripts (defined in `Pipfile`):

| Script              | Command                                                   |
| ------------------- | --------------------------------------------------------- |
| `pipenv run lint`   | `pylint --fail-under 10 daplug_core`                      |
| `pipenv run test`   | `pytest tests`                                            |
| `pipenv run test-cov` | `pytest --cov=daplug_core --cov-report=term-missing`   |

Prefer `pipenv run <script>` so dependencies from the virtualenv are guaranteed.

---

## 4. Testing Expectations

- 100% coverage is enforced by the existing suite. When touching a module, extend or add tests accordingly.
- Shared mocks live in `tests/mocks/fakes.py`. Extend this file rather than scattering ad-hoc doubles.
- Keep tests focused on behavior: each one exercises a single code path (happy path, error handling, edge cases) and asserts the observable side effects (e.g., captured SNS payloads or structured logs).

### Running the Suite

```bash
pipenv run test-cov
# or, if you only need a subset while iterating:
pipenv run pytest tests/test_publisher.py -k "logs"
```

Pytest is configured in `setup.cfg` (`testpaths = tests`). No extra flags are needed for discovery.

---

## 5. Common Agent Tasks

### 5.1 Updating the Base Adapter

`daplug_core/base_adapter.py` only wires SNS attributes together. If you need to add a new piece of metadata:

1. Update `BaseAdapter.create_format_attributes` with the merge logic.
2. Add/adjust tests in `tests/test_base_adapter.py` to assert the new metadata.
3. Run `pipenv run test-cov` before yielding.

### 5.2 Tweaking Publisher Logging

`publisher.publish` wraps a boto3 SNS client. When altering error handling:

- Ensure `tests/test_publisher.py` captures both happy path and exception cases.
- Use the provided `FakeSNSClient` + `RecordingLogger` mocks to keep tests deterministic.

### 5.3 Schema Helpers

`schema_loader` expects real files. Use `tmp_path` in tests to create ad-hoc schema YAML files. `schema_mapper` tests should continue to stub `schema_loader.load_schema` via `monkeypatch` and feed controlled schema dicts.

---

## 6. Consuming Repo Integration Checklist

Whenever `daplug-core` is updated, the datastore adapters need to:

1. Bump their dependency to the new version (`pipenv install --dev ../daplug-core` during development or install from PyPI once released).
2. Remove any residual `common/` code (since it’s now redundant).
3. Replace imports: `from daplug_core import dict_merger` instead of `from .common.dict_merger import merge`.
4. Re-run their pipelines (`pipenv run test`, custom integration suites, etc.) to ensure nothing broke downstream.

Document these steps in PR descriptions so future reviewers know how the base change propagates.

---

## 7. Style & Tooling Notes

- No type hints live in this repository (per project requirements). Keep new code dynamic.
- Favor descriptive variable names when type context would otherwise be unclear.
- When logging, ensure payloads stay JSON-serializable; lean on `json_helper.try_encode_json` when in doubt.
- Avoid direct `print`/`boto3` usage in tests—monkeypatch the modules to isolates side effects.

---

## 8. Useful Command Snippets

```bash
# Format + run a single test module
pipenv run pytest tests/test_schema_mapper.py

# Regenerate Pipfile.lock after changing dependencies
pipenv lock

# Verify import paths resolve (fails fast on syntax errors)
python -m compileall daplug_core
```

Keep this file updated as the project evolves so future agents inherit the latest tribal knowledge.
