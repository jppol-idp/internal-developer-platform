---
title: FAQ
nav_order: 0 
parent: Onboarding
domain: public
---

# FAQ - IDP 🚀

---



### 1. 🔑 Hvordan får jeg adgang til IDP?
For at få adgang skal din teamlead gøre følgende: 
- Tilføje dig via jeres servicenow formular, så du får tilføjet de korrekte AD-gruppe-rettigheder. 
- Give dig adgang til jeres Github Enterprise repo under vores jppol-idp organisation.

Hvis du eller dit team har spørgsmål eller oplever problemer, så smid altid bare en [Slack til os](https://ekstrabladet.slack.com/archives/C07TZPBHFUL). 

Er jeres team endnu ikke oprettet i IDP? Så tag fat i os – så tager vi en snak.

---

### 2. 🛠️ Hvilke værktøjer får jeg med IDP?
- Github Enterprise
- ArgoCD
- Argo Workflows
- Graphana, Prometheus, Loki
- PagerDuty

Du finder en oversigt over direkte links i readme-filen i roden.
https://github.com/jppol-idp/apps-pol/tree/main/apps/pol-dev

---
### 3. 🛠️ Hvilke værdier kan jeg sætte i mit helm chart?

Her finder du (copied) [værdierne beskrevet](https://docs.idp.jppol.dk/onboarding/helm-chart-values). 

Her finder du [værdierne beskrevet](https://github.com/jppol-idp/helm-idp-advanced/blob/main/README.md). 


### 4. 🪣 Hvordan spinner jeg en S3 bucket op?
Vi har dette repo: https://github.com/jppol-idp/helm-idp-s3-bucket/blob/main/charts/idp-s3-bucket/values.yaml
Lav en folder i stil med de øvrige I har i jeres apps-cluster.

I application.yaml skal du have noget i stil med:

```yaml
apiVersion: v2
name: ear-service
description: Dev test application
version: 0.1.0
slackChannel: idp-argocd-koa

helm:
  chart: helm/idp-s3-bucket
  chartVersion: "0.1.0"
```
(så du refererer et andet chart)
Values kan tage udgangspunkt i repo-linket.

```yaml
# -- Default values for helm-idp-s3-bucket.
# -- This is a YAML-formatted file.
# -- Declare variables to be passed into your templates.

buckets:
    # -- (string) The name of the bucket
    # @default -- "none"
  - name: "bucket-name"
    # -- Optional: The region of the bucket. default to 'eu-west-1'
    region: "eu-west-1"
    # -- Optional: The ACL of the bucket. default to 'private'.
    # Valid values: private, public-read, public-read-write, aws-exec-read, authenticated-read, bucket-owner-read, bucket-owner-full-control, log-delivery-write
    acl: "private"
    # -- Optional: The tags of the bucket. default tag 'crossplane: "true"' will always be set.
    tags:
      - key: "Name"
        value: "bucket-name"
#  - name: "jppol-idp-tjallo-tjalde"
```

Væsentligst er at skifte bucket-name.

Du kan tilføjet flere buckets af gange i filen, hvis det ønskes.

Du skal i applikationens values-fil give adgang via irsa, for de enkelte applikationer.

---

### 5. 🤫 Hvordan bør vi håndtere config og secrets?
Vi anbefaler at konfiguration ligger som environmentvariable, der kan defineres i values-filen:
```yaml
env:
  - name: ASPNETCORE_ENVIRONMENT
    value: Staging
  - name: UseIDPSecrets
    value: "true"
  - name: Hangfire__Enabled
    value: "false"
  - name: SubscriptionOrderService__apiBasePath
    value: "http://subscription-order-service-koa-test-service.koa-test.svc.cluster.local:8080"
  - name: SaapiService__apiBasePath
    value: "http://saapi-koa-test-service.koa-test.svc.cluster.local:8080/"
  - name: ASPNETCORE_HTTP_PORTS
    value: "8080"
```

Secrets bør ligge i secretsmanager. 

I skal sætte secrets via nogle actions i jeres app-repository og få værdierne eksponeret til applikationen som environmentparametre, ved at tilføje en blok til values-filen af formatet:

```yaml
external_secrets:
  - env_name: VALUE_FOR_ENVIRONMENT1
    secretsmanager_name: NAME_IN_SSM1
  - env_name: MEDIELOGIN_CLIENT_SECRET
    secretsmanager_name: medielogin_client_secret
```

Applicationen vil derefter have følgende environment-variable tilgængelige VALUE_FOR_ENVIRONMENT1 og MEDIELOGIN_CLIENT_SECRET

Kubernetes henter værdierne fra secretsmanager, så man behøver ikke have applikationskode til at foretage det opslag.

Der står lidt mere om det i apps-repo under hvert namespace. Eksempel her: https://github.com/jppol-idp/apps-[jeres-team]/blob/main/apps/[jeres-team]-test/secrets.md


---

### 6. 🖇️ Hvordan giver vi vores IDP containere adgang til vores managed service uden for IDP?

I kan se IP-adresser i README. Eksempel:
https://github.com/jppol-idp/apps-xxxx/blob/main/apps/xxxx-dev/README.md

IP'erne afhænger lidt af hvordan servicen fungerer.

Skal I bruge eksterne IP'er, så er det NAT-gatewayen, der er interessant.

Det er ikke et range, men specifikke addresser (altså et /32 "range")

---

### 7. 🧁 Hvordan laver vi custom domains?

I binder domæner via fqdn-feltet i values-filen.

Der er dog en begrænsning i forhold til hvilke domæner, der er tilgængelige i de enkelte konti. Dem kan I se i readme-filen ovre i apps-repositoriet (under de enkelte namespaces).

For pol-dev ligger den her: https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md

Available domains
pol-test.idp.jppol.dk
pol-dev.idp.jppol.dk

Det er "default-domænerne", som godt kan udvides.
Det kræver noget konfiguration hos os.

Når et domæne først er tilgængeligt kan I vælge sub-domæner på de anviste domæner i fqdn for de enkelte applikationer. 
Når der tilføjes elementer bliver der lavet dns-records automatisk. Samtidig udstedes der et certifikat til det konkrete domæne.

Hvis I ønsker records på andre domæner, end dem, der er tilgængelige i kontoen, så kan det også lade sig gøre. Det er dog betragteligt mere besværligt.

Hvis domænet hostes i en anden konto skal man finde dem der ejer hoveddomænet og lave en A-record til de load-balancer-adresser, der står i README. 
Når den er på plads kan man tilføje adressen i values-filen, og derefter fungerer certifikatudstedelse automatisk.

---

### 8. 🔐 Hvordan lukker vi for ekstern adgang til vores API endpoints?

Hvis servicen kun skal kunne nås internt i _clusteret_ skal I slå public nginx fra så den kun er tilgængelig på private nginx. 

Hvis den skal være public men begrænset kan I lave IP-whitelisting i values-filen.

```yaml
   nginx:
    public:
      enabled: true
      annotations:
        nginx.ingress.kubernetes.io/whitelist-source-range: 91.214.20.0/24,54.220.9.41/32,52.50.24.11/32
        nginx.ingress.kubernetes.io/proxy-buffer-size: "256k"
        nginx.ingress.kubernetes.io/proxy-buffers: "4 256k"
        nginx.ingress.kubernetes.io/large-client-header-buffers: "4 16k"
        nginx.ingress.kubernetes.io/proxy-busy-buffers-size: "256k"
        nginx.ingress.kubernetes.io/proxy-send-timeout: "130s"
    private:
      enabled: true
      annotations: {} 
```
Ovenstående er et eksempel på whitelisting.

Der er også sat et par andre indstillinger med bufferstørrelser. Den relevante annotation er
`nginx.ingress.kubernetes.io/whitelist-source-range: 91.214.20.0/24,54.220.9.41/32,52.50.24.11/32`

Det er også her I kan vælge at sætte nginx.public.enabled til false, hvis man slet ikke vil have servicen offentligt eksponeret.

> [!NOTE]
> På et senere tidspunkt bliver det også muligt at give adgang fra andre AWS-konti via en transit gateway.

---
### 9. Hvordan laver vi automatisk deployment til ECR fra vores kode repository



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


---
*Sidst opdateret: 17-juni-2025*
