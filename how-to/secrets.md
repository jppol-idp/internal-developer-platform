---
title: Working with Secrets
nav_order: 37
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-06-29
review_in: 6 months
---
# Working with Secrets

We use GitHub Actions and External Secrets to sync secrets from AWS Secrets Manager into the Kubernetes cluster.

Within each namespace in your IDP apps repository, you'll find a context-specific README.

Example
`https://github.com/jppol-idp/apps-<team>/blob/main/apps/<team>-dev/secrets.md`

## Adding `property` to an existing secret

In the `idp-advanced` chart, each entry under `external_secrets` becomes an ExternalSecret in the cluster. The entry's `property` field decides how that ExternalSecret is named:

| Entry | ExternalSecret name | Kubernetes Secret name |
|-------|---------------------|------------------------|
| without `property` | `<app>-env-<secretsmanager_name>` | `<app>-env-<env_name>` |
| with `property` | `<app>-env-<env_name>` | `<app>-env-<env_name>` |

If you add `property` to an entry that already exists, and its `env_name` and `secretsmanager_name` differ, the chart creates a new ExternalSecret under a new name. The secret in AWS Secrets Manager does not change, and neither does the Kubernetes Secret, so both ExternalSecrets point at the same Kubernetes Secret.

Example:

```yaml
external_secrets:
  - env_name: AZURE_OPENAI_API_KEY
    secretsmanager_name: echo-azure-openai-api-key
    property: AZURE_OPENAI_API_KEY   # added
```

The ExternalSecret `<app>-env-echo-azure-openai-api-key` is replaced by `<app>-env-azure-openai-api-key`.

The sync in ArgoCD then fails with:

```
target is owned by another ExternalSecret
```

ArgoCD only deletes the old ExternalSecret after a sync has succeeded, and the sync cannot succeed while the old one is still there. Delete the old ExternalSecret yourself:

1. Open the application in ArgoCD and click **Sync**.
2. Clear all resources except the old ExternalSecret.
3. Tick **Prune** and click **Synchronize**.

The Kubernetes Secret is then recreated by the new ExternalSecret within seconds. Pods that are already running keep their environment variables. ArgoCD can sync the rest of the application normally afterwards.

If you only have read access in ArgoCD, ask IDP in your team's onboarding channel on Slack.

Repeat this in each environment where you add `property`.
