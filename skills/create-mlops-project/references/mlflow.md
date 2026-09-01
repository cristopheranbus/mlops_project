# MLflow profile

- Use an explicit tracking URI and experiment name per environment.
- Define `start_experiment_run` only in
  `src/<package_name>/tracking/mlflow.py`. It validates configuration before opening a
  run, calls `mlflow.start_run` as a context manager, enables `mlflow.autolog` inside that
  context before yielding control, and logs the resolved configuration evidence.
- Do not call `mlflow.start_run` outside the tracking adapter. Workflows, notebooks, and
  tuning code must use `start_experiment_run`; nested trials pass `nested=True`.
- Log parameters, primary and diagnostic metrics, dataset identity, tags, model signature,
  input example, and useful evaluation artifacts.
- Add `config.version`, `config.environment`, and `config.hash` tags and a redacted
  `resolved_config.yaml` artifact to every run.
- Keep training separate from independent evaluation and promotion decisions.
- Make local tracking fully functional with temporary or SQLite-backed storage.
- Register models only when the workflow benefits from versioned lifecycle management.
- When promotion exists, use exact versions and explicit `Challenger` and `Champion`
  aliases rather than mutable stage assumptions.
- Evaluate configured thresholds and allowed regression against the current Champion.
- Preserve auditable evidence for acceptance, rejection, approval, smoke testing, and
  promotion.
- Tests must use isolated temporary stores and must not depend on a developer's MLflow
  state.
- Apply the separate [MLflow security boundary](mlflow-security.md). Generated projects
  use Tracking but do not enable AI Gateway, gateway secrets, proxy routes, or
  `auth_config.api_base`.
