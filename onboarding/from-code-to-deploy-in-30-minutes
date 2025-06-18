---
title: Fra kode til deploy på 30 min
nav_order: 0 
parent: Onboarding
domain: public
---

# Fra kode til deploy på 30 minutter 🚀

> Denne playbook hjælper dig med hurtigt at få din første applikation deployet til udviklerplatformen.

Du vil opnå:

- [x] Din kode er pakket som en container
- [x] Den er deployet via GitOps
- [x] Den er overvåget via Prometheus, logget via Loki og du kan visualisere med Grafana
- [x] Du overholder platformens sikkerhedskrav

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

Hvis du allerede har sat SSO login op: 

```
aws sso login --profile pol-test
aws sts get-caller-identity [--profile session]
aws configure export-credentials [--profile pol-test]
aws eks list-clusters --region eu-west-1 --profile pol-test
```

> Maske bruger du aws-sso `brew install aws-sso-cli` fordi man ikke behøver at vedligeholde sine roller 
manuelt i ~/.aws/config - men AWS anbefaler at bruge deres eget tool. 

Hvis du ikke 

`aws configure sso`

```
SSO session name (Recommended): `default`    # <-- this is the sso session
SSO start URL [None]:  `https://jppol-sso.awsapps.com/start#/`
SSO region [None]: `eu-west-1`
SSO registration scopes [sso:account:access]:
There are 78 AWS accounts available to you. `vælg din konto`
There are 2 roles available to you. `vælg rollen idp-customer-access`
Default client Region [None]: `eu-west-1`
CLI default output format (json if not specified) [None]:
Profile name [blabla]: `idp-dev`
```

For at tilfoje en anden konto:

`aws configure sso`

```
SSO session name [default]:
Using the account ID 01234566788
Using the role name "AWSAdministratorAccess"
Default client Region [eu-west-1]:
CLI default output format (json if not specified) [None]:
Profile name [accountname-and-number]: `idp-prod`
```

eller ret det direkte i ~/.aws/config


__find navnet på dit cluster__


`aws eks list-clusters --region eu-west-1 --profile pol-test`

tilføj dit cluster til ~/.kube/config

`aws eks update-kubeconfig --name pol-test --region eu-west-1 --profile pol-test`


### adgang til k9s

`brew install k9s`

k9s læser default config fra `~/.kube/config)` - check med `kubectl config current-context` 

> skift evt cluster context med `:ctx` og tryk Enter

### Fejlsogning

`kubectl get pods --namespace pol-test`

get terminal:

`kubectl exec -it net-utils-pol-test-55749f75f-ct5lw -n koa-dev -- /bin/bash`

get all containers in pod:

`kubectl get pod net-utils-pol-test-55749f75f-ct5lw -n pol-test -o jsonpath='{.spec.containers[*].name}'`

get logs:

`k logs -n pol-test net-utils-pol-test-55749f75f-ct5lw`
`k logs -n pol-test net-utils-pol-test-55749f75f-ct5lw --previous`

get events:

`k describe pod net-utils-pol-test-55749f75f-ct5lw -n pol-test`

get deployment:

`kubectl get pod net-utils-pol-test-55749f75f-ct5lw -n pol-test -o jsonpath='{.metadata.ownerReferences[*].name}'`

get deployment state:

`k describe deployment net-utils-pol-test -n pol-test`

get deployment manifest

`k get deployment -n pol-test net-utils-pol-test -o yaml`

### get argocd sync state

`brew install argocd`

find argo via port forward indtil videre (transit gateway)

`kubectl port-forward svc/argocd-server -n argocd 8080:443`

login i argocd

`argocd login localhost:8080 --sso --insecure`

hvem er jeg for argo:

`argocd account get-user-info`

get argo sync state

`argocd app list`

get app state:

`argocd app get argocd/net-utils-pol-test`






## 🏁 Tillykke

Du er nu i gang! 💪

---


---
*Sidst opdateret: 2025-04-23*
