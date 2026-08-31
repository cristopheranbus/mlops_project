"""Typed inventories consumed by pytest's dynamic collection hook."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from tests.project_factory import write


@dataclass(frozen=True)
class ContractCase:
    id: str
    profile: str
    expected_code: str
    mutate: Callable[[Path], None]


def _remove_local_config(root: Path) -> None:
    (root / "configs/local.yaml").unlink()


def _add_secret(root: Path) -> None:
    write(root / "configs/local.yaml", "config_version: 1\nauth_token: unsafe\n")


def _add_second_package(root: Path) -> None:
    write(root / "src/second_package/__init__.py")


def _remove_managed_run(root: Path) -> None:
    write(
        root / "src/demo_project/workflows/train.py",
        "def run_training(config):\n    return None\n",
    )


def _break_notebook_marker(root: Path) -> None:
    write(
        root / "notebooks/databricks/20_train.py",
        "from demo_project.workflows.train import run_training\nrun_training(None)\n",
    )


def _remove_monitoring_workflow(root: Path) -> None:
    (root / ".github/workflows/04-production-monitoring.yml").unlink()


CONTRACT_CASES = (
    ContractCase("missing-local-config", "python-ml", "config-layout", _remove_local_config),
    ContractCase("secret-in-config", "python-ml", "config-secret", _add_secret),
    ContractCase("second-primary-package", "python-ml", "package", _add_second_package),
    ContractCase("workflow-without-managed-run", "mlflow-local", "mlflow-run", _remove_managed_run),
    ContractCase(
        "source-notebook-without-marker",
        "databricks-mlops",
        "notebook-format",
        _break_notebook_marker,
    ),
    ContractCase(
        "missing-production-monitoring",
        "databricks-mlops",
        "workflow-contract",
        _remove_monitoring_workflow,
    ),
)
