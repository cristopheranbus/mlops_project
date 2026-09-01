# MLflow security boundary

Apply this reference to every `mlflow-local` and `databricks-mlops` project.

## Generated-project policy

- Use MLflow for Tracking, experiments, runs, artifacts, evaluation, and explicitly
  approved registry operations.
- Do not generate or enable MLflow AI Gateway, gateway secrets, gateway proxy routes, or
  an `auth_config.api_base`. The project validator reports these as `mlflow-security`.
- Generate `docs/mlflow-security.md`. Explain the difference between Tracking and AI
  Gateway, the default-disabled boundary, the validation error, dependency review,
  access control, outbound-network controls, incident response, and the process for a
  reviewed future exception.
- Link the generated guide to the
  [official MLflow security documentation](https://mlflow.org/docs/latest/self-hosting/security/),
  the [official authentication documentation](https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/),
  and [GHSA-h7x2-h6g9-p789](https://github.com/advisories/GHSA-h7x2-h6g9-p789).
- Keep MLflow bounded in `pyproject.toml`, resolve it into `uv.lock`, audit the resolved
  graph, and review the upstream changelog and advisories before upgrading. A version
  range alone is not proof that the gateway destination-validation issue is fixed.
- Never expose a self-hosted MLflow server directly to an untrusted network. Put
  authentication, authorization, TLS, request limits, logs, and network policy around it.
- Never place credentials in MLflow params, tags, artifacts, gateway configuration, Git,
  notebook outputs, or CI logs.

## Future AI Gateway enablement

Do not bypass or silence `mlflow-security`. Changing the boundary requires a reviewed
contract update with regression tests and operational evidence that all of these controls
exist:

1. a vetted upstream fix validates the scheme, hostname, resolved addresses, redirects,
   and every outbound connection destination;
2. secret creation and mutation require an explicit administrative permission;
3. outbound traffic has an allowlist and blocks loopback, private, link-local, reserved,
   multicast, unspecified, and cloud metadata destinations;
4. DNS rebinding and redirects cannot escape the allowlist;
5. secrets are stored in an approved secret manager and responses are size-limited and
   safely logged;
6. negative tests cover IPv4, IPv6, alternative numeric notation, redirects, DNS changes,
   userinfo, and metadata endpoints;
7. a security owner records the reviewed MLflow version, deployment controls, rollback,
   and monitoring evidence.

Project-level URL parsing is not a substitute for fixing the server-side request path.
If AI Gateway is a requirement, handle it as a separate security-reviewed change rather
than part of the default scaffold.
