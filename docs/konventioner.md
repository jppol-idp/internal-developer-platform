# Navne konventioner

## IDP AD Grupper

AD grupper skal hedde `idp-kunde-miljø-app-permission`.

IDP team opretter grupperne, og så er det efterfølgende op til Teamleads at populere dem vha ServiceNOW

Miljø er typisk Kubernetes namespace, fx `dev`, `test`, `uat`, `prod`. 


### Argo
- idp-koa-prod-argocd-read
- idp-koa-prod-argocd-write

### Grafana
- idp-koa-prod-grafana-read
- idp-koa-prod-grafana-write

### AWS (normalt kun test og prod da det refererer til aws konto)
- idp-koa-prod-aws-read
- idp-koa-prod-aws-write

## GitHub

AD grupper bør hedde med `github-miljø-permission` fx
- github-koa-read
- github-koa-write

## AWS 

AWS konti provisioneres med navne startende med `aws-jppol-` efterfulgt af `navn-miljø`, fx  
- `aws-jppol-koa-prod`   

Kontakt emails til aws konti starter med `aws-jppol+` efterfulgt af `navn-miljø@jppol.dk`, fx 
- `aws-jppol+koa-prod@jppol.dk`   

Mails til addresser der starter med aws-jppol+ bliver forwardet til aws-accounts-kit@pol.dk
