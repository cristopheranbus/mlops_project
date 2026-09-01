"""Execute the pinned Ruff binary against representative generated projects."""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from tests.project_factory import build_valid_project, write

if TYPE_CHECKING:
    from pathlib import Path


def _run_ruff(root: Path) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("ruff")
    assert executable is not None
    command = [
        executable,
        "check",
        "--config",
        str(root / "pyproject.toml"),
        str(root),
    ]
    # The executable is the repository-pinned Ruff binary, not untrusted input.
    return subprocess.run(  # noqa: S603
        command,
        capture_output=True,
        check=False,
        cwd=root,
        text=True,
    )


@pytest.mark.parametrize("profile", ["python-ml", "mlflow-local", "databricks-mlops"])
def test_generated_profile_passes_real_ruff(tmp_path: Path, profile: str) -> None:
    root = build_valid_project(tmp_path, profile)

    result = _run_ruff(root)

    assert result.returncode == 0, result.stdout + result.stderr


def test_product_code_print_is_rejected(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    write(root / "src/demo_project/modeling/debug.py", 'print("debug")\n')

    result = _run_ruff(root)

    assert result.returncode == 1
    assert "T201" in result.stdout


def test_cli_print_and_test_assert_are_allowed(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    write(root / "src/demo_project/cli.py", 'def main() -> None:\n    print("ready")\n')

    result = _run_ruff(root)

    assert result.returncode == 0, result.stdout + result.stderr


def test_databricks_runtime_builtins_are_allowed(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path, "databricks-mlops")
    write(
        root / "notebooks/databricks/20_train.py",
        """# Databricks notebook source
from demo_project.workflows.train import run_training

dbutils.widgets.text("environment", "dev")
display(spark.range(1))
run_training(None)
""",
    )

    result = _run_ruff(root)

    assert result.returncode == 0, result.stdout + result.stderr


def test_unnecessary_noqa_is_rejected(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    write(root / "src/demo_project/modeling/value.py", "VALUE = 1  # noqa: F401\n")

    result = _run_ruff(root)

    assert result.returncode == 1
    assert "RUF100" in result.stdout
