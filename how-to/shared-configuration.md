---
title: Sharing configuration between apps
nav_order: 24
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-08-28
review_in: 6 months
---

# Sharing configuration between apps

When more than one of your apps reads the same configuration file, you do not have to repeat it in every `values.yaml`. Deploy the file once with the `idp-configmap` chart, as an app of its own, and mount it from each of the apps that need it.

This is worth doing when the file is genuinely shared. If only one app reads it, keep it in that app's own `configMaps` block, described in [Configuring your app with environment variables](./app-configuration).

## Table of contents

- [Deploying the shared configuration](#deploying-the-shared-configuration)
- [Reading it from your apps](#reading-it-from-your-apps)
- [What happens when the configuration changes](#what-happens-when-the-configuration-changes)
- [Where to go next](#where-to-go-next)

## Deploying the shared configuration

Give the shared configuration its own folder alongside your other apps:

```yaml
# application.yaml
apiVersion: v2
name: myapp-shared-config
description: Configuration shared by the myapp services
version: 0.1.0
helm:
  chart: helm/idp-configmap
  chartVersion: "1.0.0"  # check latest at github.com/jppol-idp/helm-idp/releases
```

```yaml
# values.yaml
# yaml-language-server: $schema=https://public.docs.idp.jppol.dk/schemas/idp-configmap/latest.json
configMaps:
  - name: myapp-shared-config
    data:
      settings.json: |
        {
          "sources": []
        }
```

The ConfigMap is named exactly what you write in `name`, so your other apps can refer to it directly.

A pod can only mount a ConfigMap from its own namespace, so the folder has to sit next to the apps that read it. If the same configuration is used in more than one environment, each environment needs its own copy.

## Reading it from your apps

In each app that reads the file, mount it and ask for a restart when it changes:

```yaml
volumes:
  - name: config-volume
    configMap:
      name: myapp-shared-config

volumeMounts:
  - name: config-volume
    mountPath: /app/config

deploymentAnnotations:
  reloader.stakater.com/auto: "true"
```

`deploymentAnnotations` requires idp-advanced 3.9.0 or newer.

## What happens when the configuration changes

The annotation is the part that does the work. Without it the file is still replaced inside the running pods, but around a minute later and without your app being told, so your app keeps using whatever it read at startup. With it, the pods restart whenever the shared ConfigMap changes.

Two things worth knowing:

- Adding the annotation triggers one rolling restart by itself, the first time you apply it.
- Until the shared ConfigMap exists, pods that mount it wait in `ContainerCreating`. They start on their own as soon as it appears, so the order the apps are created in does not matter.

## Where to go next

- [Configuring your app with environment variables](./app-configuration): the ordinary case, where configuration belongs to a single app.
- [IDE autocomplete and validation for values.yaml](./values-yaml-ide-schema): what the `yaml-language-server` line above does, and how to set it up in your editor.
- The full set of `idp-configmap` options is documented in the [idp-configmap schema reference](https://public.docs.idp.jppol.dk/schemas/idp-configmap/latest.json).

If you're unsure which approach fits your case, ask on Slack. The IDP team is happy to help.
