# MLflow profile

- Use an explicit tracking URI and experiment name per environment.
- Log parameters, primary and diagnostic metrics, dataset identity, tags, model signature,
  input example, and useful evaluation artifacts.
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

