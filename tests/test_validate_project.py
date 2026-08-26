from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture

from scripts.validate_project import main, validate_project


def _write(path: Path, content: str = "content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _valid_project(root: Path, profile: str = "python-ml") -> Path:
    dependencies = '["scikit-learn>=1.5"]'
    if profile != "python-ml":
        dependencies = '["mlflow>=3.1,<4", "scikit-learn>=1.5"]'
    _write(
        root / "pyproject.toml",
        f"""
[project]
name = "demo-project"
version = "0.1.0"
dependencies = {dependencies}

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
source = ["src"]
""".strip(),
    )
    _write(root / ".mlops-profile", profile)
    for relative in (
        "uv.lock",
        "README.md",
        ".gitignore",
        ".github/workflows/ci.yml",
        "src/demo_project/__init__.py",
        "tests/test_demo.py",
        "docs/architecture.md",
        "docs/configuration.md",
        "docs/testing.md",
    ):
        _write(root / relative)
    if profile != "python-ml":
        _write(root / "docs/mlflow.md")
        _write(root / "tests/integration/test_mlflow.py")
    if profile == "databricks-mlops":
        for relative in (
            "databricks.yml",
            "docs/databricks.md",
            "docs/operations.md",
            "docs/release-checklist.md",
            "docs/rollback.md",
            "tests/external/test_workspace.py",
        ):
            _write(root / relative)
    return root


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


def test_complete_databricks_profile_is_valid(tmp_path: Path) -> None:
    root = _valid_project(tmp_path, "databricks-mlops")
    _, issues = validate_project(root)
    assert issues == []


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
