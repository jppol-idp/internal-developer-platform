---
title: Configuring your app with environment variables
nav_order: 7
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-08-28
review_in: 6 months
---

# Configuring your app with environment variables

We recommend passing configuration to your app as environment variables, defined in the `env` block of your `values.yaml`.

## Table of contents

- [Plain values](#plain-values)
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
- [Sharing configuration between apps](./shared-configuration): when the same configuration file is read by more than one of your apps.
- [IDE autocomplete and validation for values.yaml](./values-yaml-ide-schema) — set up inline validation so your editor flags invalid `env` and `configMaps` entries as you type.
- The full set of `env` and `configMaps` options is documented in the [idp-advanced schema reference](https://public.docs.idp.jppol.dk/schemas/idp-advanced/latest.json).

If you're unsure which approach fits your case, ask on Slack — the IDP team is happy to help.
