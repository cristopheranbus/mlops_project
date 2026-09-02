# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Typed YAML configuration contract with `local`, `dev`, and `prod` environments,
  deterministic hashes, runtime overrides, and secret separation.
- Notebook-first Databricks layout and centralized MLflow run management with autolog.
- Immediate validator rules for configuration, Python, notebooks, Databricks tasks, and
  MLflow run boundaries.
- Beginner tutorial, configuration guide, notebooks and MLflow guide, and migration guide
  from `v0.1.0`.
- Dynamic cross-profile testing with `pytest_generate_tests`, typed contract cases,
  deterministic project factories, property-based testing, strict markers, and timeouts.
- Numbered workflows for quality, repository security, generated Databricks contracts,
  and production monitoring contracts.
- Extensive testing strategy and CI operations guides.
- Preventive `mlflow-security` contract that blocks MLflow AI Gateway configuration in
  generated projects, with regression tests and an operational security guide.
- Immediate `ruff-config` contract with a curated stable rule set, scoped profile
  exceptions, real-linter regression tests, and a beginner migration guide.
- Immediate `mypy-config` contract with strict typed boundaries, opt-in diagnostics,
  external-only overrides, real-analyzer regression tests, and an extensive Spanish guide.
- Automated branch-policy gate enforcing the `feature → dev → main` promotion model.

### Changed

- Mutation testing now uses the current Mutmut configuration names and pytest arguments,
  runs only validator-focused tests inside the isolated mutant workspace, and exposes
  operational failures instead of reporting a false-green scheduled workflow.
- Generated projects now use exactly one primary package and keep all production Python
  logic under `src/<package>/`.
- Documentation navigation now provides dedicated paths for beginners, ML engineers,
  Databricks users, contributors, and maintainers.
- The default generated-project quality floor is now 90% branch coverage.
- The development test runner now requires pytest 9.0.3 or newer to avoid
  `PYSEC-2026-1845`.
- Dependabot now batches monthly version updates by ecosystem, groups security updates
  separately, assigns the owner, and limits version-update PRs to prevent review floods.
- Ruff is now constrained to `>=0.16.5,<0.17` and enforced consistently in this repository,
  generated projects, validation, and CI without automatic fixes.
- `dev` is now the default integration branch; Dependabot targets it explicitly, while
  `main` is reserved for controlled merge-commit promotions.

## [0.1.0] - 2026-08-26

### Added

- Initial `create-mlops-project` skill with `python-ml`, `mlflow-local`, and
  `databricks-mlops` profiles.
- Structural validator with automated tests and coverage enforcement.
- Architecture, quality, testing, MLflow, and Databricks standards.
- Complete user, maintainer, governance, contribution, and security documentation.
- Codex plugin manifest for reusable installation and distribution.
- GitHub Actions, CODEOWNERS, pull request template, and structured issue forms.

[Unreleased]: https://github.com/cristopheranbus/mlops_project/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cristopheranbus/mlops_project/releases/tag/v0.1.0
