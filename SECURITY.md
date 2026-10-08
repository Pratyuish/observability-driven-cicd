# Security Policy

## Reporting a vulnerability

Please **do not open a public GitHub issue** for a suspected vulnerability.

Until a dedicated private reporting channel is configured, use GitHub's
private vulnerability reporting feature when available for this repository.

A useful report includes:

- affected component and version/commit,
- reproduction steps,
- expected and actual behavior,
- security impact,
- suggested mitigation if known.

## Security boundaries

This project intentionally treats CI/CD and agentic automation as privileged
infrastructure.

Contributors must not:

- commit credentials, tokens, kubeconfigs, or private keys,
- embed long-lived cloud credentials in workflows,
- grant AI agents unrestricted cluster-admin access,
- bypass approval gates for production-changing remediation,
- log secrets into workflow artifacts.

Prefer short-lived workload identity/OIDC and least-privilege permissions.

## Supported versions

During pre-1.0 development, security fixes target the latest `main` branch.
