"""Cross-profile contract tests generated from the central case inventory."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_project import validate_project
from tests.contract_cases import ContractCase
from tests.project_factory import build_valid_project


@pytest.mark.contract
def test_every_supported_profile_is_valid(tmp_path: Path, project_profile: str) -> None:
    root = build_valid_project(tmp_path, project_profile)

    resolved_profile, issues = validate_project(root)

    assert resolved_profile == project_profile
    assert issues == []


@pytest.mark.contract
def test_each_contract_mutation_emits_its_owned_issue(
    tmp_path: Path,
    contract_case: ContractCase,
) -> None:
    root = build_valid_project(tmp_path, contract_case.profile)
    contract_case.mutate(root)

    _, issues = validate_project(root)
    error_codes = {issue.code for issue in issues if issue.severity == "error"}

    assert contract_case.expected_code in error_codes


@pytest.mark.databricks_contract
def test_databricks_profile_has_no_structural_errors(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path, "databricks-mlops")

    _, issues = validate_project(root, "databricks-mlops")

    assert issues == []


@pytest.mark.monitoring_contract
def test_databricks_profile_requires_production_monitoring(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path, "databricks-mlops")
    (root / ".github/workflows/04-production-monitoring.yml").unlink()

    _, issues = validate_project(root, "databricks-mlops")

    assert "workflow-contract" in {issue.code for issue in issues}
