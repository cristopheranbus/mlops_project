from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any, cast

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
SKILL_ROOT = ROOT / "skills" / "create-mlops-project"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ACTION_REF = re.compile(r"uses:\s*[^@\s]+@([^\s#]+)")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)


def _plugin_manifest() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8")))


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
