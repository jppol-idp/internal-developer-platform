---
title: Configuring your app with environment variables
nav_order: 6
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-07-28
review_in: 6 months
---

# Configuring your app with environment variables

We recommend passing configuration to your app as environment variables, defined in the `env` block of your `values.yaml`.

## Table of contents

- [Plain values](#plain-values)
- [Values from Kubernetes secrets or pod fields](#values-from-kubernetes-secrets-or-pod-fields)
- [Larger configuration blocks](#larger-configuration-blocks)
- [Where to go next](#where-to-go-next)

## Plain values

The simplest form is a literal `name`/`value` pair:

```yaml
env:
  - name: ASPNETCORE_ENVIRONMENT
    value: "Staging"
  - name: ASPNETCORE_HTTP_PORTS
    value: "8080"
  - name: MyDependencyService__apiBasePath
    value: "http://mydependency-service.my-namespace.svc.cluster.local:8080"
```

Nested configuration keys (as used by ASP.NET Core's `IConfiguration`, for example) are expressed with a double underscore, as in `MyDependencyService__apiBasePath` above.

## Values from Kubernetes secrets or pod fields

Instead of a literal `value`, an entry can use `valueFrom` to pull the value from somewhere else at pod start:

```yaml
env:
  - name: DATABASE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: my-db-secret
        key: password
  - name: POD_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
```

- `secretKeyRef` reads a key from an existing Kubernetes Secret. If the secret should come from AWS Secrets Manager, see [Working with Secrets](./secrets) for how those secrets get synced into the cluster first.
- `fieldRef` reads a field from the pod's own metadata (name, namespace, IP, etc.) — useful for values that should reflect the running pod rather than being hardcoded.

## Larger configuration blocks

For configuration that doesn't fit naturally as individual environment variables — a whole `appsettings.json` overlay, a logging config file, and the like — use `configMaps` instead and mount the result as a file:

```yaml
configMaps:
  - name: myapp-config
    data:
      appsettings.override.json: |
        {
          "Logging": {
            "LogLevel": {
              "Default": "Information"
            }
          }
        }

volumes:
  - name: config-volume
    configMap:
      name: myapp-config

volumeMounts:
  - name: config-volume
    mountPath: /app/config
```

## Where to go next

- [Working with Secrets](./secrets) — for anything that shouldn't be a plain-text value, such as passwords or API keys.
- [IDE autocomplete and validation for values.yaml](./values-yaml-ide-schema) — set up inline validation so your editor flags invalid `env` and `configMaps` entries as you type.
- The full set of `env` and `configMaps` options is documented in the [idp-advanced schema reference](https://public.docs.idp.jppol.dk/schemas/idp-advanced/latest.json).

If you're unsure which approach fits your case, ask on Slack — the IDP team is happy to help.
