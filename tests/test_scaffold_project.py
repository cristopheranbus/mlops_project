"""Tests for the deterministic project generator."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from scripts.scaffold_project import PROFILES, Profile, create_project, main, normalize_package
from scripts.validate_project import validate_project

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("profile", PROFILES)
def test_generator_creates_each_valid_profile(tmp_path: Path, profile: Profile) -> None:
    root = create_project(tmp_path / profile, "risk-model", profile=profile)

    resolved, issues = validate_project(root, profile)

    assert resolved == profile
    assert not [issue for issue in issues if issue.severity == "error"]
    assert (root / "src/risk_model").is_dir()


def test_generator_can_embed_repo_local_skill(tmp_path: Path) -> None:
    root = create_project(tmp_path / "repo", "repo", embed_skill=True)

    assert (root / ".agents/skills/create-mlops-project/SKILL.md").is_file()
    assert (root / ".agents/skills/create-mlops-project/scripts/scaffold_project.py").is_file()


def test_generator_refuses_non_empty_destination(tmp_path: Path) -> None:
    destination = tmp_path / "existing"
    destination.mkdir()
    (destination / "owned.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(FileExistsError, match="not empty"):
        create_project(destination, "safe-project")

    assert (destination / "owned.txt").read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Customer Churn", "customer_churn"),
        ("123 model", "ml_123_model"),
        ("class", "ml_class"),
    ],
)
def test_package_normalization(name: str, expected: str) -> None:
    assert normalize_package(name) == expected


def test_invalid_names_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="letters or digits"):
        create_project(tmp_path / "bad", "---")
    with pytest.raises(ValueError, match="invalid Python package"):
        create_project(tmp_path / "bad-package", "valid", package_name="not-valid")


def test_cli_supports_offline_generation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    destination = tmp_path / "cli-project"

    assert main([str(destination), "--name", "CLI Project", "--skip-lock"]) == 0
    assert f"Created {destination.resolve()}" in capsys.readouterr().out
