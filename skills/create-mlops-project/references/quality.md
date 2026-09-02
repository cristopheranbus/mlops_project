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

## Mypy contract

Declare `mypy>=2.3.1,<2.4` and `types-pyyaml>=6.0.12,<7`. Check owned `src` and `tests`
with Python 3.12, `strict = true`, `warn_unused_configs`, `disallow_any_explicit`,
`disallow_any_unimported`, `strict_bytes`, `strict_equality_for_none`, error-code display,
and these opt-in codes:

```text
deprecated, explicit-override, exhaustive-match, ignore-without-code,
mutable-override, possibly-undefined, redundant-expr, redundant-self,
truthy-bool, truthy-iterable, unused-awaitable
```

Do not set global `ignore_missing_imports`, `ignore_errors`, `follow_imports = "skip"`,
`disable_error_code`, or exclusions that hide owned code. An override may only target a
specific external namespace and must not weaken the primary package or tests. Prefer a
typed release, a `types-*` package, a local `.pyi` stub, or a typed adapter before such an
override. If `mypy_path` declares `typings`, version that directory.

Keep Databricks notebooks out of mypy's direct scope. Their production logic belongs in
typed workflows under `src/<package>/`; notebook runtime globals stay at the thin boundary.
Generate `docs/mypy.md` with beginner instructions, configuration, every opt-in code,
narrowing, stubs, external adapters, ignores, casts, troubleshooting, migration, CI commands,
and official links.

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
Run mypy in a dedicated Ubuntu matrix for Python 3.12 and 3.13 with `--no-incremental` and
publish JUnit even when it fails. Include a branch-policy job in the `quality` aggregator:
features and Dependabot target `dev`, only `dev` promotes to `main`, and `main → dev` is
reserved for merge-commit synchronization. Features use squash into `dev`; promotions and
cross-branch synchronizations use merge commits.

Use `02` for CodeQL, dependency review, locked-dependency auditing, and supply-chain
controls. Default every workflow to `contents: read`, grant extra permissions per job,
never use `pull_request_target` to execute repository code, and pin every action to a
full commit SHA with a version comment.

Generate `.github/dependabot.yml` with `target-branch: dev`, grouped monthly version updates,
a low open-PR limit per ecosystem, and separately grouped security updates. Do not generate
auto-approve or auto-merge. Explain that this file does not enable Dependabot alerts,
Dependabot security updates, secret scanning, or push protection: those are hosted repository
settings. Include a post-publication checklist and official GitHub links in the generated
operations documentation. Do not mutate remote settings unless the user explicitly requests
it and the target repository has been verified.

Use GitHub's official guides for
[Dependabot alerts](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-dependabot-alerts),
[Dependabot security updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates),
[secret scanning](https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enable-secret-scanning),
and [push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection).

External deployment is a separate job with a protected environment and workload identity.
A missing external credential must skip or block that job clearly, never turn it into a
false success. Fork pull requests never receive deployment credentials.

## Repository hygiene

Ignore virtual environments, caches, coverage output, local tracking stores, artifacts,
models, large data, notebook checkpoints, local credentials, and build output. Never
commit tokens, private keys, Databricks profiles, service-principal secrets, or production
host configuration. Do not declare completion while a required local gate fails.
