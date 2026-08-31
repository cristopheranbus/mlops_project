# Testing standard

Build tests as executable evidence for the generated project's public contracts. A high
test count is not a goal by itself: every test must own a meaningful behavior, boundary,
failure mode, or operational invariant.

## Pytest organization

Use `tests/conftest.py` for shared collection policy and fixtures with repository-wide
meaning. Use `pytest_generate_tests` only for dynamic, cross-cutting inventories such as
profiles, contract cases, notebook formats, or runtime-selected cases. Give every dynamic
case a stable, descriptive ID and allow `--profile` to narrow the matrix. Keep small,
local input tables next to their tests with `@pytest.mark.parametrize`.

Do not create uncontrolled Cartesian products. Represent compatible combinations as
typed case objects and parametrize those complete cases. Collection must not contact the
network, read credentials, or depend on unordered filesystem results.

Recommended support layout:

```text
tests/
├── conftest.py
├── cases/
├── factories/
├── unit/
├── contract/
├── integration/
├── security/
├── external/
└── e2e/
```

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

### Security and robustness

Test path traversal, symlinks that escape the project, malformed declarative files,
unexpected encodings, nested secret-shaped keys, untrusted workflow triggers, action
pinning, and minimum permissions. Security tests must use synthetic values that cannot be
mistaken for real credentials.

### Property-based

Use property-based testing for broad invariants such as canonical hashes, configuration
merge laws, schema rejection, and path containment. Bound generated inputs, disable a
deadline only when filesystem timing is genuinely variable, and preserve the failing
example emitted by the framework when it reveals a regression.

### Mutation

Use scheduled mutation testing for high-risk pure logic such as configuration, validation,
promotion gates, and monitoring thresholds. Introduce the mutation score as informational,
then make an agreed threshold blocking after surviving mutants have been reviewed. Never
replace behavioral assertions with exclusions merely to raise the score.

## Coverage and test quality

Default to 90% branch coverage, configurable upward by the user. Prioritize high coverage for
configuration, contracts, gates, deployment decisions, and rollback logic. Do not add
tests that merely repeat implementation details or inflate the percentage without
checking behavior.

Every project configures strict markers, a finite default timeout, JUnit output in CI,
and a clear opt-in for `external` tests. Reruns must not hide flaky behavior. An `xfail`
needs a reason, an issue, and a removal condition.

## Required evidence per rule

For each generated-project rule, keep traceability between:

1. normative requirement;
2. implementation;
3. positive test;
4. negative test;
5. stable diagnostic code;
6. beginner-facing correction instructions;
7. CI check that executes the evidence.
