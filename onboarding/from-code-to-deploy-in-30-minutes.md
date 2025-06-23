---
title: From code to deploy to observability in 30 minutes 
nav_order: 0 
parent: Onboarding
domain: public
---

# From code to deploy to observability in 30 minutes 🚀
> This playbook helps you quickly deploy your first application to the developer platform.


> [!IMPORTANT]
> The examples use `Politiken`-specific domains and variables.  
> Make sure to **replace all values** with values relevant to your own organization.
> 
> Example: `https://github.com/jppol-idp/apps-pol` → `https://github.com/jppol-idp/apps-yourdomain`


---
**By the end of this session, you will have:**

- [x] Access to the IDP
- [x] Your code packaged as a container
- [x] Deployed via GitOps with visibility in ArgoCD
- [x] Monitoring via Prometheus, logging via Loki, and visualization in Grafana
- [x] You comply with the platform’s — and thus JPPOL’s — security requirements

---


## ⏱️ Prerequisites

Before you begin, make sure you have the following in place:

- [ ] Access to your code repository, e.g., [https://github.com/Politiken](https://github.com/Politiken)
- [ ] Access to your deployment repository, e.g., [https://github.com/jppol-idp/apps-pol](https://github.com/jppol-idp/apps-pol) ([access management](https://github.com/orgs/jppol-idp/teams/apps-pol/members))
- [ ] Access to #idp-support on [Slack](https://ekstrabladet.slack.com/archives/C08HWLGQCTE)
- [ ] Access to IDP tools, e.g., [https://pol-test.idp.jppol.dk/](https://pol-test.idp.jppol.dk/)
- [ ] Access to the role idp-customer-access in your AWS account aws-jppol-pol-test [aws-jppol-pol-test](https://jppol-sso.awsapps.com/start#/)
- [ ] Access to the role IDP-client-read-access in our ECR AWS account aws-jppol-idp-shared [aws-jppol-idp-shared](https://jppol-sso.awsapps.com/start#/)
- [ ] Docker or similar installed

---

## 🪛 Step-by-Step: Deploy Your First Workload

### 1. 📁 Create an app in your code repository (se example [https://github.com/Politiken/idp-test](https://github.com/Politiken/idp-test))
Name the app after yourself to make it easy to identify.

```bash
mkdir app && cd app
echo 'print("Hello, IDP!")' > app.py
```

Add a Dockerfile:

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```

### 2. 🐳 Build and optionally test your image locally

```bash
docker build . -t app.py:0.1.0
docker run app.py:0.1.0
```

---

### 3. Upload your image to the IDP ECR repository

> 🚨 You typically don’t have permission to upload images directly — but Politiken’s GitHub organization does.

Denne [GitHub Action](https://github.com/Politiken/idp-test/blob/master/.github/workflows/build-push-deploy.yaml) bygger, 
tagger og uploader dit image til ECR i vores idp-shared konto: 354918371398


```yaml
uses: jppol-idp/tag-and-push-ecr@a7bb367d9e4393d243da605e4c4b700c18e2c34d
namespace: pol
image_tags: ${{ github.run_number }}
```

Vores ECR repository tillader at actions i Politikens github organisation må uploade images hertil
`arn:aws:ecr:eu-west-1:354918371398:repository/pol/*`

> Du kan checke om dit image er uploadet korrekt, ved at vælge `IDP-client-read-access` rollen i AWS konto [aws-jppol-idp-shared](https://jppol-sso.awsapps.com/start#/)

__Automatic deploy__

Efter image er uploaded, kan deployment trigges direkte fra jeres kode repository. Disse github secrets er oprettet i Politikens org, og kan bruges til at trigge deployment i IDP repository jppol-idp/pol-apps 

- IDP_DEPLOY_APP_ID
- IDP_DEPLOY_APP_KEY

```yaml
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ vars.IDP_DEPLOY_APP_ID }}
          private-key: ${{ secrets.IDP_DEPLOY_APP_KEY }}
          owner: ${{ github.repository_owner }}
          repositories: apps-pol
```

> GitHub app'en befinder sig her [https://github.com/organizations/jppol-idp/settings/installations/61380040](https://github.com/organizations/jppol-idp/settings/installations/61380040)

### 4. Create deployment configuration

Forbered helm chart i deploy repo [https://github.com/jppol-idp/apps-pol](https://github.com/jppol-idp/apps-pol)

```bash
git clone https://github.com/jppol-idp/apps-pol.git
cd apps-pol/apps/pol-test
mkdir app
```

**Et deployment består typisk af 2 filer**
`application.yaml` beskriver helm chart 

```yaml
apiVersion: v2
name: app
description: app 
version: 0.1.0    # <-- version af deployment definition

helm:
  chart: helm/idp-advanced
  chartVersion: "0.1.14"    # <-- version af helm chart
```

> chart: `helm/idp-advanced` henviser til [jppol-idp/helm-idp-advanced](https://github.com/jppol-idp/helm-idp-advanced/tree/main/charts/idp-advanced/Chart.yaml) hvor detaljer om vardier er beskrevet

`values.yaml` beskriver variabler specifikke for dette deployment, fx

```yaml
image:
  repository: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/pol/app 
  pullPolicy: IfNotPresent
  tag: "0.1.0"
```
> [README.md](https://github.com/jppol-idp/helm-idp-advanced/blob/main/README.md) beskriver hvilke values der kan defineres
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
![image](https://github.com/user-attachments/assets/a634da84-ff6c-4497-a39f-e22a15ee60fb)

Go and drilldown and filter your logs with Loki
![image](https://github.com/user-attachments/assets/e22fed76-be65-4c54-8f11-61e784c09bf0)



---

## 🏁 Congratulations

You're now up and running! 💪

---


---
*Last updated: 2025-06-23*
