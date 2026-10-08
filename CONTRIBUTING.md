# Contributing

Thank you for helping improve observability-driven-cicd.

## Ways to contribute

- Fix documentation.
- Add or improve health gates.
- Add PromQL checks.
- Improve Kubernetes manifests.
- Add synthetic transactions.
- Add observability integrations.
- Add safe agent tools.
- Add cloud-specific examples.
- Improve tests and developer experience.

## Development workflow

1. Fork the repository.
2. Create a branch from `main`.
3. Make a focused change.
4. Add or update tests and documentation.
5. Run the local validation commands.
6. Open a pull request using the repository template.

Suggested branch names:

```text
feature/<short-name>
fix/<short-name>
docs/<short-name>
```

## Principles

Changes should preserve these guarantees:

- The core demo remains runnable without a paid service.
- AI integrations remain optional.
- Agents do not receive unrestricted production write access.
- Health gates should be deterministic where possible.
- Observability backends should remain replaceable.
- Secrets must never be committed.

## Pull requests

A good pull request should explain:

- What problem it solves.
- How it was tested.
- Whether it changes deployment behavior.
- Whether it changes security or agent permissions.
- Any new dependencies.

Small pull requests are preferred.

## Good first issues

Good first contributions include:

- New cluster-health checks.
- New PromQL gates.
- Documentation improvements.
- Additional synthetic checks.
- Test coverage.
- Grafana dashboard panels.

## Developer Certificate of Origin

By contributing, you certify that you have the right to submit the work under
the project's Apache-2.0 license.
