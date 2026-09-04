# Distribution and generation modes

Use one canonical skill contract across every mode. Never maintain independent copies of its
rules by hand.

## Personal skill

Install `skills/create-mlops-project/` in the user's personal skills directory when one person
needs the generator across multiple repositories. Invoke `$create-mlops-project` from a parent
directory and generate into a missing or empty destination.

## Repository-local skill

Place the skill at `.agents/skills/create-mlops-project/` when a team must version the same
workflow with its code. Do not place it in an otherwise empty destination before generating;
generate first and use the CLI `--embed-skill` option, or copy it afterward with explicit
authorization. The embedded copy is tooling, not part of the generated application's package.

## Plugin

The repository root is the plugin boundary. `.codex-plugin/plugin.json` points to `./skills/`.
Keep the plugin, Python package, and changelog versions aligned for releases.

## Deterministic CLI

After installing this Python package, use:

```text
create-mlops-project DESTINATION --name PROJECT_NAME --profile python-ml
```

Available profiles are `python-ml`, `mlflow-local`, and `databricks-mlops`. Use `--package`
to override the normalized import name, `--embed-skill` to vendor the skill, and `--skip-lock`
only in an offline bootstrap where the user understands that `uv lock` must run before
`uv sync --locked`.

The CLI creates a generic contract-valid baseline. Adaptive skill generation remains the
correct mode when the output must implement a particular dataset, target, metric, threshold,
or serving contract. In either mode, run `validate_project.py` and the generated quality gates.

## Safety and publication

Every mode refuses a non-empty destination. Initializing Git, creating a remote, changing
GitHub settings, enabling external infrastructure, and using credentials remain separate,
explicitly authorized operations.
