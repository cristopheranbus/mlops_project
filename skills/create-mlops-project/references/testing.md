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

For Mutmut 3, use the supported `source_paths`, `also_copy`, `pytest_add_cli_args`, and
`pytest_add_cli_args_test_selection` fields. Do not generate the obsolete `paths_to_mutate`,
`tests_dir`, or `runner` settings. Align the staged source path with the module identity used
by pytest; when the canonical source is outside a conventional `src` layout, either stage it
ephemerally under `src/<package>` or choose another explicit layout whose import identity is
proven by a test.

The mutation job must:

1. run on Linux when the selected tool has no native Windows support;
2. omit `continue-on-error` around mutation execution and result collection;
3. assert that the imported module lives inside the current mutant workspace;
4. attempt to export structured counts such as `mutmut-cicd-stats.json` even on failure;
5. fail when that evidence file is absent or the selected suite is empty;
6. publish the evidence as a CI artifact and summarize the counts;
7. record the source revision, scope, formula, and first accepted baseline in project docs.

A score is not evidence when tests ran against the original module, no mutants were
collected, or statistics could not be exported. Keep the score informational until
equivalent mutants have been classified; operational failures are blocking from the first
run. Generated `docs/testing.md` must explain how to reproduce the analysis, interpret each
status, investigate survivors, and distinguish a low score from a broken run.

Use the [official Mutmut configuration reference](https://github.com/boxed/mutmut#configuration)
for supported field names and update semantics.

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
