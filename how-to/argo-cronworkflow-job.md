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

This covers running a single container on a schedule, with environment variables, secrets, and AWS permissions - what most scheduled jobs need. Jobs with multiple steps are covered separately, under [Advanced: multi-step jobs (DAG)](#advanced-multi-step-jobs-dag).

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

## IAM permissions with IRSA

If your job needs to call AWS APIs directly (S3, DynamoDB, SES, etc.), enable IAM Roles for Service Accounts (IRSA) on the job's ServiceAccount and attach the permissions it needs. Requires chart version `1.2.6` or later.

```yaml
serviceAccount:
  create: true
  irsa:
    enabled: true
    iamPolicyStatements:
      - Effect: Allow
        Action:
          - s3:ListBucket
        Resource:
          - arn:aws:s3:::my-team-artifacts
      - Effect: Allow
        Action:
          - s3:GetObject
          - s3:PutObject
        Resource:
          - arn:aws:s3:::my-team-artifacts/*
```

This creates an IAM role trusted by the job's ServiceAccount, with the policy statements above attached. For S3 access specifically, see [Workload access (IRSA)](./s3-bucket#workload-access-irsa) in the S3 guide - the same `iamPolicyStatements` pattern applies there.

### Testing locally

To run or debug your job's code locally with the same AWS permissions it has in the cluster, assume the job's IRSA role from your workstation:

```bash
eval "$(./scripts/assume-<namespace>-irsa-role.sh <job-name>)"
aws sts get-caller-identity
```

`<job-name>` is `metadata.jobName` from your `values.yaml`, and the scripts live in your team's apps repository under `scripts/` - see [Assuming the role from your machine](./s3-bucket#assuming-the-role-from-your-machine) in the S3 guide for the equivalent flow against the namespace's S3 access role.

---

## Auto-updating the image

To have ArgoCD Image Updater bump the job's image tag automatically when a new build lands in ECR, see [Working with Argo Workflows and other non-standard CRDs](./auto-updates#working-with-argo-workflows-and-other-non-standard-crds) in the auto-updates guide - it walks through the exact `argocd_image_updater_helm_image_spec` and `argocd_image_updater_force_update` settings this chart needs.

---

## Advanced: multi-step jobs (DAG)

Everything above covers a single container on a schedule, which is what most jobs need. If a job needs multiple steps in one run - in order, in parallel, or with dependencies between them - `workflowSpec.templates` can hold several templates wired together with a Directed Acyclic Graph (DAG) instead of just one. Requires chart version `1.2.6` or later.

Give one template a `dag` block instead of a `container` block, and reference your other templates by name:

```yaml
spec:
  schedules:
    - "0 23 * * *"
  workflowSpec:
    entrypoint: my-cron-job
    templates:
      - name: my-cron-job
        dag:
          tasks:
            - name: fetch
              template: fetch-data
            - name: process
              template: process-data
              dependencies:
                - fetch

      - name: fetch-data
        container:
          image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/my-team/my-cron-job:latest
          command: ["node"]
          args: ["fetch.js"]

      - name: process-data
        container:
          image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/my-team/my-cron-job:latest
          command: ["node"]
          args: ["process.js"]
```

`entrypoint` points at the DAG template (`my-cron-job` here), not at one of the container steps. Each task's `template` field names one of the other templates in the list; `dependencies` controls ordering - tasks with no dependency on each other run in parallel. See [Argo Workflows' DAG documentation](https://argo-workflows.readthedocs.io/en/latest/walk-through/dag/) for the full set of options (loops, conditionals, passing artifacts between steps).

Everything else on this page - secrets, IRSA, auto-updating - applies the same way whether a job has one template or several.

---

## Monitoring & troubleshooting

Each run shows up as a Kubernetes `Job`/`Workflow` in the namespace, and its logs are collected the same way as any other workload - see [Application logs](./application-logs). To get notified when a run fails, see [Alerting](./alerting).

**Common gotchas:**

- **Nothing seems to run, or `cowsay` output shows up somewhere unexpected.** The chart's defaults deploy a working example job (`whalesay`, printing to logs via `cowsay`) so it's usable out of the box - if `spec.workflowSpec` isn't fully overridden in your `values.yaml`, parts of that default may still be in effect. Diff your rendered `CronWorkflow` against what you expect if a run doesn't do what you think it should.
- **A run doesn't fire when expected, or seems to replace one still in progress.** Check `spec.concurrencyPolicy` - the default, `Replace`, kills an in-flight run when the next schedule comes due rather than letting both run or skipping the new one. Set it to `Forbid` if overlapping runs would cause problems (e.g. two runs writing to the same resource).
- **A scheduled run never starts at all.** If the workflow controller was down or delayed past `spec.startingDeadlineSeconds` when a schedule fired, that run is skipped rather than started late. Raise `startingDeadlineSeconds` if late-but-still-useful runs matter for your job.
- **`AccessDenied` calling AWS APIs from inside the job.** Check `serviceAccount.irsa.enabled` is `true` and that `iamPolicyStatements` actually covers the action and resource being called - see [IAM permissions with IRSA](#iam-permissions-with-irsa).
- **`AccessDenied` on `sts:AssumeRole` when assuming the job's role from your own machine.** Requires chart version `1.2.6` or later - earlier versions only trust the running pod's identity, not a human session.
- **A DAG template fails validation, or a step runs with the wrong container.** Requires chart version `1.2.6` or later for [multi-step jobs](#advanced-multi-step-jobs-dag) - earlier versions could inject a stray container into DAG parent templates.

If something here doesn't cover your case, ask in your onboarding Slack channel - the IDP team is happy to help.
