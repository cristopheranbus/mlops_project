from __future__ import annotations

import json
from pathlib import Path

from pytest import CaptureFixture

from scripts.validate_project import main, validate_project
from tests.project_factory import build_valid_project, write


def _write(path: Path, content: str = "content\n") -> None:
    write(path, content)


def _valid_project(root: Path, profile: str = "python-ml") -> Path:
    return build_valid_project(root, profile)


def _error_codes(root: Path, profile: str = "auto") -> set[str]:
    _, issues = validate_project(root, profile)
    return {issue.code for issue in issues if issue.severity == "error"}


def test_minimum_python_project_is_valid(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _, issues = validate_project(root)
    assert issues == []


def test_missing_pyproject_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    (root / "pyproject.toml").unlink()
    assert "missing" in _error_codes(root)


def test_missing_tests_are_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    (root / "tests/test_demo.py").unlink()
    assert "tests" in _error_codes(root)


def test_incomplete_quality_configuration_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "pyproject.toml", '[project]\nname = "demo"\nversion = "0.1.0"\n')
    assert {"quality-config", "coverage-config"} <= _error_codes(root)


def test_placeholder_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "docs/configuration.md", "Set CHANGEME before use.\n")
    assert "placeholder" in _error_codes(root)


def test_sensitive_file_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / ".env", "TOKEN=secret\n")
    assert "secret-file" in _error_codes(root)


def test_missing_config_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    (root / "configs/local.yaml").unlink()
    assert "config-layout" in _error_codes(root)


def test_invalid_config_version_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "configs/base.yaml", "config_version: 2\n")
    assert "config-format" in _error_codes(root)


def test_invalid_config_yaml_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "configs/base.yaml", "project: [broken\n")
    assert "config-format" in _error_codes(root)


def test_non_mapping_config_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "configs/base.yaml", "- item\n")
    assert "config-format" in _error_codes(root)


def test_sensitive_config_key_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "configs/local.yaml", "config_version: 1\nauth_token: unsafe\n")
    assert "config-secret" in _error_codes(root)


def test_config_dependencies_are_required(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    _write(
        root / "pyproject.toml",
        pyproject.replace(
            '["pydantic>=2.11,<3", "pyyaml>=6.0.2,<7", "scikit-learn>=1.5"]',
            '["scikit-learn>=1.5"]',
        ),
    )
    assert "config-layout" in _error_codes(root)


def test_multiple_primary_packages_are_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "src/another_package/__init__.py")
    assert "package" in _error_codes(root)


def test_reusable_definition_outside_src_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "scripts/train.py", "def train():\n    return None\n")
    assert "python-layout" in _error_codes(root)


def test_missing_quality_workflow_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    (root / ".github/workflows/01-code-quality.yml").unlink()
    assert "workflow-contract" in _error_codes(root)


def test_workflow_name_is_part_of_the_public_contract(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    path = root / ".github/workflows/01-code-quality.yml"
    _write(path, path.read_text(encoding="utf-8").replace("01 - Code quality", "Quality"))
    assert "workflow-contract" in _error_codes(root)


def test_workflows_default_to_read_only_contents(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    path = root / ".github/workflows/02-security.yml"
    _write(path, path.read_text(encoding="utf-8").replace("contents: read", "contents: write"))
    assert "workflow-contract" in _error_codes(root)


def test_pull_request_target_is_rejected(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    path = root / ".github/workflows/01-code-quality.yml"
    _write(path, path.read_text(encoding="utf-8").replace("pull_request:", "pull_request_target:"))
    assert "workflow-contract" in _error_codes(root)


def test_actions_must_be_pinned_to_a_commit_sha(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    path = root / ".github/workflows/01-code-quality.yml"
    _write(path, path.read_text(encoding="utf-8") + "      - uses: actions/checkout@v4\n")
    assert "workflow-contract" in _error_codes(root)


def test_incomplete_mlflow_profile_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "python-ml")
    assert "mlflow" in _error_codes(root, "mlflow-local")


def test_incomplete_databricks_profile_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    assert "missing" in _error_codes(root, "databricks-mlops")


def test_complete_mlflow_profile_is_valid(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    _, issues = validate_project(root)
    assert issues == []


def test_missing_mlflow_adapter_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    (root / "src/demo_project/tracking/mlflow.py").unlink()
    assert "mlflow-run" in _error_codes(root)


def test_missing_mlflow_security_guide_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    (root / "docs/mlflow-security.md").unlink()
    assert "missing" in _error_codes(root)


def test_mlflow_gateway_api_base_is_rejected(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    _write(
        root / "configs/gateway.yaml",
        "mlflow:\n  gateway:\n    auth_config:\n      api_base: http://127.0.0.1:8080\n",
    )
    assert "mlflow-security" in _error_codes(root)


def test_gateway_auth_config_is_rejected_without_mlflow_label(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    _write(
        root / "configs/provider.yaml",
        "auth_config:\n  api_base: https://internal.example\n",
    )
    assert "mlflow-security" in _error_codes(root)


def test_mlflow_gateway_secret_api_is_rejected(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    _write(
        root / "src/demo_project/tracking/gateway.py",
        'action = "CreateGatewaySecret"\nroute = "/api/2.0/mlflow/gateway/secrets"\n',
    )
    assert "mlflow-security" in _error_codes(root)


def test_mlflow_gateway_proxy_route_is_rejected(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    _write(
        root / "resources/gateway.yml",
        "proxy_route: /gateway/proxy/chat/completions\n",
    )
    assert "mlflow-security" in _error_codes(root)


def test_unrelated_api_base_is_not_rejected(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    _write(root / "configs/external_api.yaml", "service:\n  api_base: https://example.com\n")
    assert "mlflow-security" not in _error_codes(root)


def test_autolog_after_yield_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    _write(
        root / "src/demo_project/tracking/mlflow.py",
        """from contextlib import contextmanager
import mlflow

@contextmanager
def start_experiment_run(config):
    with mlflow.start_run() as run:
        yield run
        mlflow.autolog()
""",
    )
    assert "mlflow-run" in _error_codes(root)


def test_direct_start_run_outside_adapter_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    _write(root / "src/demo_project/modeling/train.py", "import mlflow\nmlflow.start_run()\n")
    assert "mlflow-run" in _error_codes(root)


def test_workflow_must_use_managed_run(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "mlflow-local")
    _write(
        root / "src/demo_project/workflows/train.py", "def run_training(config):\n    return None\n"
    )
    assert "mlflow-run" in _error_codes(root)


def test_complete_databricks_profile_is_valid(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    _, issues = validate_project(root)
    assert issues == []


def test_source_notebook_requires_marker(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    _write(
        root / "notebooks/databricks/20_train.py",
        "from demo_project.workflows.train import run_training\nrun_training(None)\n",
    )
    assert "notebook-format" in _error_codes(root)


def test_notebook_definition_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    path = root / "notebooks/databricks/20_train.py"
    _write(path, path.read_text(encoding="utf-8") + "\ndef helper():\n    return None\n")
    assert "notebook-layout" in _error_codes(root)


def test_notebook_must_import_workflow(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    _write(
        root / "notebooks/databricks/20_train.py", "# Databricks notebook source\nprint('train')\n"
    )
    assert "notebook-layout" in _error_codes(root)


def test_valid_ipynb_notebook_is_accepted(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    (root / "notebooks/databricks/20_train.py").unlink()
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from demo_project.workflows.train import run_training\n",
                    "run_training(None)\n",
                ],
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    _write(root / "notebooks/databricks/20_train.ipynb", json.dumps(notebook))
    databricks = (root / "databricks.yml").read_text(encoding="utf-8")
    _write(root / "databricks.yml", databricks.replace("20_train.py", "20_train.ipynb"))
    _, issues = validate_project(root)
    assert issues == []


def test_ipynb_outputs_are_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [{"output_type": "stream", "name": "stdout", "text": ["x"]}],
                "source": ["from demo_project.workflows.train import run_training\n"],
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    _write(root / "notebooks/databricks/30_evaluate.ipynb", json.dumps(notebook))
    assert "notebook-format" in _error_codes(root)


def test_duplicate_notebook_formats_are_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    notebook = {
        "cells": [],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    _write(root / "notebooks/databricks/20_train.ipynb", json.dumps(notebook))
    assert "notebook-format" in _error_codes(root)


def test_notebook_task_outside_canonical_directory_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    _write(root / "notebooks/exploration/train.py", "# Databricks notebook source\n")
    databricks = (root / "databricks.yml").read_text(encoding="utf-8")
    _write(
        root / "databricks.yml",
        databricks.replace("notebooks/databricks/20_train.py", "notebooks/exploration/train.py"),
    )
    assert "databricks-task" in _error_codes(root)


def test_bundle_requires_notebook_task(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    _write(root / "databricks.yml", "bundle:\n  name: demo\n")
    assert "databricks-task" in _error_codes(root)


def test_databricks_workflow_must_validate_the_bundle(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    path = root / ".github/workflows/03-databricks.yml"
    _write(path, path.read_text(encoding="utf-8").replace("databricks bundle validate", "echo"))
    assert "workflow-contract" in _error_codes(root)


def test_monitoring_workflow_requires_schedule_and_manual_trigger(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    path = root / ".github/workflows/04-production-monitoring.yml"
    _write(path, path.read_text(encoding="utf-8").replace("  schedule:\n", ""))
    assert "workflow-contract" in _error_codes(root)


def test_invalid_profile_marker_is_reported_and_falls_back(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / ".mlops-profile", "unknown-profile\n")
    profile, issues = validate_project(root)
    assert profile == "python-ml"
    assert "profile" in {issue.code for issue in issues}


def test_invalid_toml_is_reported(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    _write(root / "pyproject.toml", "this is not = valid toml\n")
    assert "pyproject" in _error_codes(root)


def test_missing_path_is_reported(tmp_path: Path) -> None:
    assert "path" in _error_codes(tmp_path / "missing")


def test_validation_does_not_modify_files(tmp_path: Path) -> None:
    root = _valid_project(tmp_path)
    before = {
        path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }
    validate_project(root)
    after = {
        path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()
    }
    assert before == after


def test_cli_reports_success(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    root = _valid_project(tmp_path)
    assert main([str(root)]) == 0
    assert "Result: 0 error(s)" in capsys.readouterr().out


def test_cli_reports_failure(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    assert main([str(tmp_path / "missing")]) == 1
    assert "ERROR [path]" in capsys.readouterr().out
