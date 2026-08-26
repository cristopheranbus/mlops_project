# Quality standard

## Reproducibility and packaging

- Manage Python with `uv`; commit `pyproject.toml` and `uv.lock`.
- Use explicit Python and dependency constraints. Avoid `latest`, floating external
  branches, and unbounded critical dependencies.
- Make the package buildable and keep generated distributions out of Git.
- Provide `.env.example` only when environment variables exist, with safe example values.

## Required gates

Configure and run, adapting paths but not weakening intent without documenting why:

```text
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```

Use Ruff for lint, imports, and formatting; MyPy with strict checking for owned source;
Pytest with a default coverage floor of 85%; and a package build check. Generated code,
notebooks, and declarative files need not count toward coverage.

## CI

Mirror the local gates in GitHub Actions. Use minimum permissions, concurrency controls,
fixed Python versions, and stable pinned action releases. External deployment is a
separate job with an explicit environment and credentials. A missing external credential
must skip or block that job clearly, never turn it into a false success.

## Repository hygiene

Ignore virtual environments, caches, coverage output, local tracking stores, artifacts,
models, large data, notebook checkpoints, local credentials, and build output. Never
commit tokens, private keys, Databricks profiles, service-principal secrets, or production
host configuration. Do not declare completion while a required local gate fails.

