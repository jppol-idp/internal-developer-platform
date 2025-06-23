---
title: Fra kode til deploy på 30 min
nav_order: 0 
parent: Onboarding
domain: public
---

# From code to deploy in 30 minutes 🚀
> [!IMPORTANT]
> Examples are in the context of Politiken - change Politiken/POL variables in links to your own domain.


> Denne playbook hjælper dig med hurtigt at få din første applikation deployet til udviklerplatformen.

---
Du vil efter denne session have opnået:

- [x] Adgang til IDP
- [x] Din kode er pakket som en container
- [x] Den er deployet via GitOps
- [x] Den er overvåget via Prometheus, logget via Loki og visualiseret via Grafana
- [x] Du overholder platformens og dermed JPPOLs sikkerhedskrav

---


## ⏱️ Forudsætninger

Før du starter, skal du have følgende på plads:

- [ ] Adgang til dit kode repo: fx [https://github.com/Politiken](https://github.com/Politiken)
- [ ] Adgang til dit deploy repo: fx [https://github.com/jppol-idp/apps-pol](https://github.com/jppol-idp/apps-pol) ([adgangstyring](https://github.com/orgs/jppol-idp/teams/apps-pol/members))
- [ ] Adgang til #idp-support på [Slack](https://ekstrabladet.slack.com/archives/C08HWLGQCTE)
- [ ] Adgang til IDP tools: fx [https://pol-test.idp.jppol.dk/](https://pol-test.idp.jppol.dk/)
- [ ] Adgang til rollen `idp-customer-access` i din AWS konto [aws-jppol-pol-test](https://jppol-sso.awsapps.com/start#/)
- [ ] Adgang til rollen `IDP-client-read-access` i vores ECR AWS konto [aws-jppol-idp-shared](https://jppol-sso.awsapps.com/start#/)
- [ ] Docker eller lign. installeret (brew install --cask docker)

---

## 🪛 Trin-for-trin: Deploy din første workload

### 1. 📁 Opret app i dit kode repository (se evt [https://github.com/Politiken/idp-test](https://github.com/Politiken/idp-test)

```bash
mkdir app && cd app
echo 'print("Hello, IDP!")' > app.py
```

Tilføj en `Dockerfile`:

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```

### 2. 🐳 Byg og test evt dit image lokalt

```bash
docker build . -t app.py:0.1.0
docker run app.py:0.1.0
```

---

### 3. Upload dit image til IDPs ECR repository

> 🚨 Du har som udgangspunkt ikke lov til at uploade dit image direkte, men det har Politikens GitHub organisation.

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

__Automatisk deploy__

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

### 4. Opret deployment konfiguration

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

### 5. 📦 Commit og push til GitOps repo

---

- Tjek i ArgoCD UI om `myapp` er synkroniseret.
- Metrics eksponeres automatisk og er synlige i Prometheus & Grafana.
- Bekræft log output i Grafana
- 
---

## 🏁 Tillykke

Du er nu i gang! 💪

---


---
*Sidst opdateret: 2025-04-23*
