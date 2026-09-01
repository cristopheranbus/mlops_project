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
Pytest with a default branch-coverage floor of 90%; and a package build check. Generated code,
notebooks, and declarative files need not count toward coverage.

## Ruff contract

Declare `ruff>=0.16.5,<0.17`, target Python 3.12, use a 100-character line length, and
set `preview = false`. Select this stable curated baseline explicitly:

```text
E, F, W, I, N, UP, B, A, ANN, ASYNC, BLE, C4, DTZ, EM, ERA, EXE, FA, FLY,
FURB, G, ICN, INP, INT, LOG, PIE, PT, PTH, Q, RET, RSE, S, SIM, SLOT, T10,
T20, TC, ARG, PERF, PGH, PLC, PLE, PLW, RUF
```

Do not select `ALL`, enable preview rules, add global ignores, or exclude `src`, `tests`,
or production notebooks. Additional stable selectors are allowed when the project needs
them. Keep exemptions code-specific and path-specific. The generated baseline permits:

- `S101` under `tests/**/*.py`, because pytest assertions are executable test evidence;
- `T201` in `src/**/cli.py`, because a CLI must write intentional user-facing output;
- `N999` in `notebooks/databricks/**/*.py`, because ordered notebook names such as
  `20_train.py` intentionally begin with a number.

For `databricks-mlops`, declare `dbutils`, `display`, and `spark` as Ruff builtins and
declare `notebooks` plus `notebooks/databricks` as namespace packages. Do not add those
runtime names to local-only profiles.

Use package `__init__.py` files where Python modules are intended to be packages. Run
safe fixes locally, inspect the diff, then format. CI only checks and never rewrites.
Generated `docs/testing.md` must explain the selected baseline, the three scoped
exceptions, how to read a rule code, and why blanket `noqa` comments are prohibited.

## CI

Generate numbered workflows with stable public names:

```text
01 - Code quality and package validation
02 - Repository security scanning
03 - Databricks bundle validation and deployment
04 - Production model monitoring
```

All profiles include `01` and `02`. Only `databricks-mlops` includes `03` and `04`.
Mirror local gates in `01`, including supported Python versions, Linux and Windows,
branch coverage, build, wheel installation smoke testing, and durable test reports.

Use `02` for CodeQL, dependency review, locked-dependency auditing, and supply-chain
controls. Default every workflow to `contents: read`, grant extra permissions per job,
never use `pull_request_target` to execute repository code, and pin every action to a
full commit SHA with a version comment.

External deployment is a separate job with a protected environment and workload identity.
A missing external credential must skip or block that job clearly, never turn it into a
false success. Fork pull requests never receive deployment credentials.

## Repository hygiene

Ignore virtual environments, caches, coverage output, local tracking stores, artifacts,
models, large data, notebook checkpoints, local credentials, and build output. Never
commit tokens, private keys, Databricks profiles, service-principal secrets, or production
host configuration. Do not declare completion while a required local gate fails.
