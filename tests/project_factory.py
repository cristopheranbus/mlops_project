"""Deterministic factories for generated-project contract tests."""

from __future__ import annotations

from pathlib import Path

ProfileName = str


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
    write(
        root / "pyproject.toml",
        f"""
[project]
name = "demo-project"
version = "0.1.0"
dependencies = {dependencies}

[tool.ruff]
line-length = 100

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
        "src/demo_project/__init__.py",
        "src/demo_project/config/models.py",
        "src/demo_project/config/loader.py",
        "src/demo_project/config/hashing.py",
        "src/demo_project/workflows/__init__.py",
        "tests/test_demo.py",
        "docs/architecture.md",
        "docs/configuration.md",
        "docs/testing.md",
    ):
        write(root / relative)
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
        write(root / "tests/integration/test_mlflow.py")
        write(
            root / "src/demo_project/tracking/mlflow.py",
            """from contextlib import contextmanager

import mlflow


@contextmanager
def start_experiment_run(config):
    with mlflow.start_run() as run:
        mlflow.autolog(log_input_examples=True, log_model_signatures=True, silent=False)
        mlflow.set_tags({
            "config.version": "1",
            "config.environment": "local",
            "config.hash": "sha256",
        })
        mlflow.log_artifact("resolved_config.yaml")
        yield run
""",
        )
        write(
            root / "src/demo_project/workflows/train.py",
            """from demo_project.tracking.mlflow import start_experiment_run


def run_training(config):
    with start_experiment_run(config, run_name="train"):
        return None
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
            "tests/external/test_workspace.py",
        ):
            write(root / relative)
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
