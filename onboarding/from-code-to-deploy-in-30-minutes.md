---
title: From code to deploy in 30 minutes
nav_order: 2 
parent: Onboarding
domain: public
permalink: /codetodeploy
---


# From code to deploy in 30 minutes 🚀
> This playbook helps you quickly deploy your first application to the developer platform.

---
**By the end of this session, you will have:**

- [x] Access to IDP
- [x] Your code packaged as a container
- [x] Deployed via GitOps with visibility in ArgoCD
- [x] Monitoring via Prometheus, logging via Loki, and visualization in Grafana
- [x] You comply with the platform’s security requirements
- [x] You are ready to use IDP in your daily work

---

> 🚨 The examples use `Politiken`-specific domains and variables.  
> Make sure to **replace all values** with values relevant to your own organization.
> 
> Example: `https://github.com/jppol-idp/apps-pol` → `https://github.com/jppol-idp/apps-yourdomain`

---


## ⏱️ Prerequisites

Before you begin, make sure you have the following in place:

- [ ] Access to your code repository, e.g., [https://github.com/Politiken](https://github.com/Politiken)
- [ ] Access to your IDP deployment repository, e.g., [https://github.com/jppol-idp/apps-pol](https://github.com/jppol-idp/apps-pol) ([access management](https://github.com/orgs/jppol-idp/teams/apps-pol/members))
- [ ] Access to #idp-support on [Slack](https://ekstrabladet.slack.com/archives/C08HWLGQCTE)
- [ ] Access to IDP tools, e.g., [https://argocd.pol-test.idp.jppol.dk](https://argocd.pol-test.idp.jppol.dk), [https://grafana.pol-test.idp.jppol.dk](https://grafana.pol-test.idp.jppol.dk)
- [ ] Docker or similar installed

---

## 🪛 Step-by-Step: Deploy Your First Workload

### 1. 📁 Create an app in your code repository (se example [https://github.com/Politiken/idp-test](https://github.com/Politiken/idp-test))
Tip: Name the app after yourself to make it easy to identify.

```bash
mkdir app-name && cd app-name
echo 'print("Hello, IDP!")' > app-name.py
```

Add a Dockerfile:

```Dockerfile
FROM python:3.11-slim
WORKDIR /app-name
COPY app-name.py .
CMD ["python", "app-name.py"]
```

---

### 2. 🐳 Build and optionally test your image locally

```bash
docker build . -t app-name.py:0.1.0
docker run app-name.py:0.1.0
```

---

### 3. Upload your image to the IDP ECR repository

> 🚨 You typically don’t have permission to upload images directly — but Politiken’s GitHub organization does.

This GitHub Action builds, tags, and uploads your image to ECR in our idp-shared account: 354918371398
[https://github.com/Politiken/idp-test/blob/master/.github/workflows/build-push-deploy.yaml](https://github.com/Politiken/idp-test/blob/master/.github/workflows/build-push-deploy.yaml)


```yaml
uses: jppol-idp/tag-and-push-ecr@a7bb367d9e4393d243da605e4c4b700c18e2c34d
namespace: pol
image_tags: ${{ github.run_number }}
```

The ECR repository allows GitHub Actions from Politiken’s organization to upload images here:
arn:aws:ecr:eu-west-1:354918371398:repository/pol/*

> You can verify the image upload by assuming the IDP-client-read-access role in the AWS account aws-jppol-idp-shared [aws-jppol-idp-shared](https://jppol-sso.awsapps.com/start#/)

__Automatic deployment__

The IDP cluster can update to the latest version of the images built, optionally limiting to tags matching certain SemVer 
og Regex patterns.

This feature is enabled in `application.yaml` with a set of annotations. Enabling this feature will limit the need to 
modify the deploy repository, as you only need to modify it in case of entirely new deployments or when tweaking the 
configuration. [You can read more about auto updating images here.](https://public.docs.idp.jppol.dk/how-to-auto-update)

---
### 4. Create deployment configuration

Prepare a Helm chart in the deploy repo: [https://github.com/jppol-idp/apps-pol](https://github.com/jppol-idp/apps-pol)

```bash
git clone https://github.com/jppol-idp/apps-pol.git
cd apps-pol/apps/pol-test
mkdir app-name
```

**A deployment typically consists of two files:**

`application.yaml` - describes the Helm chart:

```yaml
apiVersion: v2
name: app-name
description: my first idp app
version: 0.1.0    # <-- version af deployment definition

helm:
  chart: helm/idp-advanced
  chartVersion: "0.1.14"    # <-- version af helm chart
```

> The chart helm/idp-advanced refers to [jppol-idp/helm-idp-advanced](https://github.com/jppol-idp/helm-idp-advanced/tree/main/charts/idp-advanced/Chart.yaml)

`values.yaml`- defines deployment-specific variables:

```yaml
image:
  repository: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/pol/app 
  pullPolicy: IfNotPresent
  tag: "0.1.0"
```

> You can go here and [find a list of all configurable variables](https://github.com/jppol-idp/helm-idp-advanced/blob/main/README.md)

---

### 5. 📦 Commit and push to your GitOps repo and see deployment in ArgoCD
After committing your chart.yaml and values.yaml files to your "apps-pol" github repository deployment will start.

Check in ArgoCD if your app has been synchronised and deployed and a certificate been issued.  

Go to ArgoCD for deployment [https://argocd.pol-test.idp.jppol.dk](https://argocd.pol-test.idp.jppol.dk)

---

### 6. Confirm log output in Grafana
Metrics are automatically exposed with Prometheus and Loki and are visible in Grafana.

Go to Grafana for monitoring
[(https://grafana.pol-test.idp.jppol.dk)](https://grafana.pol-test.idp.jppol.dk)

Go to drilldown to see your Prometheus stats
![image](https://public.docs.idp.jppol.dk/assets/onboarding-grafana-drilldown-metrics.png)

Go and drilldown and filter your logs with Loki
![image](https://public.docs.idp.jppol.dk/assets/onboarding-grafana-drilldown-logs.png)



---

### 7. 🏁 Congratulations

You're now up and running! 💪

You are **always** very welcome to ask questions in [Slack](https://ekstrabladet.slack.com/archives/C08HWLGQCTE) - we're happy to help!

Also, feel free to explore our [FAQ](faq) for answers to frequently asked questions and onboarding guidance.

---


---
*Last updated: 2025-06-23*
