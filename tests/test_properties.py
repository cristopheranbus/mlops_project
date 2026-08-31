"""Property-based checks for invariants with a broad input surface."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from scripts.validate_project import validate_project
from tests.project_factory import build_valid_project, write

SAFE_KEYS = st.from_regex(r"[a-z][a-z0-9_]{0,11}", fullmatch=True).filter(
    lambda value: not any(word in value for word in ("password", "secret", "token", "private_key"))
)
SAFE_VALUES = st.one_of(st.integers(), st.booleans(), st.none())


@given(st.dictionaries(SAFE_KEYS, SAFE_VALUES, max_size=8))
@settings(max_examples=30, deadline=None)
def test_safe_configuration_mappings_do_not_look_like_secrets(
    values: dict[str, int | bool | None],
) -> None:
    with TemporaryDirectory() as temporary:
        root = build_valid_project(Path(temporary))
        payload = {"config_version": 1, "parameters": values}
        write(root / "configs/local.yaml", yaml.safe_dump(payload, sort_keys=True))

        _, issues = validate_project(root)

        assert "config-secret" not in {issue.code for issue in issues}


@given(st.sampled_from(("password", "api_token", "client_secret", "private_key")))
def test_sensitive_configuration_keys_are_always_rejected(
    sensitive_key: str,
) -> None:
    with TemporaryDirectory() as temporary:
        root = build_valid_project(Path(temporary))
        payload = {"config_version": 1, "service": {sensitive_key: "unsafe"}}
        write(root / "configs/local.yaml", yaml.safe_dump(payload, sort_keys=True))

        _, issues = validate_project(root)

        assert "config-secret" in {issue.code for issue in issues}


@given(st.integers(min_value=1, max_value=6))
@settings(max_examples=12, deadline=None)
def test_notebook_tasks_cannot_escape_the_canonical_directory(
    traversal_depth: int,
) -> None:
    with TemporaryDirectory() as temporary:
        root = build_valid_project(Path(temporary), "databricks-mlops")
        escaped_path = "../" * traversal_depth + "outside.py"
        databricks = (root / "databricks.yml").read_text(encoding="utf-8")
        write(
            root / "databricks.yml",
            databricks.replace("notebooks/databricks/20_train.py", escaped_path),
        )

        _, issues = validate_project(root)

        assert "databricks-task" in {issue.code for issue in issues}
