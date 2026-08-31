# Databricks profile

- Declare workspace resources with Databricks Asset Bundles and keep `databricks.yml` as
  the infrastructure source of truth.
- Provide at least `dev` and `prod` targets with environment-specific variables.
- Build and deploy the shared Python package as a wheel. Use notebook-first Job entry
  points under `notebooks/databricks/`; they load widgets and configuration, import a
  package workflow, and invoke it without declaring functions or classes.
- Accept source-format `.py` notebooks whose first line is
  `# Databricks notebook source` and output-free `nbformat: 4` `.ipynb` notebooks. Do not
  keep both formats for the same notebook name.
- Require bundle `notebook_task` paths to resolve inside `notebooks/databricks/`.
  `notebooks/exploration/` is optional and must never be referenced by a Job.
- Use Unity Catalog for governed registered models and exact model versions.
- Separate evaluation, approval, deployment, smoke test, and Champion promotion tasks.
- Use GitHub OIDC and a production service principal. Never commit static tokens.
- Apply minimum job and environment permissions. Production requires an explicit approval
  boundary when requested by the organization.
- Validate the bundle locally when possible, but distinguish that from an authorized
  workspace deployment.
- Promote only after the endpoint is ready and the exact approved version passes a smoke
  test. Preserve the previous Champion and document rollback.
- Include operational, release, and rollback instructions and identify which checks need
  a live workspace.
- Generate `.github/workflows/03-databricks.yml` with the public name
  `03 - Databricks bundle validation and deployment`. Pull requests run offline contract
  tests and `databricks bundle validate`; deployment uses workload identity, a protected
  environment, explicit targets, and never runs with production credentials on fork PRs.
- Generate `.github/workflows/04-production-monitoring.yml` with the public name
  `04 - Production model monitoring`. It is scheduled and manually runnable, reads the
  exact model version and configuration hash, checks freshness, schema, drift,
  performance and serving health, and emits auditable evidence. Monitoring must not
  retrain, approve, or promote a model as an implicit side effect.
