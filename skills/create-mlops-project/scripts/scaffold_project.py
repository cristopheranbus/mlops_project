"""Deterministic baseline generator for new ML repositories."""

from __future__ import annotations

import argparse
import json
import keyword
import re
import shutil
import subprocess
from pathlib import Path
from typing import Literal

from scripts.validate_project import RUFF_REQUIRED_SELECTORS

Profile = Literal["python-ml", "mlflow-local", "databricks-mlops"]
PROFILES: tuple[Profile, ...] = ("python-ml", "mlflow-local", "databricks-mlops")


def _write(path: Path, content: str = "content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def normalize_package(project_name: str) -> str:
    """Return a valid import package derived from a project name."""
    package = re.sub(r"[^a-zA-Z0-9]+", "_", project_name).strip("_").lower()
    if package and package[0].isdigit():
        package = f"ml_{package}"
    if keyword.iskeyword(package):
        package = f"ml_{package}"
    if not package or not package.isidentifier():
        message = "project name must contain letters or digits"
        raise ValueError(message)
    return package


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


def _quality_workflow() -> str:
    return """name: 01 - Code quality and package validation
on:
  pull_request:
  push:
    branches: [dev, main]
permissions:
  contents: read
jobs:
  branch-policy:
    runs-on: ubuntu-latest
    steps:
      - run: test "$BASE_REF" != "main" || test "$HEAD_REF" = "dev"
  type-check:
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
    runs-on: ubuntu-latest
    steps:
      - run: uv run mypy --no-incremental --python-version 3.12 # matrix also covers 3.13
  quality:
    needs: [branch-policy, type-check]
    runs-on: ubuntu-latest
    steps:
      - run: echo quality
"""


def _pyproject(project_name: str, package: str, profile: Profile) -> str:
    dependencies = ["pydantic>=2.11,<3", "pyyaml>=6.0.2,<7", "scikit-learn>=1.5"]
    if profile != "python-ml":
        dependencies.insert(0, "mlflow>=3.1,<4")
    databricks = (
        'builtins = ["dbutils", "display", "spark"]\n'
        'namespace-packages = ["notebooks", "notebooks/databricks"]\n'
        if profile == "databricks-mlops"
        else ""
    )
    mlflow_override = (
        '\n[[tool.mypy.overrides]]\nmodule = ["mlflow"]\nignore_missing_imports = true\n'
        if profile != "python-ml"
        else ""
    )
    return f"""[build-system]
requires = ["hatchling>=1.27,<2"]
build-backend = "hatchling.build"

[project]
name = {json.dumps(project_name)}
version = "0.1.0"
requires-python = ">=3.12,<3.14"
dependencies = {json.dumps(dependencies)}

[dependency-groups]
dev = ["mypy>=2.3.1,<2.4", "pytest>=9,<10", "ruff>=0.16.5,<0.17", "types-pyyaml>=6.0.12,<7"]

[tool.hatch.build.targets.wheel]
packages = ["src/{package}"]

[tool.ruff]
target-version = "py312"
line-length = 100
preview = false
extend-exclude = [".agents"]
{databricks}[tool.ruff.lint]
select = {json.dumps(sorted(RUFF_REQUIRED_SELECTORS))}
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
"src/**/cli.py" = ["T201"]
"notebooks/databricks/**/*.py" = ["N999"]
[tool.ruff.lint.isort]
known-first-party = ["{package}"]

[tool.mypy]
python_version = "3.12"
files = ["src", "tests"]
strict = true
warn_unused_configs = true
disallow_any_explicit = true
disallow_any_unimported = true
strict_bytes = true
strict_equality_for_none = true
show_error_codes = true
show_error_code_links = true
enable_error_code = ["deprecated", "explicit-override", "exhaustive-match", "ignore-without-code", "mutable-override", "possibly-undefined", "redundant-expr", "redundant-self", "truthy-bool", "truthy-iterable", "unused-awaitable"]
{mlflow_override}
[tool.pytest.ini_options]
testpaths = ["tests"]
[tool.coverage.run]
source = ["src"]
"""


def create_project(
    destination: Path,
    project_name: str,
    *,
    package_name: str | None = None,
    profile: Profile = "python-ml",
    embed_skill: bool = False,
) -> Path:
    """Create a baseline in a missing or empty destination without overwriting files."""
    root = destination.resolve()
    if root.exists() and any(root.iterdir()):
        message = f"destination is not empty: {root}"
        raise FileExistsError(message)
    root.mkdir(parents=True, exist_ok=True)
    package = package_name or normalize_package(project_name)
    if not package.isidentifier():
        message = f"invalid Python package name: {package}"
        raise ValueError(message)

    _write(root / "pyproject.toml", _pyproject(project_name, package, profile))
    _write(root / ".mlops-profile", f"{profile}\n")
    _write(
        root / "uv.lock",
        'version = 1\nrevision = 3\nrequires-python = ">=3.12,<3.14"\n',
    )
    _write(root / ".gitignore", ".venv/\n__pycache__/\n.env\nmlruns/\n")
    _write(
        root / "README.md",
        f"# {project_name}\n\nBaseline MLOps `{profile}`. Run `uv lock`, `uv sync --locked`, and `uv run pytest`.\n",
    )
    for relative, title in (
        ("docs/architecture.md", "Architecture"),
        ("docs/configuration.md", "Configuration"),
        ("docs/testing.md", "Testing"),
    ):
        _write(root / relative, f"# {title}\n\nSee the project README for the local workflow.\n")
    _write(
        root / "docs/mypy.md",
        "# Static types with mypy\n\nRun `uv run mypy`. The strict mode rejects explicit `Any` and requires a code on every `type: ignore`. Prefer typed adapters, `types-*` packages, local stubs, and exact overrides. See https://mypy.readthedocs.io/en/stable/.\n",
    )
    for relative in (
        f"src/{package}/__init__.py",
        f"src/{package}/config/__init__.py",
        f"src/{package}/config/models.py",
        f"src/{package}/config/loader.py",
        f"src/{package}/config/hashing.py",
        f"src/{package}/workflows/__init__.py",
        "tests/__init__.py",
    ):
        _write(root / relative, '"""Generated project module."""\n')
    _write(
        root / "tests/test_project.py", "def test_project_contract() -> None:\n    assert True\n"
    )
    _write(
        root / "configs/base.yaml",
        f"config_version: 1\nproject:\n  name: {json.dumps(project_name)}\n",
    )
    _write(root / "configs/local.yaml", "config_version: 1\nproject:\n  environment: local\n")
    _write(root / ".github/workflows/01-code-quality.yml", _quality_workflow())
    _write(
        root / ".github/workflows/02-security.yml", _workflow("02 - Repository security scanning")
    )

    if profile != "python-ml":
        _add_mlflow(root, package)
    if profile == "databricks-mlops":
        _add_databricks(root, package)
    if embed_skill:
        source = Path(__file__).resolve().parents[1]
        shutil.copytree(source, root / ".agents/skills/create-mlops-project")
    return root


def _add_mlflow(root: Path, package: str) -> None:
    _write(root / "docs/mlflow.md", "# MLflow\n\nTracking runs locally by default.\n")
    _write(
        root / "docs/mlflow-security.md",
        "# MLflow security\n\nMLflow AI Gateway is disabled. Before enabling it, review GHSA-h7x2-h6g9-p789, require administrative authorization, HTTPS allowlists, egress controls, and a corrected version. Never configure gateway secrets, api_base, or proxy routes here.\n",
    )
    _write(root / "tests/integration/__init__.py", '"""Integration tests."""\n')
    _write(
        root / "tests/integration/test_mlflow.py",
        "def test_mlflow_contract() -> None:\n    assert True\n",
    )
    _write(root / f"src/{package}/tracking/__init__.py", '"""Tracking adapters."""\n')
    _write(
        root / f"src/{package}/tracking/mlflow.py",
        """from collections.abc import Iterator
from contextlib import contextmanager

import mlflow


@contextmanager
def start_experiment_run(config: object, *, run_name: str) -> Iterator[object]:
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.autolog(log_input_examples=True, log_model_signatures=True, silent=False)
        mlflow.set_tags(
            {"config.version": "1", "config.environment": str(config), "config.hash": "sha256"}
        )
        mlflow.log_artifact("resolved_config.yaml")
        yield run
""",
    )
    _write(
        root / f"src/{package}/workflows/train.py",
        f'from {package}.tracking.mlflow import start_experiment_run\n\n\ndef run_training(config: object) -> None:\n    with start_experiment_run(config, run_name="train"):\n        pass\n',
    )


def _add_databricks(root: Path, package: str) -> None:
    for environment in ("dev", "prod"):
        _write(
            root / f"configs/{environment}.yaml",
            f"config_version: 1\nproject:\n  environment: {environment}\n",
        )
    for name in ("databricks", "operations", "release-checklist", "rollback"):
        _write(root / f"docs/{name}.md", f"# {name.replace('-', ' ').title()}\n")
    _write(root / "tests/external/__init__.py", '"""External tests."""\n')
    _write(
        root / "tests/external/test_workspace.py",
        "def test_workspace_contract() -> None:\n    assert True\n",
    )
    _write(
        root / "notebooks/databricks/20_train.py",
        f"# Databricks notebook source\nfrom {package}.workflows.train import run_training\n\nrun_training(None)\n",
    )
    _write(
        root / "databricks.yml",
        "bundle:\n  name: generated-ml-project\nresources:\n  jobs:\n    training:\n      tasks:\n        - task_key: train\n          notebook_task:\n            notebook_path: notebooks/databricks/20_train.py\n",
    )
    _write(
        root / ".github/workflows/03-databricks.yml",
        _workflow(
            "03 - Databricks bundle validation and deployment",
            "      - run: databricks bundle validate -t dev\n",
        ),
    )
    _write(
        root / ".github/workflows/04-production-monitoring.yml",
        'name: 04 - Production model monitoring\non:\n  schedule:\n    - cron: "17 6 * * *"\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n  monitor:\n    runs-on: ubuntu-latest\n    steps:\n      - run: project-monitor --environment prod --check-config-hash\n',
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--package")
    parser.add_argument("--profile", choices=PROFILES, default="python-ml")
    parser.add_argument("--embed-skill", action="store_true")
    parser.add_argument("--skip-lock", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = create_project(
        args.destination,
        args.name,
        package_name=args.package,
        profile=args.profile,
        embed_skill=args.embed_skill,
    )
    if not args.skip_lock:
        uv_executable = shutil.which("uv")
        if uv_executable is None:
            message = "uv is required unless --skip-lock is used"
            raise RuntimeError(message)
        subprocess.run([uv_executable, "lock"], cwd=root, check=True)
    print(f"Created {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
