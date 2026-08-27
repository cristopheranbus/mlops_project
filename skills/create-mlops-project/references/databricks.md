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
