"""Central pytest collection policy for profile and contract matrices."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

if os.environ.get("MUTANT_UNDER_TEST"):
    mutant_skill_root = Path.cwd() / "skills" / "create-mlops-project"
    sys.path.insert(0, str(mutant_skill_root))

from scripts.validate_project import PROFILES
from tests.contract_cases import CONTRACT_CASES


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("mlops-contract")
    group.addoption(
        "--profile",
        action="store",
        choices=("all", *PROFILES),
        default="all",
        help="Limit generated-project contract cases to one MLOps profile.",
    )
    group.addoption(
        "--run-external",
        action="store_true",
        default=False,
        help="Run tests that need explicitly authorized external infrastructure.",
    )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    selected_profile = metafunc.config.getoption("--profile")
    if "project_profile" in metafunc.fixturenames:
        profiles = PROFILES if selected_profile == "all" else (selected_profile,)
        parameters = [
            pytest.param(
                profile,
                id=f"profile={profile}",
                marks=pytest.mark.databricks_contract if profile == "databricks-mlops" else (),
            )
            for profile in profiles
        ]
        metafunc.parametrize("project_profile", parameters)
    if "contract_case" in metafunc.fixturenames:
        cases = tuple(
            case
            for case in CONTRACT_CASES
            if selected_profile == "all" or case.profile == selected_profile
        )
        parameters = []
        for case in cases:
            marks = []
            if case.profile == "databricks-mlops":
                marks.append(pytest.mark.databricks_contract)
            if case.id == "missing-production-monitoring":
                marks.append(pytest.mark.monitoring_contract)
            parameters.append(pytest.param(case, id=case.id, marks=marks))
        metafunc.parametrize("contract_case", parameters)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-external"):
        return
    skip_external = pytest.mark.skip(reason="requires --run-external and authorized infrastructure")
    for item in items:
        if "external" in item.keywords:
            item.add_marker(skip_external)
