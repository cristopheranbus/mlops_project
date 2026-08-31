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

### Changed

- Generated projects now use exactly one primary package and keep all production Python
  logic under `src/<package>/`.
- Documentation navigation now provides dedicated paths for beginners, ML engineers,
  Databricks users, contributors, and maintainers.
- The default generated-project quality floor is now 90% branch coverage.

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
