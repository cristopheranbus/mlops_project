# Configuration standard

Apply this standard to every generated profile.

## Files and ownership

- Version `configs/base.yaml` and `configs/local.yaml` for every project.
- Add `configs/dev.yaml` and `configs/prod.yaml` for `databricks-mlops`.
- Put typed models in `src/<package_name>/config/models.py`, deterministic loading and
  merging in `loader.py`, and canonical hashing in `hashing.py`.
- Workflows and notebooks receive the validated `AppConfig`; they do not read YAML
  directly.
- Keep bundle resource variables in Databricks bundle configuration, not application
  YAML.

## Schema and precedence

- Require `config_version: 1` and validate with frozen Pydantic models using strict types
  and `extra="forbid"`.
- Resolve `base.yaml`, then the selected environment file, then explicit runtime
  overrides. Deep-merge mappings; replace lists and scalar values; allow `null` only for
  optional fields.
- Support `local`, `dev`, and `prod`. Local CLI execution may default to `local`;
  Databricks Jobs and production execution must select the environment explicitly.
- Expose CLI `--environment` and repeatable `--set key=value`. Databricks notebooks use
  `environment`, `run_name`, and `config_overrides_json` widgets.

## Reproducibility and secrets

- Produce a canonical JSON representation and SHA-256 hash of the resolved configuration.
- Preserve the environment and applied overrides with the execution result. MLflow
  profiles log `config.version`, `config.environment`, and `config.hash`, plus a redacted
  `resolved_config.yaml` artifact.
- Never model or serialize credentials, tokens, passwords, private keys, or secret-scope
  values. Obtain them separately from the runtime.
- Add Pydantic and PyYAML with bounded versions to generated projects.

## Generated documentation

Explain the four files, precedence, merge behavior, common validation errors, CLI and
notebook overrides, hashing, and the separation between parameters, infrastructure, and
secrets. Include one complete resolved example that a beginner can reproduce locally.
