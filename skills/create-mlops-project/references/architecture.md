# Architecture standard

Apply this standard in proportion to the selected profile and the problem's real needs.

## Required shape

- Use exactly one primary package at `src/<package_name>` and keep imports package-based.
- Put configuration loading under `config/`, domain transformations under `data/`,
  `features/`, or `modeling/`, orchestration under `workflows/`, and tracking adapters
  under `tracking/` when applicable.
- Separate configuration, data access, feature preparation, training, evaluation, and
  inference contracts. Add registry, deployment, and serving modules only when relevant.
- Keep orchestration entry points thin. Production notebooks may parse runtime parameters,
  load configuration, import one package workflow, and invoke it; they must not declare
  functions or classes. Optional exploratory notebooks live under `notebooks/exploration`
  and are never Job entry points.
- Keep configuration versioned and environment-neutral. Load secrets from the runtime,
  never from committed values.
- Provide a local path that runs without production services. Put external integrations
  behind explicit adapters or runtime boundaries.
- Separate model training, independent evaluation, approval, deployment, smoke testing,
  and promotion when the selected profile includes those stages.

## Project documentation

Every project includes `README.md` plus `docs/architecture.md`, `docs/configuration.md`,
and `docs/testing.md`. The README must include a first local run, a directory map,
configuration changes, quality commands, common errors, and credential boundaries. It
must teach a beginner what works without credentials and how to run tests before a pull
request. Add `docs/mlflow.md` for MLflow profiles and explain how to locate a run and the
resolved configuration that produced it. Add
`docs/databricks.md`, `docs/operations.md`, `docs/release-checklist.md`, and
`docs/rollback.md` for production deployment, including how to invoke a production
notebook and which steps require a live workspace.

Document where each component executes, which system is authoritative, what can run
locally, and which validations require credentials. Do not generate Databricks resources
for projects that selected a smaller profile.
