---
name: create-mlops-project
description: Create a new production-oriented Python ML or MLOps repository from a problem contract, using a local, MLflow, or Databricks profile with tests, CI, validation, and operational documentation. Use when bootstrapping a new ML repository; do not use for ordinary Python packages or modifications to an existing repository.
---

# Create MLOps Project

Create a new, independent repository adapted to the user's ML problem. Do not copy an
existing project or treat a previous repository as a template.

## Gather the contract

Confirm or safely infer these inputs before generating files: project name, importable
package name, empty destination, problem type, data sources, target, framework, primary
metric, acceptance thresholds, Python version, coverage target, and one profile:

- `python-ml`: local Python ML project without MLflow or Databricks.
- `mlflow-local`: local project with MLflow tracking, evaluation, artifacts, and optional
  registry behavior.
- `databricks-mlops`: local development plus MLflow, Unity Catalog, Databricks Asset
  Bundles, Jobs, approval gates, Model Serving, and smoke tests.

Ask only for missing choices that materially change the result. Default to Python 3.12,
`uv`, 85% coverage, and the smallest profile that satisfies the request.

## Create safely

1. Resolve the destination to an absolute path.
2. Create a missing destination, but do not overwrite, delete, or repurpose a non-empty
   destination without explicit authorization.
3. Read [architecture](references/architecture.md), [quality](references/quality.md), and
   [testing](references/testing.md).
4. For `mlflow-local`, also read [MLflow](references/mlflow.md).
5. For `databricks-mlops`, read both [MLflow](references/mlflow.md) and
   [Databricks](references/databricks.md).
6. Generate the project from the selected standards and the user's domain contract. Keep
   notebooks thin and place reusable logic in the Python package.
7. Record the chosen profile in `.mlops-profile` so validation is reproducible.
8. Run `scripts/validate_project.py <destination> --profile <profile>` from this skill.
9. Run every applicable local quality command, fix failures, and repeat validation.

## Completion contract

Return created components, assumptions, the selected profile, commands run, successful
checks, failed checks, and external checks not run. Never report Databricks, registry,
serving, or other external validation as successful without executing it against
authorized infrastructure. Do not expose secrets or initialize a remote repository unless
the user separately asks.
