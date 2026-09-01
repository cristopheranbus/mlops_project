"""Focused edge cases that protect parser and profile-resolution boundaries."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from scripts.validate_project import validate_project
from tests.project_factory import build_valid_project, write

if TYPE_CHECKING:
    from pathlib import Path


def _codes(root: Path, profile: str = "auto") -> set[str]:
    _, issues = validate_project(root, profile)
    return {issue.code for issue in issues}


def test_missing_typed_configuration_module_is_reported(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    (root / "src/demo_project/config/hashing.py").unlink()
    assert "config-layout" in _codes(root)


def test_sensitive_keys_nested_in_lists_are_reported(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    write(
        root / "configs/local.yaml",
        "config_version: 1\nservices:\n  - name: safe\n    client_secret: unsafe\n",
    )
    assert "config-secret" in _codes(root)


def test_invalid_python_outside_owned_directories_is_reported(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    write(root / "tools/broken.py", "def broken(:\n")
    assert "python-layout" in _codes(root)


def test_invalid_mlflow_adapter_is_reported(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path, "mlflow-local")
    write(root / "src/demo_project/tracking/mlflow.py", "def broken(:\n")
    assert "mlflow-run" in _codes(root)


def test_malformed_ipynb_is_reported(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path, "databricks-mlops")
    write(root / "notebooks/databricks/30_evaluate.ipynb", "{not-json")
    assert "notebook-format" in _codes(root)


def test_ipynb_requires_nbformat_four_and_a_cell_list(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path, "databricks-mlops")
    source = root / "notebooks/databricks/20_train.py"
    source.unlink()
    write(
        root / "notebooks/databricks/20_train.ipynb",
        json.dumps({"nbformat": 3, "cells": {}}),
    )
    assert "notebook-format" in _codes(root)


def test_resource_files_can_own_notebook_tasks(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path, "databricks-mlops")
    write(root / "databricks.yml", "bundle:\n  name: demo\n")
    write(
        root / "resources/training.yml",
        "resources:\n  jobs:\n    training:\n      tasks:\n"
        "        - notebook_task:\n"
        "            notebook_path: ../notebooks/databricks/20_train.py\n",
    )
    assert "databricks-task" not in _codes(root)


def test_profile_is_inferred_from_databricks_bundle_without_marker(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path, "databricks-mlops")
    (root / ".mlops-profile").unlink()
    profile, _ = validate_project(root)
    assert profile == "databricks-mlops"


def test_example_specific_dataset_names_are_reported(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    write(root / "docs/architecture.md", "Dataset Iris should not leak into generated projects.\n")
    assert "example-leak" in _codes(root)
