---
title: Working with Scheduled Jobs
nav_order: 31
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-09-22
review_in: 6 months
---
# Working with Scheduled Jobs

## Introduction

This guide shows how to run a scheduled job using the [argo-cronworkflow-job chart](https://github.com/jppol-idp/helm-idp/tree/main/charts/argo-cronworkflow-job). It is a thin wrapper around Argo Workflows' `CronWorkflow` resource - the same idea as a Kubernetes `CronJob`, but built on [Argo Workflows](https://argo-workflows.readthedocs.io/en/latest/cron-workflows/), which is what runs scheduled work on the platform.

This covers running a single container on a schedule, with environment variables and secrets - what most scheduled jobs need.

---

## Table of contents

{: .no_toc }

- TOC
{:toc}

---

## Quick start: a simple cron job

In your apps repository, add a folder for the job under the relevant namespace folder:

```
apps/team-dev/my-cron-job/
├── application.yaml
└── values.yaml
```

`application.yaml` tells ArgoCD which chart to deploy:

```yaml
apiVersion: v2
name: my-cron-job
description: my-cron-job
version: 0.1.0
helm:
  chart: helm/argo-cronworkflow-job
  chartVersion: "1.2.5" # Check https://github.com/jppol-idp/helm-idp/tree/main/charts/argo-cronworkflow-job for the latest version
```

`values.yaml` defines the schedule and the container that runs on it - this is the minimum needed for a working job:

```yaml
metadata:
  jobName: "my-cron-job"

spec:
  schedules:
    - "0 23 * * *"
  workflowSpec:
    entrypoint: my-cron-job
    templates:
      - name: my-cron-job
        container:
          image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/my-team/my-cron-job:latest
          command: ["node"]
          args: ["runJob.js"]
```

Once committed, ArgoCD deploys a `CronWorkflow` that runs your container on the given schedule. Everything else - concurrency behavior, history limits, autoscaling - has a sensible chart default; add it only if you need something other than the default. See the reference table below.

### Configuration reference

| Field | Default | Description |
|---|---|---|
| `metadata.jobName` | `example-cron-job` | Name of the `CronWorkflow` resource. Required. |
| `spec.schedules` | `["*/1 * * * *"]` | One or more [cron schedules](https://en.wikipedia.org/wiki/Cron#Cron_expression) the job runs on. |
| `spec.concurrencyPolicy` | `Replace` | What happens if a run is still going when the next schedule fires: `Replace` stops the running job and starts the new one, `Forbid` skips the new run, `Allow` runs both concurrently. |
| `spec.successfulJobsHistoryLimit` / `spec.failedJobsHistoryLimit` | `5` | How many past runs of each outcome to keep for inspection. |
| `spec.startingDeadlineSeconds` | `30` | How much of a delay is tolerated before a missed schedule is abandoned rather than started late. |
| `spec.suspend` | `false` | Set to `true` to pause the schedule without removing the job. |
| `vpa.enabled` | - | Enables a VerticalPodAutoscaler for the job's containers. Not required, but set on every job we've seen in practice - recommended. |

`env` sets environment variables shared by every container template in the job - see [Configuring your app with environment variables](./app-configuration) for the general pattern.

### Secrets

Use `external_secrets` to pull values from AWS Secrets Manager into the job's environment, the same way other IDP charts do - see [Working with Secrets](./secrets) for how secrets get into Secrets Manager in the first place.

```yaml
external_secrets:
  - env_name: API_CLIENT_SECRET
    secretsmanager_name: my-cron-job_api-client-secret
```

`env_name` is the environment variable name inside the container. `secretsmanager_name` is the secret's name under `customer/<namespace>/` in Secrets Manager - the namespace and path prefix are added automatically. Add `property` if the secret holds a JSON object and you only want one key from it.

---

## Auto-updating the image

To have ArgoCD Image Updater bump the job's image tag automatically when a new build lands in ECR, see [Working with Argo Workflows and other non-standard CRDs](./auto-updates#working-with-argo-workflows-and-other-non-standard-crds) in the auto-updates guide - it walks through the exact `argocd_image_updater_helm_image_spec` and `argocd_image_updater_force_update` settings this chart needs.

---

## Monitoring & troubleshooting

Each run shows up as a Kubernetes `Job`/`Workflow` in the namespace, and its logs are collected the same way as any other workload - see [Application logs](./application-logs). To get notified when a run fails, see [Alerting](./alerting).

**Common gotchas:**

- **Nothing seems to run, or `cowsay` output shows up somewhere unexpected.** The chart's defaults deploy a working example job (`whalesay`, printing to logs via `cowsay`) so it's usable out of the box - if `spec.workflowSpec` isn't fully overridden in your `values.yaml`, parts of that default may still be in effect. Diff your rendered `CronWorkflow` against what you expect if a run doesn't do what you think it should.
- **A run doesn't fire when expected, or seems to replace one still in progress.** Check `spec.concurrencyPolicy` - the default, `Replace`, kills an in-flight run when the next schedule comes due rather than letting both run or skipping the new one. Set it to `Forbid` if overlapping runs would cause problems (e.g. two runs writing to the same resource).
- **A scheduled run never starts at all.** If the workflow controller was down or delayed past `spec.startingDeadlineSeconds` when a schedule fired, that run is skipped rather than started late. Raise `startingDeadlineSeconds` if late-but-still-useful runs matter for your job.

If something here doesn't cover your case, ask in your onboarding Slack channel - the IDP team is happy to help.
