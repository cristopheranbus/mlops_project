"""Deterministic factories for generated-project contract tests."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from scripts.validate_project import RUFF_REQUIRED_SELECTORS

if TYPE_CHECKING:
    from pathlib import Path

type ProfileName = str


def write(path: Path, content: str = "content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _workflow(name: str, body: str = "") -> str:
    return f"""name: {name}
on:
  pull_request:
permissions:
  contents: read
jobs:
  contract:
    runs-on: ubuntu-latest
    steps:
      - run: echo contract
{body}"""


def build_valid_project(root: Path, profile: ProfileName = "python-ml") -> Path:
    dependencies = '["pydantic>=2.11,<3", "pyyaml>=6.0.2,<7", "scikit-learn>=1.5"]'
    if profile != "python-ml":
        dependencies = (
            '["mlflow>=3.1,<4", "pydantic>=2.11,<3", "pyyaml>=6.0.2,<7", "scikit-learn>=1.5"]'
        )
    ruff_selectors = json.dumps(sorted(RUFF_REQUIRED_SELECTORS))
    ruff_databricks_settings = (
        'builtins = ["dbutils", "display", "spark"]\n'
        'namespace-packages = ["notebooks", "notebooks/databricks"]\n'
        if profile == "databricks-mlops"
        else ""
    )
    write(
        root / "pyproject.toml",
        f"""
[project]
name = "demo-project"
version = "0.1.0"
requires-python = ">=3.12,<3.14"
dependencies = {dependencies}

[dependency-groups]
dev = ["ruff>=0.16.5,<0.17"]

[tool.ruff]
target-version = "py312"
line-length = 100
preview = false
{ruff_databricks_settings}
[tool.ruff.lint]
select = {ruff_selectors}
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
"src/**/cli.py" = ["T201"]
"notebooks/databricks/**/*.py" = ["N999"]

[tool.ruff.lint.isort]
known-first-party = ["demo_project"]

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
source = ["src"]
""".strip(),
    )
    write(root / ".mlops-profile", profile)
    for relative in (
        "uv.lock",
        "README.md",
        ".gitignore",
        "docs/architecture.md",
        "docs/configuration.md",
        "docs/testing.md",
    ):
        write(root / relative)
    for relative in (
        "src/demo_project/__init__.py",
        "src/demo_project/config/__init__.py",
        "src/demo_project/config/models.py",
        "src/demo_project/config/loader.py",
        "src/demo_project/config/hashing.py",
        "src/demo_project/workflows/__init__.py",
    ):
        write(root / relative, '"""Generated project module."""\n')
    write(root / "tests/__init__.py", '"""Generated project tests."""\n')
    write(root / "tests/test_demo.py", "def test_project_contract() -> None:\n    assert True\n")
    write(
        root / ".github/workflows/01-code-quality.yml",
        _workflow("01 - Code quality and package validation"),
    )
    write(
        root / ".github/workflows/02-security.yml",
        _workflow("02 - Repository security scanning"),
    )
    write(root / "configs/base.yaml", "config_version: 1\nproject:\n  name: demo\n")
    write(root / "configs/local.yaml", "config_version: 1\nproject:\n  environment: local\n")
    if profile != "python-ml":
        write(root / "docs/mlflow.md")
        write(
            root / "docs/mlflow-security.md",
            """# Seguridad de MLflow

Este proyecto usa MLflow Tracking y no habilita MLflow AI Gateway. La creación de
gateway secrets, `api_base` y las rutas de proxy están fuera del contrato generado.

Antes de incorporar AI Gateway, revisa GHSA-h7x2-h6g9-p789, valida una versión corregida,
aplica autorización administrativa, una allowlist HTTPS y controles de egress.
""",
        )
        write(
            root / "tests/integration/test_mlflow.py",
            "def test_mlflow_contract() -> None:\n    assert True\n",
        )
        write(root / "tests/integration/__init__.py", '"""Integration tests."""\n')
        write(root / "src/demo_project/tracking/__init__.py", '"""Tracking adapters."""\n')
        write(
            root / "src/demo_project/tracking/mlflow.py",
            """from collections.abc import Iterator
from contextlib import contextmanager

import mlflow


@contextmanager
def start_experiment_run(config: object) -> Iterator[object]:
    with mlflow.start_run() as run:
        mlflow.autolog(log_input_examples=True, log_model_signatures=True, silent=False)
        mlflow.set_tags({
            "config.version": "1",
            "config.environment": str(config),
            "config.hash": "sha256",
        })
        mlflow.log_artifact("resolved_config.yaml")
        yield run
""",
        )
        write(
            root / "src/demo_project/workflows/train.py",
            """from demo_project.tracking.mlflow import start_experiment_run


def run_training(config: object) -> None:
    with start_experiment_run(config, run_name="train"):
        pass
""",
        )
    if profile == "databricks-mlops":
        write(root / "configs/dev.yaml", "config_version: 1\nproject:\n  environment: dev\n")
        write(root / "configs/prod.yaml", "config_version: 1\nproject:\n  environment: prod\n")
        for relative in (
            "docs/databricks.md",
            "docs/operations.md",
            "docs/release-checklist.md",
            "docs/rollback.md",
        ):
            write(root / relative)
        write(
            root / "tests/external/test_workspace.py",
            "def test_workspace_contract() -> None:\n    assert True\n",
        )
        write(root / "tests/external/__init__.py", '"""External tests."""\n')
        write(
            root / "notebooks/databricks/20_train.py",
            """# Databricks notebook source
from demo_project.workflows.train import run_training

run_training(None)
""",
        )
        write(
            root / "databricks.yml",
            """bundle:
  name: demo
resources:
  jobs:
    training:
      tasks:
        - task_key: train
          notebook_task:
            notebook_path: notebooks/databricks/20_train.py
""",
        )
        write(
            root / ".github/workflows/03-databricks.yml",
            _workflow(
                "03 - Databricks bundle validation and deployment",
                "      - run: databricks bundle validate -t dev\n",
            ),
        )
        write(
            root / ".github/workflows/04-production-monitoring.yml",
            """name: 04 - Production model monitoring
on:
  schedule:
    - cron: "17 6 * * *"
  workflow_dispatch:
permissions:
  contents: read
jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - run: project-monitor --environment prod --check-config-hash
""",
        )
    return root
