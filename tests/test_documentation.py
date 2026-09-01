from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")


def _markdown_files() -> list[Path]:
    ignored_parts = {".git", ".venv", ".pytest_cache", ".pytest-tmp"}
    return [
        path for path in ROOT.rglob("*.md") if not any(part in ignored_parts for part in path.parts)
    ]


def test_local_markdown_links_resolve() -> None:
    broken: list[str] = []
    for source in _markdown_files():
        content = source.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(content):
            target = raw_target.strip()
            if target.startswith(EXTERNAL_PREFIXES) or target.startswith("<"):
                continue
            relative = target.split("#", maxsplit=1)[0]
            if relative and not (source.parent / relative).exists():
                broken.append(f"{source.relative_to(ROOT)} -> {target}")

    assert broken == []


def test_documentation_index_lists_every_guide() -> None:
    index = (DOCS / "README.md").read_text(encoding="utf-8")
    guides = sorted(path.name for path in DOCS.glob("*.md") if path.name != "README.md")

    missing = [name for name in guides if f"({name})" not in index]
    assert missing == []


def test_beginner_documentation_covers_first_local_path() -> None:
    tutorial = (DOCS / "beginner-tutorial.md").read_text(encoding="utf-8")
    required = (
        "Git",
        "Python",
        "uv",
        "primera prueba",
        "--environment local",
        "error del validador",
        "pull request",
    )

    assert all(term.lower() in tutorial.lower() for term in required)


def test_runtime_contract_guides_cover_public_interfaces() -> None:
    configuration = (DOCS / "configuration.md").read_text(encoding="utf-8")
    tracking = (DOCS / "notebooks-mlflow.md").read_text(encoding="utf-8")

    assert all(
        term in configuration
        for term in ("AppConfig", "load_config", "config_hash", "resolved_config.yaml")
    )
    assert all(
        term in tracking for term in ("start_experiment_run", "mlflow.autolog", "notebook_task")
    )


def test_testing_and_ci_guides_cover_operational_interfaces() -> None:
    testing = (DOCS / "testing-strategy.md").read_text(encoding="utf-8")
    workflows = (DOCS / "ci-workflows.md").read_text(encoding="utf-8")

    assert all(
        term in testing
        for term in ("pytest_generate_tests", "--run-external", "Hypothesis", "branch coverage")
    )
    assert all(
        term in workflows
        for term in (
            "01 - Code quality",
            "02 - Repository security",
            "03 - Databricks",
            "04 - Production model monitoring",
            "contents: read",
        )
    )


def test_mlflow_security_guide_covers_boundary_and_official_sources() -> None:
    security = (DOCS / "mlflow-security.md").read_text(encoding="utf-8")

    assert all(
        term in security
        for term in (
            "mlflow-security",
            "AI Gateway",
            "api_base",
            "SSRF",
            "allowlist",
            "egress",
            "GHSA-h7x2-h6g9-p789",
            "https://mlflow.org/docs/latest/self-hosting/security/",
        )
    )


def test_ruff_guide_covers_contract_migration_and_official_sources() -> None:
    guide = (DOCS / "ruff.md").read_text(encoding="utf-8")

    assert all(
        term in guide
        for term in (
            "ruff-config",
            "preview = false",
            "S101",
            "T201",
            "N999",
            "RUF100",
            "https://docs.astral.sh/ruff/configuration/",
            "https://docs.astral.sh/ruff/linter/#rule-selection",
            "https://docs.astral.sh/ruff/rules/",
            "https://docs.astral.sh/ruff/formatter/",
        )
    )


def test_mypy_guide_covers_contract_migration_and_official_sources() -> None:
    guide = (DOCS / "mypy.md").read_text(encoding="utf-8")

    assert all(
        term in guide
        for term in (
            "mypy-config",
            "disallow_any_explicit",
            "explicit-override",
            "exhaustive-match",
            "possibly-undefined",
            "TypeGuard",
            "TypedDict",
            "Protocol",
            "types-PyYAML",
            "https://mypy.readthedocs.io/en/stable/config_file.html",
            "https://mypy.readthedocs.io/en/stable/error_codes.html",
            "https://mypy.readthedocs.io/en/stable/type_narrowing.html",
        )
    )
