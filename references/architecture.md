# Architecture standard

Apply this standard in proportion to the selected profile and the problem's real needs.

## Required shape

- Use `src/<package_name>` and keep imports package-based.
- Separate configuration, data access, feature preparation, training, evaluation, and
  inference contracts. Add registry, deployment, and serving modules only when relevant.
- Keep orchestration entry points thin. Notebooks may explore or invoke package functions,
  but must not become the only home of reusable or tested logic.
- Keep configuration versioned and environment-neutral. Load secrets from the runtime,
  never from committed values.
- Provide a local path that runs without production services. Put external integrations
  behind explicit adapters or runtime boundaries.
- Separate model training, independent evaluation, approval, deployment, smoke testing,
  and promotion when the selected profile includes those stages.

## Project documentation

Every project includes `README.md` plus `docs/architecture.md`, `docs/configuration.md`,
and `docs/testing.md`. Add `docs/mlflow.md` for MLflow profiles. Add
`docs/databricks.md`, `docs/operations.md`, `docs/release-checklist.md`, and
`docs/rollback.md` for production deployment.

Document where each component executes, which system is authoritative, what can run
locally, and which validations require credentials. Do not generate Databricks resources
for projects that selected a smaller profile.

