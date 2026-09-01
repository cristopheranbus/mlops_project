"""Execute pinned mypy against representative generated projects."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.project_factory import build_valid_project, write


def _mypy_executable() -> str:
    scripts_dir = Path(sys.executable).parent
    candidate = scripts_dir / ("mypy.exe" if sys.platform == "win32" else "mypy")
    executable = str(candidate) if candidate.is_file() else shutil.which("mypy")
    assert executable is not None
    return executable


def _run_mypy(root: Path, python_version: str = "3.12") -> subprocess.CompletedProcess[str]:
    command = [
        _mypy_executable(),
        "--config-file",
        str(root / "pyproject.toml"),
        "--no-incremental",
        "--python-version",
        python_version,
    ]
    # The executable is the repository-pinned mypy binary, not untrusted input.
    return subprocess.run(  # noqa: S603
        command,
        capture_output=True,
        check=False,
        cwd=root,
        text=True,
    )


@pytest.mark.parametrize("profile", ["python-ml", "mlflow-local", "databricks-mlops"])
@pytest.mark.parametrize("python_version", ["3.12", "3.13"])
def test_generated_profiles_pass_real_mypy(
    tmp_path: Path,
    profile: str,
    python_version: str,
) -> None:
    root = build_valid_project(tmp_path, profile)

    result = _run_mypy(root, python_version)

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("source", "error_code"),
    [
        ("def missing_annotation(value):\n    return value\n", "no-untyped-def"),
        ("from typing import Any\nVALUE: Any = 1\n", "explicit-any"),
        ("VALUE: str = 1  # type: ignore\n", "ignore-without-code"),
        (
            "def choose(enabled: bool) -> int:\n"
            "    if enabled:\n"
            "        value = 1\n"
            "    return value\n",
            "possibly-undefined",
        ),
        (
            "async def operation() -> int:\n"
            "    return 1\n\n"
            "async def caller() -> None:\n"
            "    operation()\n",
            "unused-coroutine",
        ),
    ],
)
def test_strict_mypy_rejects_unsafe_code(
    tmp_path: Path,
    source: str,
    error_code: str,
) -> None:
    root = build_valid_project(tmp_path)
    write(root / "src/demo_project/modeling/unsafe.py", source)

    result = _run_mypy(root)

    assert result.returncode == 1
    assert f"[{error_code}]" in result.stdout


def test_mypy_rejects_incomplete_match(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    write(
        root / "src/demo_project/modeling/match.py",
        """from typing import Literal

def label(value: Literal["yes", "no"]) -> str:
    match value:
        case "yes":
            return "accepted"
""",
    )

    result = _run_mypy(root)

    assert result.returncode == 1
    assert "[return]" in result.stdout or "[exhaustive-match]" in result.stdout


def test_mypy_requires_override_decorator(tmp_path: Path) -> None:
    root = build_valid_project(tmp_path)
    write(
        root / "src/demo_project/modeling/override.py",
        """class Base:
    def train(self) -> int:
        return 1

class Child(Base):
    def train(self) -> int:
        return 2
""",
    )

    result = _run_mypy(root)

    assert result.returncode == 1
    assert "[explicit-override]" in result.stdout
