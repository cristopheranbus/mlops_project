"""Validate structural MLOps project invariants without modifying the project."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tomllib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml

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
SENSITIVE_CONFIG_KEY = re.compile(r"(?:password|private[_-]?key|secret|token)", re.IGNORECASE)
PYTHON_DEFINITION = re.compile(r"^\s*(?:async\s+def|def|class)\s+", re.MULTILINE)


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


def _load_yaml(path: Path, issues: list[Issue], code: str) -> dict[str, Any] | None:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        issues.append(Issue("error", code, f"Cannot read YAML file {path.name}: {exc}"))
        return None
    if not isinstance(loaded, dict):
        issues.append(Issue("error", code, f"YAML root must be a mapping: {path.name}"))
        return None
    return cast(dict[str, Any], loaded)


def _primary_package(root: Path, issues: list[Issue]) -> Path | None:
    src = root / "src"
    packages = (
        [path for path in src.iterdir() if path.is_dir() and not path.name.startswith(".")]
        if src.is_dir()
        else []
    )
    if len(packages) != 1:
        issues.append(
            Issue(
                "error",
                "package",
                f"Expected exactly one primary package under src; found {len(packages)}",
            )
        )
        return None
    return packages[0]


def _contains_sensitive_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            SENSITIVE_CONFIG_KEY.search(str(key)) or _contains_sensitive_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _validate_configuration(
    root: Path,
    package: Path | None,
    profile: Profile,
    dependencies: list[str],
    issues: list[Issue],
) -> None:
    required = ["base.yaml", "local.yaml"]
    if profile == "databricks-mlops":
        required.extend(("dev.yaml", "prod.yaml"))
    configs = root / "configs"
    for name in required:
        path = configs / name
        if not path.is_file():
            issues.append(
                Issue("error", "config-layout", f"Required config is missing: configs/{name}")
            )
            continue
        data = _load_yaml(path, issues, "config-format")
        if data is None:
            continue
        if data.get("config_version") != 1:
            issues.append(
                Issue("error", "config-format", f"configs/{name} must declare config_version: 1")
            )
        if _contains_sensitive_key(data):
            issues.append(
                Issue(
                    "error",
                    "config-secret",
                    f"Sensitive key found in versioned config: configs/{name}",
                )
            )
    if not any(item.startswith("pydantic") for item in dependencies):
        issues.append(
            Issue("error", "config-layout", "Configuration requires a pydantic dependency")
        )
    if not any(item.startswith("pyyaml") for item in dependencies):
        issues.append(Issue("error", "config-layout", "Configuration requires a pyyaml dependency"))
    if package is not None:
        for relative in (
            "config/models.py",
            "config/loader.py",
            "config/hashing.py",
            "workflows",
        ):
            if not (package / relative).exists():
                issues.append(
                    Issue(
                        "error",
                        "config-layout",
                        f"Required package component is missing: src/{package.name}/{relative}",
                    )
                )


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _python_tree(path: Path, issues: list[Issue], code: str) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        issues.append(Issue("error", code, f"Cannot parse Python file {path}: {exc}"))
        return None


def _validate_python_layout(root: Path, issues: list[Issue]) -> None:
    ignored = {".git", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    for path in root.rglob("*.py"):
        relative = path.relative_to(root)
        if any(part in ignored for part in relative.parts):
            continue
        if relative.parts[0] in {"src", "tests", "notebooks"}:
            continue
        tree = _python_tree(path, issues, "python-layout")
        if tree is not None and any(
            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
            for node in tree.body
        ):
            issues.append(
                Issue(
                    "error",
                    "python-layout",
                    f"Reusable Python definitions must live under src: {relative}",
                )
            )


def _validate_mlflow(root: Path, package: Path | None, issues: list[Issue]) -> None:
    if package is None:
        return
    adapter = package / "tracking" / "mlflow.py"
    if not adapter.is_file():
        issues.append(
            Issue(
                "error",
                "mlflow-run",
                f"Missing canonical MLflow adapter: src/{package.name}/tracking/mlflow.py",
            )
        )
        return
    tree = _python_tree(adapter, issues, "mlflow-run")
    if tree is None:
        return
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.name == "start_experiment_run"
    ]
    valid_context = False
    if functions:
        for node in ast.walk(functions[0]):
            if not isinstance(node, ast.With | ast.AsyncWith):
                continue
            start_calls = [
                call
                for item in node.items
                for call in ast.walk(item.context_expr)
                if isinstance(call, ast.Call) and _call_name(call.func).endswith("mlflow.start_run")
            ]
            if not start_calls:
                continue
            autolog_lines = [
                child.lineno
                for child in ast.walk(node)
                if isinstance(child, ast.Call) and _call_name(child.func).endswith("mlflow.autolog")
            ]
            yield_lines = [
                child.lineno
                for child in ast.walk(node)
                if isinstance(child, ast.Yield | ast.YieldFrom)
            ]
            valid_context = bool(
                autolog_lines and yield_lines and min(autolog_lines) < min(yield_lines)
            )
    source = adapter.read_text(encoding="utf-8")
    evidence = ("config.version", "config.environment", "config.hash", "resolved_config.yaml")
    if not valid_context or not all(item in source for item in evidence):
        issues.append(
            Issue(
                "error",
                "mlflow-run",
                "start_experiment_run must open start_run, enable autolog before yield, "
                "and log config evidence",
            )
        )
    for path in package.rglob("*.py"):
        if path == adapter:
            continue
        other_tree = _python_tree(path, issues, "mlflow-run")
        if other_tree is not None and any(
            isinstance(node, ast.Call) and _call_name(node.func).endswith("mlflow.start_run")
            for node in ast.walk(other_tree)
        ):
            issues.append(
                Issue(
                    "error",
                    "mlflow-run",
                    "Direct mlflow.start_run call outside tracking adapter: "
                    f"{path.relative_to(root)}",
                )
            )
    workflows = package / "workflows"
    workflow_sources = [path.read_text(encoding="utf-8") for path in workflows.glob("*.py")]
    if not any("start_experiment_run" in source_text for source_text in workflow_sources):
        issues.append(
            Issue("error", "mlflow-run", "At least one workflow must use start_experiment_run")
        )


def _notebook_source(path: Path, issues: list[Issue]) -> str | None:
    if path.suffix == ".py":
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(Issue("error", "notebook-format", f"Cannot read notebook {path}: {exc}"))
            return None
        if not source.startswith("# Databricks notebook source"):
            issues.append(
                Issue(
                    "error", "notebook-format", f"Source notebook lacks Databricks marker: {path}"
                )
            )
        return source
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        issues.append(
            Issue("error", "notebook-format", f"Cannot read IPYNB notebook {path}: {exc}")
        )
        return None
    if not isinstance(notebook, dict) or notebook.get("nbformat") != 4:
        issues.append(Issue("error", "notebook-format", f"IPYNB must use nbformat 4: {path}"))
        return None
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        issues.append(Issue("error", "notebook-format", f"IPYNB cells must be a list: {path}"))
        return None
    sources: list[str] = []
    for cell in cells:
        if not isinstance(cell, dict) or cell.get("cell_type") != "code":
            continue
        raw_source = cell.get("source", "")
        if isinstance(raw_source, list):
            sources.append("".join(str(item) for item in raw_source))
        else:
            sources.append(str(raw_source))
        if cell.get("outputs", []) != [] or cell.get("execution_count") is not None:
            issues.append(
                Issue(
                    "error",
                    "notebook-format",
                    f"IPYNB outputs and execution counts must be cleared: {path}",
                )
            )
            break
    return "\n".join(sources)


def _walk_mappings(value: object) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        mapping = cast(dict[str, Any], value)
        yield mapping
        for child in mapping.values():
            yield from _walk_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_mappings(child)


def _validate_databricks(root: Path, package: Path | None, issues: list[Issue]) -> None:
    notebook_root = root / "notebooks" / "databricks"
    notebooks = (
        sorted((*notebook_root.rglob("*.py"), *notebook_root.rglob("*.ipynb")))
        if notebook_root.is_dir()
        else []
    )
    if not notebooks:
        issues.append(
            Issue(
                "error",
                "notebook-layout",
                "No production notebook found under notebooks/databricks",
            )
        )
        return
    identities: set[str] = set()
    for path in notebooks:
        identity = str(path.relative_to(notebook_root).with_suffix("")).lower()
        if identity in identities:
            issues.append(
                Issue("error", "notebook-format", f"Duplicate notebook formats for {identity}")
            )
        identities.add(identity)
        source = _notebook_source(path, issues)
        if source is None:
            continue
        relative = path.relative_to(root)
        if PYTHON_DEFINITION.search(source):
            issues.append(
                Issue(
                    "error", "notebook-layout", f"Notebook declares a function or class: {relative}"
                )
            )
        if package is not None and not re.search(
            rf"(?:from\s+{re.escape(package.name)}\.workflows|import\s+{re.escape(package.name)}\.workflows)",
            source,
        ):
            issues.append(
                Issue(
                    "error",
                    "notebook-layout",
                    f"Notebook must import package workflows: {relative}",
                )
            )

    yaml_paths = [root / "databricks.yml"]
    resources = root / "resources"
    if resources.is_dir():
        yaml_paths.extend(sorted((*resources.rglob("*.yml"), *resources.rglob("*.yaml"))))
    notebook_tasks: list[tuple[Path, str]] = []
    for yaml_path in yaml_paths:
        if not yaml_path.is_file():
            continue
        data = _load_yaml(yaml_path, issues, "databricks-task")
        if data is None:
            continue
        for mapping in _walk_mappings(data):
            task = mapping.get("notebook_task")
            if isinstance(task, dict) and isinstance(task.get("notebook_path"), str):
                notebook_tasks.append((yaml_path, cast(str, task["notebook_path"])))
    if not notebook_tasks:
        issues.append(Issue("error", "databricks-task", "Bundle must define a notebook_task"))
        return
    notebook_root_resolved = notebook_root.resolve()
    for yaml_path, notebook_path in notebook_tasks:
        candidate = (yaml_path.parent / notebook_path).resolve()
        if not candidate.is_relative_to(notebook_root_resolved) or not candidate.is_file():
            issues.append(
                Issue(
                    "error",
                    "databricks-task",
                    "Notebook task must reference an existing file under "
                    f"notebooks/databricks: {notebook_path}",
                )
            )


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

    package = _primary_package(root, issues)
    test_files = list((root / "tests").rglob("test_*.py")) if (root / "tests").is_dir() else []
    if not test_files:
        issues.append(Issue("error", "tests", "No test_*.py files found"))

    dependencies = _dependency_strings(data)
    _validate_configuration(root, package, profile, dependencies, issues)
    _validate_python_layout(root, issues)
    if profile in {"mlflow-local", "databricks-mlops"}:
        if not any(item.startswith("mlflow") for item in dependencies):
            issues.append(Issue("error", "mlflow", "MLflow profile requires an mlflow dependency"))
        for relative in ("docs/mlflow.md", "tests/integration"):
            _require(root, relative, issues)
        _validate_mlflow(root, package, issues)
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
        _validate_databricks(root, package, issues)

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
