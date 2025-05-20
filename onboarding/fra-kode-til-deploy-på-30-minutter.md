---
title: Fra kode til deploy på 30 min
nav_order: 0 
parent: Onboarding
domain: public
---

# Fra kode til deploy på 30 minutter 🚀

> Denne playbook hjælper dig med hurtigt at få din første applikation deployet til udviklerplatformen.

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

### 4. 📦 Commit og push til GitOps repo

---

- Tjek i ArgoCD UI om `myapp` er synkroniseret.
- Bekræft log output i Grafana
- Metrics eksponeres automatisk og er synlige i Prometheus & Grafana.
- Hvis du bruger tracing (OpenTelemetry), vil spans dukke op i Tempo.

---

### 5. Adgang til Kubernetes

Authenticate til din AWS konto med aws cli `brew install awscli`

Hvis du allerede har sat SSO login op, 

aws sts get-caller-identity [--profile session]
aws configure export-credentials [--profile koa-dev]
aws eks list-clusters --region eu-west-1 --profile koa-dev



> Nogen vælger at bruge aws-sso `brew install aws-sso-cli` fordi man ikke behøver at vedligeholde sine roller manuelt i ~/.aws/config - men nu anbefales det fra AWS at bruge deres eget tool, sjovt nok. Det er måske også ok, nu hvor det understøtter sso, men det er da stadig irriterende at bøvle med manuel konfiguration. Da de fleste dog kun har et par konti, og at ventetiden på aws-cli sync'er stiger med antallet af konti, overgiver jeg mig.

```bash
aws configure sso
```
answer truthfully - note, if you call it default, it will be default - maybe you already have that.

SSO session name (Recommended): `default`    # <-- this is the sso session
SSO start URL [None]:  `https://jppol-sso.awsapps.com/start#/`
SSO region [None]: `eu-west-1`
SSO registration scopes [sso:account:access]:
There are 78 AWS accounts available to you. `vælg din konto`
There are 2 roles available to you. `vælg rollen idp-customer-access`
Default client Region [None]: `eu-west-1`
CLI default output format (json if not specified) [None]:
Profile name [blabla]: `idp-dev`

If you need to add another account run

```bash
aws configure sso
```
SSO session name [default]:
Using the account ID 01234566788
Using the role name "AWSAdministratorAccess"
Default client Region [eu-west-1]:
CLI default output format (json if not specified) [None]:
Profile name [accountname-and-number]: `idp-prod`

eller du kan bare rette det direkte i ~/.aws/config


__find navnet på dit cluster__

aws eks list-clusters --profile koa-dev

tilføj dit cluster til ~/.kube/config

aws eks update-kubeconfig --name prod-cluster --region eu-west-1 profile --koa-dev


adgang til k9s

k9s læser default config fra (~/.kube/config)

check selv med `kubectl config current-context` 

skift evt cluster context med `:ctx` og tryk Enter

Get terminal

kubectl get pods --namespace koa-test

kubectl exec -it b2b-offer-api-net-koa-dev-84fbbff795-5sjbr -n koa-dev -- /bin/bash
kubectl get pod b2b-offer-api-net-koa-dev-84fbbff795-5sjbr -n koa-dev -o jsonpath='{.spec.containers[*].name}'

logs

k logs -n crossplane-system 

## 🏁 Klar på 30 minutter

Når ovenstående trin er fulgt:

- [x] Din kode er pakket som en container
- [x] Den er deployet via GitOps
- [x] Den er overvåget via Prometheus, logget via Loki og traced via Tempo
- [x] Du overholder platformens sikkerhedskrav

Du er nu i gang! 💪

---

## ✅ Next steps: Tilføj sikkerhed og policies

- Tilføj `securityContext` i Helm chart til at køre som non-root
- Tilføj resource limits
- Scan dit image med Trivy i CI
- Valider mod Kyverno policies

---
*Sidst opdateret: 2025-04-23*
