### Architecture Decision Record (ADR)

#### Title: 009 Kubernetes Multicluster vs Multitenancy

#### Date: 2024-07-03

---

## Status

Forslag

## Kontekst

Vi skal beslutte om vi skal implementere Kubernetes med multicluster eller multitenancy strategi. Dette valg vil påvirke vores cloud-arkitektur, risici, omkostninger og driftsprocesser. Måske 15 prod og 15 test clusters ?

## Beslutning

(Detaljer om den endelige beslutning, når denne er truffet)


## Kubernetes Multicluster
   - Bedre **isolation** mellem miljøer, hvilket reducerer risikoen for "noisy neighbor" problemer.
   - Højere **sikkerhed** og enklere overholdelse af compliance.
   - Evne til at **skalere** individuelt per cluster efter behov uden at påvirke andre miljøer.
   - **Uafhængighed**, frihed til at tilpasse og opgradere individuelle clusters separat.
   - **Reduceret blast radius ved fejl**, da problemer i ét cluster ikke påvirker andre clusters.
   - Øget **operational cost** med flere clusters at administrere.
   - Højere ressourcekrav og **omkostninger** for at opretholde flere clusters.
   - Øget **netværks overhead** på tværs af clusters, hvilket kan påvirke kommunikation og performance.

## Kubernetes Multitenancy
   - **Omkostningseffektivitet**: Deling af ressourcer mellem flere tenants, hvilket reducerer overall omkostninger.
   - **Centraliseret administration**: Enkel administration af flere tenants fra et enkelt cluster.
   - **Ressourceudnyttelse**: Bedre udnyttelse af ressourcer ved at lade flere tenants dele de samme ressourcepuljer.
   - **Sikkerhed**: Øgede sikkerhedsrisici på grund af deling af ressourcer mellem flere tenants.
   - **Støj og performance**: Risiko for "noisy neighbor" problemer, hvor én tenant kan påvirke andre tenants ydeevne.
   - **Kompleksitet i isolation**: Sværere at opnå fuldstændig isolation mellem tenants.
   - **Omkostningsproblem**: Udfordrende at allokere ressourcer og omkostninger præcist mellem forskellige tenants, hvilket kan føre til ineffektiv omkostningsstyring.

## Alternativer

(Listning af mulige alternativer, som kan overvejes)  
Følgende produkter tilbyder Kubernetes multi-tenancy eller multi-cluster management:

- **Suse Rancher**: Multi Kubernetes cloud management.
- **Portainer**: Alternativ til Rancher.
- **KubeSphere**: Alternativ til Rancher, både multitenant og multicloud Kubernetes management.
- **Cloudify**: Orchestrator of orchestrators for hybrid cloud.
- **vCluster**: Kubernetes multi-tenancy.

### Relevante Ressourcer
- [Kubernetes: One Cluster or Many?](https://tanzu.vmware.com/content/blog/kubernetes-one-cluster-or-many)
- [Calculating SaaS Cost Per Tenant in AWS Kubernetes Environment](https://aws.amazon.com/blogs/apn/calculating-saas-cost-per-tenant-a-poc-implementation-in-an-aws-kubernetes-environment/)
- [Why Kubernetes is the Best Platform for Building Multi-Tenant SaaS Applications](https://www.cncf.io/blog/2021/06/10/why-kubernetes-is-the-best-platform-for-building-multi-tenant-saas-applications/)
- [Multi-Tenant Design Considerations for Amazon EKS Clusters](https://aws.amazon.com/blogs/containers/multi-tenant-design-considerations-for-amazon-eks-clusters/)
