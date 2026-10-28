---
title: Grafana dashboards and alerts as code
nav_order: 13
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-10-28
review_in: 6 months
---

# Grafana dashboards and alerts as code

# Table of Contents
- [What this is](#what-this-is)
- [Quick start](#quick-start)
- [Folder](#folder)
- [Dashboards](#dashboards)
  - [Exporting a dashboard from Grafana](#exporting-a-dashboard-from-grafana)
  - [Dashboard uids and URLs](#dashboard-uids-and-urls)
  - [Taking over a dashboard made in the Grafana UI](#taking-over-a-dashboard-made-in-the-grafana-ui)
  - [Using the same dashboard in several environments](#using-the-same-dashboard-in-several-environments)
  - [Other dashboard sources](#other-dashboard-sources)
- [Alert rules](#alert-rules)
  - [Taking over an alert rule made in the Grafana UI](#taking-over-an-alert-rule-made-in-the-grafana-ui)
- [Deploying via ArgoCD](#deploying-via-argocd)
- [Changing and deleting](#changing-and-deleting)
- [Using the chart in your own Helm chart](#using-the-chart-in-your-own-helm-chart)
- [Troubleshooting](#troubleshooting)
- [Moving from idp-grafana-alarm](#moving-from-idp-grafana-alarm)

# What this is

The `idp-grafana-customer-resources` Helm chart lets you keep your Grafana dashboards and alert rules in your apps repository, next to your applications. ArgoCD deploys them, and Grafana is updated automatically.

One release of the chart creates:

- a **folder** in Grafana
- your **dashboards**, in that folder
- your **alert rules**, in that folder

The recommended workflow is the same for dashboards and alerts: **build and test in the Grafana UI first**, then export and paste the result into `values.yaml`.

> **Note:** Once a dashboard or alert rule is managed by the chart, the chart is the source of truth. Changes you make in the Grafana UI are overwritten within about 10 minutes. To change something, edit it in the UI, export it again and commit the new version.

# Quick start

In your apps repository, create a directory under `apps/<namespace>/`, for example `apps/my-namespace/my-team-grafana/`, with two files.

**`application.yaml`:**

```yaml
apiVersion: v2
name: my-team-grafana
description: Grafana dashboards and alerts for my team
version: 0.1.0
helm:
  chart: helm/idp-grafana-customer-resources
  chartVersion: "1.1.0"  # example version, see the latest at https://github.com/jppol-idp/helm-idp/releases
```

**`values.yaml`:**

```yaml
folder: "My Team"

dashboards:
  - name: api-overview
    json: |
      {
        "title": "API overview",
        "panels": [ ... ]
      }
```

Commit and push. ArgoCD deploys the dashboard to the folder "My Team" in your Grafana.

# Folder

By default the chart creates a folder for its dashboards and alert rules.

| Value | Effect |
|-------|--------|
| `folder: "My Team"` | Creates a folder with this title |
| No `folder` | Creates a folder named after the directory in your apps repository, for example `my-team-grafana` |
| `folderUID: "<uid>"` | Creates no folder and uses an existing one. Find the uid in the folder's URL in Grafana: `/dashboards/f/<uid>/` |

Set either `folder` or `folderUID`, not both.

> **Note:** An alert rule group cannot move to another folder. If you switch an existing release with alert rules between `folder` and `folderUID`, ArgoCD fails to sync. Remove the alert rules, sync, and add them again.

# Dashboards

Each entry in `dashboards` needs a `name` and the dashboard itself. The `name` is used in Kubernetes resource names, so it may only contain lowercase letters, digits and hyphens, for example `api-overview`.

## Exporting a dashboard from Grafana

1. Open the dashboard in Grafana.
2. Click **Export** in the top right and choose **Export as JSON**. If Grafana asks for a format, choose the classic JSON model.
3. Leave **Export the dashboard to use in another instance** off.
4. Click **Copy to clipboard**.
5. Paste the JSON under `json: |` in your `values.yaml`, indented below the `json` key:

```yaml
dashboards:
  - name: api-overview
    json: |
      {
        "uid": "abc123",
        "title": "API overview",
        "panels": [ ... ]
      }
```

Large dashboards are fine. If the JSON is not valid, ArgoCD shows an error when it renders the chart.

## Dashboard uids and URLs

Every dashboard in Grafana has a uid, which is part of its URL: `https://grafana.<cluster>.idp.jppol.dk/d/<uid>/...`.

Several namespaces share the same Grafana, for example a dev and a test namespace on the same cluster. If two namespaces deployed a dashboard with the same uid, they would overwrite each other without any error. To prevent that, **the chart sets the uid itself** to `<namespace>-<folder name>-<name>` and ignores the uid in your exported JSON. Long uids are shortened to Grafana's limit of 40 characters.

This means that the URL of a dashboard deployed with the chart differs from the one you exported.

## Taking over a dashboard made in the Grafana UI

If you already have a dashboard made in the Grafana UI and want to keep its URL and bookmarks, set `uid` to the uid from the export:

```yaml
dashboards:
  - name: api-overview
    uid: abc123          # keeps the existing dashboard and its URL
    json: |
      {
        "uid": "abc123",
        "title": "API overview",
        ...
      }
```

The chart then takes over the existing dashboard instead of creating a new one. It is moved to the chart's folder.

Only do this for a dashboard that exists in one namespace. If you deploy the same `uid` in two namespaces on the same cluster, the dashboards overwrite each other.

Without `uid`, the chart creates a new dashboard next to the old one. Delete the old one in the Grafana UI when you have checked the new one.

## Using the same dashboard in several environments

You can copy the same `values.yaml` to your dev, test and prod namespaces. Each namespace gets its own dashboard, because the chart puts the namespace in the uid.

Check which data sources your dashboard uses:

- **Prometheus** and **Loki** have the same uid on every cluster, so dashboards using them work everywhere.
- **Mimir** and **Tempo** have a different uid on each cluster. A dashboard exported from dev that uses them does not work in prod as it is.

To make such a dashboard work everywhere, add a data source variable to the dashboard (**Settings > Variables > New variable**, type **Data source**) and use that variable in the panels before you export.

## Other dashboard sources

Instead of `json`, a dashboard can come from one of these sources. Use exactly one per dashboard.

```yaml
dashboards:
  # A dashboard from grafana.com, by id and revision
  - name: node-exporter
    grafanaCom:
      id: 1860
      revision: 37
    datasources:
      - inputName: DS_PROMETHEUS
        datasourceName: Prometheus

  # A dashboard JSON file from a URL that Grafana can reach without login
  - name: remote-dashboard
    url: https://example.com/dashboard.json

  # A dashboard JSON stored in a ConfigMap in the same namespace
  - name: from-configmap
    configMapRef:
      name: my-dashboards
      key: api-overview.json
```

Dashboards from grafana.com and many shared JSON files ask for their data source when they are imported, using names like `DS_PROMETHEUS`. Map those names to a data source in your Grafana with `datasources`, as in the example above. The `datasourceName` is the name of the data source as shown in Grafana, for example `Prometheus` or `Loki`.

# Alert rules

Alert rules use the same values as `idp-grafana-alarm`: `interval`, `rules` and `groups`. Follow [Working with Alerting](/how-to/alerting.html#step-1-create-and-test-in-the-gui) to create and test a rule in the Grafana UI and export it as YAML, then paste the rules into the same `values.yaml` as your dashboards.

Set `contactPointRef` to the name of your team's Slack contact point, as shown under **Alerting > Contact points** in Grafana.

- If you use [IDP-managed alerts](/how-to/idp-managed-alerts.html), use the same value as `contactPointRef` there, so your own alerts and the IDP-managed ones post to the same channel in the same format.
- If you already route alerts to a contact point, for example with `notification_settings.receiver` in `idp-grafana-alarm`, use that name.
- If you don't have a contact point yet, see [Requesting a Slack Contact Point](/how-to/alerting.html#requesting-a-slack-contact-point).

```yaml
folder: "My Team"
contactPointRef: "Slack - MyTeam dev"   # your team's contact point

interval: 1m
rules:
  - uid: high-error-rate
    title: High Error Rate
    condition: C
    data:
      # ... query and condition from the export
    for: 5m
    annotations:
      summary: "High error rate detected"
    labels:
      severity: warning
```

Every rule is sent to `contactPointRef`. You can leave out `notification_settings` from the export. If a rule should go to another channel, keep `notification_settings.receiver` on that rule, and it takes precedence. If a rule has no receiver and `contactPointRef` is not set, ArgoCD shows an error, so an alert never ends up somewhere you don't see it.

`rules` creates one alert rule group named after the directory in your apps repository. Use `groups` for several groups with their own names and intervals, as described in [Using Multiple Alert Groups](/how-to/alerting.html#using-multiple-alert-groups).

[How Your Alert Looks in Slack](/how-to/alerting.html#how-your-alert-looks-in-slack) describes the annotations and labels that shape the Slack message.

Unlike dashboards, the chart **keeps the `uid` of each alert rule as you write it**. Alert rule uids must be unique across all namespaces on the cluster. If you copy the same rules to dev and test on the same cluster, give each copy its own uid, for example by adding the environment: `high-error-rate-dev`.

## Taking over an alert rule made in the Grafana UI

Grafana only lets the chart take over an existing rule when the rule stays in the same folder and the same group. Use `folderUID` with the uid of the rule's folder, and `groups` with the group name from the export:

```yaml
folderUID: "my-team-folder-uid"   # the folder the rule is in today

groups:
  - name: my-alert-group          # groups[].name from the export
    interval: 1m
    rules:
      - uid: abc123xyz            # unchanged from the export
        # ... the rest of the rule from the export
```

The rule is updated in place and keeps its uid.

If you want the rule in the chart's own folder instead, delete the rule in the Grafana UI first, then deploy it with the chart. Otherwise Grafana rejects it, see [Troubleshooting](#troubleshooting).

# Deploying via ArgoCD

1. Create the directory with `application.yaml` and `values.yaml` as shown in [Quick start](#quick-start).
2. Commit and push to `main`. ArgoCD creates the folder, the dashboards and the alert rules.
3. Open Grafana and find your folder under **Dashboards**.

You can keep dashboards and alert rules in the same release, or split them into several directories, for example one per service. Each release gets its own folder unless you point them to the same one with `folderUID`.

# Changing and deleting

- **Change a dashboard:** edit it in the Grafana UI, export it again and replace the JSON in `values.yaml`. Changes made only in the UI are overwritten within about 10 minutes.
- **Rename the folder:** change `folder`. Dashboards and alert rules stay in it.
- **Delete a dashboard or alert rule:** remove it from `values.yaml` and push. ArgoCD removes it from Grafana.
- **Delete everything:** remove the directory from your apps repository. ArgoCD removes the folder, dashboards and alert rules.

# Using the chart in your own Helm chart

If your team builds its own Helm chart, you can add `idp-grafana-customer-resources` as a dependency. It can be added more than once with different aliases, for example one per service:

```yaml
# Chart.yaml
dependencies:
  - name: idp-grafana-customer-resources
    alias: api-grafana
    version: "1.1.0"  # example version, see the latest at https://github.com/jppol-idp/helm-idp/releases
    repository: oci://354918371398.dkr.ecr.eu-west-1.amazonaws.com/helm
  - name: idp-grafana-customer-resources
    alias: worker-grafana
    version: "1.1.0"
    repository: oci://354918371398.dkr.ecr.eu-west-1.amazonaws.com/helm
```

```yaml
# values.yaml
api-grafana:
  folder: "My Project - API"
  dashboards:
    - name: overview
      configMapRef:
        name: my-project-dashboards
        key: api-overview.json

worker-grafana:
  folder: "My Project - Worker"
```

Each alias gets its own folder and resource names, so the two do not collide.

To keep dashboard JSON as files in your chart rather than in values, create a ConfigMap in your chart and point to it with `configMapRef`:

```yaml
# templates/dashboards-configmap.yaml in your chart
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-project-dashboards
data:
  api-overview.json: {{ .Files.Get "dashboards/api-overview.json" | quote }}
```

A ConfigMap can hold at most 1 MiB in total.

# Troubleshooting

**The dashboard or alert rule does not show up in Grafana.** ArgoCD can show the app as Healthy even when Grafana rejected a resource. Open the resource in ArgoCD and check `status.conditions` in the live manifest. Common messages:

| Message | Cause | Fix |
|---------|-------|-----|
| `PostAlertRule (status 409)` | An alert rule with the same `uid` already exists, either from another namespace on the cluster or made in the Grafana UI | Give the rule a unique `uid`, or see [Taking over an alert rule made in the Grafana UI](#taking-over-an-alert-rule-made-in-the-grafana-ui) |
| `InvalidModelResolution` ... `configmaps "..." not found` | The ConfigMap in `configMapRef` does not exist in the namespace | Create the ConfigMap or fix its name |
| `spec.folderUID is immutable` or `spec.folderRef is immutable` | An alert rule group was moved to another folder | See the note under [Folder](#folder) |

**The dashboard moved to another folder or changed by itself.** Another namespace deploys a dashboard with the same `uid`. Remove `uid` from one of them so the chart sets a unique one.

**My change in the Grafana UI disappeared.** The chart overwrote it. Export the dashboard and commit the change, see [Changing and deleting](#changing-and-deleting).

If you are stuck, write to the IDP team in your team's onboarding channel on Slack.

# Moving from idp-grafana-alarm

`idp-grafana-customer-resources` replaces `idp-grafana-alarm` for new setups. Existing `idp-grafana-alarm` releases keep working, and there is no need to migrate them.

The alert values are the same, with two differences:

- `folderRef` is replaced by `folderUID`, which points to a folder by its uid in Grafana.
- `contactPointRef` sets the Slack contact point for all rules, so `notification_settings` is no longer needed on each rule. A rule without a receiver is an error.
