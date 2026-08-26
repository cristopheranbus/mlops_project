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
