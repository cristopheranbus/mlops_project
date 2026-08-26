"""Validate structural MLOps project invariants without modifying the project."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

Profile = Literal["python-ml", "mlflow-local", "databricks-mlops"]
PROFILES: tuple[Profile, ...] = ("python-ml", "mlflow-local", "databricks-mlops")
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yml", ".yaml", ".json", ".txt"}
PLACEHOLDER_PATTERNS = (
    re.compile(r"\b(?:TODO|FIXME|CHANGEME)\b", re.IGNORECASE),
    re.compile(r"\{\{[^{}]+\}\}"),
    re.compile(r"<\s*(?:package|project|target)[_-]?name\s*>", re.IGNORECASE),
)
SECRET_NAME_PATTERNS = (
    re.compile(r"^\.env$", re.IGNORECASE),
    re.compile(r"^\.databrickscfg$", re.IGNORECASE),
    re.compile(r"\.(?:pem|key|p12|pfx)$", re.IGNORECASE),
)


@dataclass(frozen=True)
class Issue:
    severity: Literal["error", "warning"]
    code: str
    message: str


def _require(root: Path, relative: str, issues: list[Issue]) -> None:
    if not (root / relative).exists():
        issues.append(Issue("error", "missing", f"Required path is missing: {relative}"))


def _load_pyproject(path: Path, issues: list[Issue]) -> dict[str, object]:
    try:
        with path.open("rb") as stream:
            return tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        issues.append(Issue("error", "pyproject", f"Cannot read pyproject.toml: {exc}"))
        return {}


def _tool_table(data: dict[str, object], name: str) -> object | None:
    tool = data.get("tool")
    return tool.get(name) if isinstance(tool, dict) else None


def _dependency_strings(data: dict[str, object]) -> list[str]:
    values: list[str] = []
    project = data.get("project")
    if isinstance(project, dict):
        dependencies = project.get("dependencies", [])
        if isinstance(dependencies, list):
            values.extend(str(item).lower() for item in dependencies)
        optional = project.get("optional-dependencies", {})
        if isinstance(optional, dict):
            for group in optional.values():
                if isinstance(group, list):
                    values.extend(str(item).lower() for item in group)
    groups = data.get("dependency-groups")
    if isinstance(groups, dict):
        for group in groups.values():
            if isinstance(group, list):
                values.extend(str(item).lower() for item in group)
    return values


def _infer_profile(root: Path, requested: str, issues: list[Issue]) -> Profile:
    if requested != "auto":
        return cast(Profile, requested)
    marker = root / ".mlops-profile"
    if marker.is_file():
        value = marker.read_text(encoding="utf-8").strip()
        if value in PROFILES:
            return value
        issues.append(Issue("error", "profile", f"Unknown profile in .mlops-profile: {value}"))
    if (root / "databricks.yml").exists():
        return "databricks-mlops"
    return "mlflow-local" if (root / "docs" / "mlflow.md").exists() else "python-ml"


def _scan_files(root: Path, issues: list[Issue]) -> None:
    ignored_parts = {".git", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    for path in root.rglob("*"):
        if any(part in ignored_parts for part in path.parts) or not path.is_file():
            continue
        if any(pattern.search(path.name) for pattern in SECRET_NAME_PATTERNS):
            issues.append(
                Issue("error", "secret-file", f"Potential secret file: {path.relative_to(root)}")
            )
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(root)
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(content):
                issues.append(
                    Issue("error", "placeholder", f"Unresolved placeholder in {relative}")
                )
                break
        if re.search(r"\biris\b", content, re.IGNORECASE):
            issues.append(
                Issue("error", "example-leak", f"Example-specific name 'iris' found in {relative}")
            )


def validate_project(root: Path, requested_profile: str = "auto") -> tuple[Profile, list[Issue]]:
    """Return the resolved profile and all validation issues."""
    issues: list[Issue] = []
    root = root.resolve()
    if not root.is_dir():
        return "python-ml", [Issue("error", "path", f"Project directory does not exist: {root}")]

    profile = _infer_profile(root, requested_profile, issues)
    for relative in (
        "pyproject.toml",
        "uv.lock",
        "src",
        "tests",
        "README.md",
        ".gitignore",
        ".github/workflows/ci.yml",
        "docs/architecture.md",
        "docs/configuration.md",
        "docs/testing.md",
    ):
        _require(root, relative, issues)

    pyproject_path = root / "pyproject.toml"
    data = _load_pyproject(pyproject_path, issues) if pyproject_path.is_file() else {}
    for tool_name in ("ruff", "mypy", "pytest"):
        if _tool_table(data, tool_name) is None:
            issues.append(
                Issue("error", "quality-config", f"Missing [tool.{tool_name}] configuration")
            )
    if _tool_table(data, "coverage") is None:
        issues.append(Issue("error", "coverage-config", "Missing [tool.coverage] configuration"))

    src = root / "src"
    packages = (
        [path for path in src.iterdir() if path.is_dir() and not path.name.startswith(".")]
        if src.is_dir()
        else []
    )
    if not packages:
        issues.append(Issue("error", "package", "No importable package directory found under src"))
    test_files = list((root / "tests").rglob("test_*.py")) if (root / "tests").is_dir() else []
    if not test_files:
        issues.append(Issue("error", "tests", "No test_*.py files found"))

    dependencies = _dependency_strings(data)
    if profile in {"mlflow-local", "databricks-mlops"}:
        if not any(item.startswith("mlflow") for item in dependencies):
            issues.append(Issue("error", "mlflow", "MLflow profile requires an mlflow dependency"))
        for relative in ("docs/mlflow.md", "tests/integration"):
            _require(root, relative, issues)
    if profile == "databricks-mlops":
        for relative in (
            "databricks.yml",
            "docs/databricks.md",
            "docs/operations.md",
            "docs/release-checklist.md",
            "docs/rollback.md",
            "tests/external",
        ):
            _require(root, relative, issues)

    _scan_files(root, issues)
    return profile, issues


def _format_issues(issues: Iterable[Issue]) -> str:
    return "\n".join(f"{issue.severity.upper()} [{issue.code}] {issue.message}" for issue in issues)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--profile", choices=("auto", *PROFILES), default="auto")
    args = parser.parse_args(argv)
    profile, issues = validate_project(args.project_root, args.profile)
    print(f"Profile: {profile}")
    if issues:
        print(_format_issues(issues))
    errors = sum(issue.severity == "error" for issue in issues)
    warnings = sum(issue.severity == "warning" for issue in issues)
    print(f"Result: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
