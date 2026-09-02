from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import cast

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
SKILL_ROOT = ROOT / "skills" / "create-mlops-project"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ACTION_REF = re.compile(r"uses:\s*[^@\s]+@([^\s#]+)")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)


def _plugin_manifest() -> dict[str, object]:
    return cast("dict[str, object]", json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8")))


def test_plugin_manifest_points_to_the_bundled_skill() -> None:
    manifest = _plugin_manifest()

    assert manifest["name"] == "create-mlops-project"
    assert manifest["skills"] == "./skills/"
    assert (SKILL_ROOT / "SKILL.md").is_file()
    assert SEMVER.fullmatch(str(manifest["version"]))
    assert manifest["license"] == "Apache-2.0"


def test_plugin_and_python_package_versions_match() -> None:
    manifest = _plugin_manifest()
    with (ROOT / "pyproject.toml").open("rb") as stream:
        pyproject = tomllib.load(stream)

    assert manifest["version"] == pyproject["project"]["version"]


def test_skill_frontmatter_and_ui_metadata_are_aligned() -> None:
    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    _, frontmatter_text, _ = skill_text.split("---", maxsplit=2)
    frontmatter = yaml.safe_load(frontmatter_text)
    metadata = yaml.safe_load((SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8"))

    assert frontmatter["name"] == "create-mlops-project"
    assert "new" in frontmatter["description"].lower()
    assert "$create-mlops-project" in metadata["interface"]["default_prompt"]
    assert metadata["policy"]["allow_implicit_invocation"] is True


def test_github_yaml_files_parse() -> None:
    yaml_files = [
        ROOT / ".github" / "dependabot.yml",
        *sorted((ROOT / ".github" / "workflows").glob("*.yml")),
        *sorted((ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml")),
    ]

    for path in yaml_files:
        assert yaml.safe_load(path.read_text(encoding="utf-8")) is not None, path


def test_dependabot_batches_updates_without_pr_flooding() -> None:
    config = yaml.safe_load((ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8"))

    assert config["version"] == 2
    updates = config["updates"]
    assert {item["package-ecosystem"] for item in updates} == {"uv", "github-actions"}
    for item in updates:
        assert item["schedule"]["interval"] == "monthly"
        assert item["target-branch"] == "dev"
        assert item["open-pull-requests-limit"] == 1
        assert item["assignees"] == ["cristopheranbus"]
        assert "labels" not in item

        groups = item["groups"]
        version_groups = [
            group for group in groups.values() if group["applies-to"] == "version-updates"
        ]
        security_groups = [
            group for group in groups.values() if group["applies-to"] == "security-updates"
        ]
        assert len(version_groups) == 1
        assert len(security_groups) == 1
        assert version_groups[0]["patterns"] == ["*"]
        assert set(version_groups[0]["update-types"]) == {"major", "minor", "patch"}
        assert security_groups[0]["patterns"] == ["*"]


def test_repository_workflows_have_numbered_public_names() -> None:
    expected_names = {
        "01-code-quality.yml": "01 - Code quality and package validation",
        "02-security.yml": "02 - Repository security scanning",
        "03-databricks-contract.yml": "03 - Databricks bundle validation and deployment contract",
        "04-monitoring-contract.yml": "04 - Production model monitoring contract",
    }

    for filename, expected_name in expected_names.items():
        workflow = yaml.safe_load(
            (ROOT / ".github" / "workflows" / filename).read_text(encoding="utf-8")
        )
        assert workflow["name"] == expected_name
        assert workflow["permissions"]["contents"] == "read"


def test_repository_workflows_use_immutable_actions_and_safe_triggers() -> None:
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        source = path.read_text(encoding="utf-8")
        assert "pull_request_target" not in source, path
        assert all(FULL_SHA.fullmatch(ref) for ref in ACTION_REF.findall(source)), path


def test_quality_workflow_uses_read_only_ruff_gates() -> None:
    source = (ROOT / ".github" / "workflows" / "01-code-quality.yml").read_text(encoding="utf-8")

    assert "ruff check . --output-format=github" in source
    assert "ruff format --check ." in source
    assert "ruff check . --fix" not in source
    assert "ruff format ." not in source


def test_quality_workflow_enforces_branch_and_mypy_contracts() -> None:
    source = (ROOT / ".github" / "workflows" / "01-code-quality.yml").read_text(encoding="utf-8")

    assert "branch-policy:" in source
    assert '"$BASE_REF" == "main" && "$HEAD_REF" != "dev"' in source
    assert "type-check:" in source
    assert "--no-incremental" in source
    assert "--junit-format per_file" in source
    assert "needs: [branch-policy, static-analysis, type-check, tests, package]" in source


def test_mutation_analysis_uses_current_config_and_reports_operational_failures() -> None:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        pyproject = tomllib.load(stream)

    config = pyproject["tool"]["mutmut"]
    assert config["source_paths"] == ["skills/create-mlops-project/scripts/validate_project.py"]
    assert config["pytest_add_cli_args_test_selection"] == [
        "tests/test_contract_matrix.py",
        "tests/test_properties.py",
        "tests/test_validate_project.py",
        "tests/test_validator_edges.py",
    ]
    assert config["pytest_add_cli_args"] == [
        "--no-cov",
        "-q",
    ]
    assert "runner" not in config
    assert "paths_to_mutate" not in config
    assert "tests_dir" not in config

    workflow = (ROOT / ".github" / "workflows" / "01-code-quality.yml").read_text(encoding="utf-8")
    mutation_job = workflow.split("  mutation-analysis:", maxsplit=1)[1].split(
        "\n  quality:", maxsplit=1
    )[0]
    assert "continue-on-error" not in mutation_job

    conftest = (ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert 'os.environ.get("MUTANT_UNDER_TEST")' in conftest
    assert 'Path.cwd() / "skills" / "create-mlops-project"' in conftest
    assert conftest.index("sys.path.insert") < conftest.index(
        "from scripts.validate_project import PROFILES"
    )
