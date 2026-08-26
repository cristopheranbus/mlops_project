# Testing standard

## Test layers

### Unit

Test transformations, configuration resolution, metrics, gates, payload construction,
and promotion rules without network, credentials, Databricks, or shared state. Use small
fixtures, `tmp_path`, controlled random seeds, and deterministic assertions.

### Contract

Test data schemas, target rules, configuration files, model signatures, inference inputs
and outputs, required artifacts, and deployment manifests. Contract tests protect the
boundaries between training, evaluation, and serving.

### Local integration

For applicable profiles, exercise a small end-to-end path with temporary storage and
MLflow backed by a local file or SQLite store. Verify model logging/loading, evaluation,
artifacts, and registry behavior without production services.

### External integration

Mark tests that require authorized infrastructure as `external`; do not run them by
default. Mark local multi-component tests as `integration`. Report missing credentials as
not run. Never mock an external check and then describe production as validated.

### Smoke

When deployment exists, invoke the exact approved version, validate the response schema
and semantics, and block promotion on failure.

## Coverage and test quality

Default to 85% coverage, configurable by the user. Prioritize high coverage for
configuration, contracts, gates, deployment decisions, and rollback logic. Do not add
tests that merely repeat implementation details or inflate the percentage without
checking behavior.
