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
        ROOT / ".github" / "workflows" / "ci.yml",
        *sorted((ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml")),
    ]

    for path in yaml_files:
        assert yaml.safe_load(path.read_text(encoding="utf-8")) is not None, path
