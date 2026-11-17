---
title: From code to deploy in 30 minutes
nav_order: 2 
parent: Onboarding
domain: public
layout: last-reviewed
last_reviewed_on: 2026-11-17
review_in: 3 months
---


# From code to deploy in 30 minutes 🚀
> This guide helps you quickly deploy your first application to the developer platform.

> 💡 Prefer to start from a working example? Create a repository from the [IDP workshop template](https://github.com/jppol-idp/idp-workshop-template) and follow its `ASSIGNMENT.md`. It walks through the same steps as this guide, with a small service, CI workflow and deployment manifests already in place.

---
**By the end of this session, you will have:**

- Your code packaged as a container
- Deployed via GitOps with visibility in Argo CD
- Monitoring via Prometheus, logging via Loki, and visualization in Grafana
- You comply with the platform’s security requirements
- You are ready to use IDP in your daily work

---
## ⏱️ Prerequisites

Before you begin, make sure you have the following in place:

- [ ] Access to your IDP onboarding channel on Slack `#idp-TEAM-onboarding` and `#idp-announcements`
- [ ] Access to your IDP deployment repository on GitHub `https://github.com/jppol-idp/apps-TEAM`
- [ ] Access to your IDP tools, Argo CD and Grafana. Check your links at `https://github.com/jppol-idp/apps-TEAM/tree/main/apps/TEAM-dev`
- [ ] Access to your own code repository, e.g., `https://github.com/TEAM`
- [ ] Docker or similar installed

Note: To get access to IDP make a request in your `#idp-TEAM-onboarding` channel.

---

## 🪛 Step-by-Step: Deploy Your First Workload

### 1. 📁 Create an app in your own code repository 
See example [https://github.com/jppol-idp/generic-service](https://github.com/jppol-idp/generic-service)

Tip: Name the app after yourself to make it easy to identify.

The platform expects your container to keep running and answer HTTP requests on its service port. A script that prints a line and exits is restarted over and over.

```bash
mkdir app-name && cd app-name
echo 'Hello, IDP!' > index.html
```

Add a Dockerfile:

```Dockerfile
FROM python:3.11-slim
WORKDIR /app-name
COPY index.html .
CMD ["python", "-m", "http.server", "8080"]
```

---

### 2. 🐳 Build and optionally test your image locally

```bash
docker build . -t app-name:0.1.0
docker run -p 8080:8080 app-name:0.1.0
```

Open `http://localhost:8080` to see the page.

---

### 3. Upload your image to the IDP ECR repository

> 🚨 You typically don’t have permission to upload images directly — but your GitHub organization does.

This GitHub Action tags and pushes your image to ECR in our idp-shared account: 354918371398
[https://github.com/jppol-idp/tag-and-push-ecr/blob/main/action.yaml](https://github.com/jppol-idp/tag-and-push-ecr/blob/main/action.yaml)

The ECR repository allows GitHub Actions from your organization to upload images to a namespaced registry. For instance, Actions from Politiken's organization is allowed to push images to: `arn:aws:ecr:eu-west-1:354918371398:repository/pol/*`.

For an example on how to use it, view the [generic-service](https://github.com/jppol-idp/generic-service).

To both build an image and to tag and push it you can use this GitHub Action.
[https://github.com/jppol-idp/build-and-push-ecr](https://github.com/jppol-idp/build-and-push-ecr)

---
### 4. Create deployment configuration

Prepare a Helm chart in the deploy repo: `https://github.com/jppol-idp/apps-TEAM`

```bash
git clone https://github.com/jppol-idp/apps-TEAM.git
cd apps-TEAM/apps/TEAM-dev
mkdir app-name
```

**A deployment typically consists of two files:**

`application.yaml` - describes the Helm chart:

```yaml
apiVersion: v2
name: app-name
description: my first idp app
version: 0.1.0    # <-- version of the deployment definition

helm:
  chart: helm/idp-advanced
  chartVersion: "4.0.0"    # <-- example version, check latest at github.com/jppol-idp/helm-idp/releases
```

> The chart helm/idp-advanced refers to [idp-advanced in jppol-idp/helm-idp](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-advanced/Chart.yaml)

`values.yaml`- defines deployment-specific variables:

```yaml
image:
  repository: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/pol/app-name    # <-- replace pol with your organization prefix (see step 3)
  pullPolicy: IfNotPresent
  tag: "0.1.0"

service:
  port: 8080    # <-- the port your app listens on. Health checks call / on this port
```

> [Find a list of all configurable variables](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-advanced/README.md) or [see examples in our generic service](https://github.com/jppol-idp/apps-demo/tree/main/apps/demo-dev/generic-service) that covers most common needs.

__Automatic deployment__

The ECR repository uses immutable tags, meaning you can't use `latest` as a tag for your images.

But, the IDP cluster can update to the latest version of the images built, optionally limiting to tags matching certain SemVer or Regex patterns.

This feature is enabled in `application.yaml` with a set of annotations. Enabling this feature will limit the need to modify the deploy repository, as you only need to modify it in case of entirely new deployments or when tweaking the configuration. [Read more about auto updating images.](https://public.docs.idp.jppol.dk/how-to/auto-updates.html)

---

### 5. 📦 Commit and push to your GitOps repo and see deployment in Argo CD
After committing your application.yaml and values.yaml files to your `/jppol-idp/apps-TEAM` github repository deployment will start.

Check in Argo CD that your app has been synchronised and is healthy.

Your app is not reachable from outside the cluster yet. To give it a URL with a certificate, enable `ingress` in `values.yaml` (see the chart's README).

Go to Argo CD for deployment.
Check your link at `https://github.com/jppol-idp/apps-TEAM/tree/main/apps/TEAM-dev`

---

### 6. Confirm log output in Grafana
Logs from your app are collected automatically in Loki, and CPU and memory metrics in Prometheus. Both are visible in Grafana. To get your app's own metrics, expose a `/metrics` endpoint and enable `serviceMonitor` in `values.yaml`.

Go to Grafana for monitoring.
Check your link at `https://github.com/jppol-idp/apps-TEAM/tree/main/apps/TEAM-dev`

Go to drilldown to see your Prometheus stats
![image](https://public.docs.idp.jppol.dk/assets/onboarding-grafana-drilldown-metrics.png)

Go and drilldown and filter your logs with Loki
![image](https://public.docs.idp.jppol.dk/assets/onboarding-grafana-drilldown-logs.png)



---

### 7. 🏁 Congratulations

You're now up and running! 💪

You are **always** very welcome to ask questions in your onboarding channel on Slack - we're happy to help!

Also, feel free to explore our [How to section](https://public.docs.idp.jppol.dk/how-to/) for further guidance.

---
