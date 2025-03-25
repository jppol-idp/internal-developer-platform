### Architecture Decision Record (ADR)

#### Title: 006 Valg af container orkestrering

#### Date: 2024-08-19

---

## Status

Godkendt

## Kontekst

Vores cloud-infrastruktur har trods manglende fælles retningslinjer centreret sig om containere - derfor er det oplagt at IDP som noget af det første fokuserer på container drift - vi skal i IDP regi beslutte, hvordan vi ønsker at drive container infrastruktur. 

## Beslutning

Brug EKS (AWS managed Kubernetes) som containeradministration og samtidig potentielt fundament for vores udviklings platform. I valget af EKS fremfor ECS er der lagt særligt vægt på at:

1. Fleksibilitet og Portabilitet: Kubernetes kan køre på enhver cloud eller lokal infrastruktur og undgår leverandørbinding.

2. Stærkt Økosystem: Kubernetes har et meget stort community og et rigt udvalg af værktøjer og services, og forventes at kunne tiltrække kandidater i højere grad.

3. IAC-platform: Mulighed for at bruge kubernetes som infrastructure as code platform, og dermed opnå mulighed for cloud agnostisk gitops infrastruktur.

Kubernetes er således en mere omfattende og fleksibel løsning til vores projekt.

Kubernetes understøtter vores [manifest](https://github.com/jppol-idp/internal-developer-platform/wiki/manifest) hvor hurtig onboarding og fokus på developer experience er central, ved at kunne stille et så komplet som muligt udviklingsmiljø til rådighed for udviklerne.

## Konsekvenser

1. Flere tekniske udfordringer med kubernetes selv og tilhørende komponenter i en multi-tenant struktur, herunder logging, overvågning, deployment, omkostningsstyring, namespace isolering.

2. Vi har ikke pt folk nok med med erfaring i Kubernetes og IDP, og der vil være en stejl læringskurve for at opbygge og drifte platformen.

3. Prioritering af container teknologi frem for serverless: Vi fokuserer i første omgang på containere, hvilket nødvendigvis betyder at serverless ikke prioriteres endnu.

## Mere kontekst

Vores tilgang til administration og ejerskab af infrastruktur i DUT, herunder EB, JP, Politiken, Bold, Holdet samt Koncernens fællesfunktioner, har udviklet sig over tid og ført til følgende:

- Ineffektiv brug af infrastruktur pga. historisk uenighed om teknologivalg og manglende fælles retningslinjer
- Betydelig variation i deployment, overvågning og administration af lifecycle på tværs af produkter
- Legacy infrastruktur og teknisk gæld tynger eksisterende teams, forhindrer innovation og produktivitet

Givet det nuværende teknologilandskab inden for DUT, ønsker vi en containeradministrationsplatform, der på sigt kan understøtte en bred vifte af applikationer, fra "moderne" cloud-native [12-faktor applikationer](https://12factor.net) til "legacy" stateful monolitiske applikationer, potentielt omfattende både Linux- og Windows-baserede applikationer.

Der er præcedens for brug af Kubernetes inden for DUT, da AI og EB teams har bygget deres platforme på Kubernetes.   
Der er også præcedens for brug af ECS inden for DUT, da JP og koncernen har bygget deres platforme på ECS.

## Alternativer

Der eksisterer flere produkter, der specifikt fokuserer på at køre og administrere containere i produktion:

- Cloud Managed Kubernetes Providers
  - AWS EKS
  - Google GKE
  - Azure AKS
  - Digital Ocean Kubernetes
  - Redhat OpenShift
  - GitLab Kubernetes
- AWS ECS (native AWS container orchestrator)
- AWS Fargate (native AWS serverless container orchestrator, runs on eks and ecs)
- Docker Swarm (simple, built-in to Docker, but less feature-rich than Kubernetes)
- CloudFoundry (PaaS, now runs on top of kubernetes)
- Hashicorp Nomad (apparently dead)
- Apache Mesos (mere kompleks end Kubernetes, og ikke så populær)

Fra ovenstående liste af produkter er Kubernetes den klare markedsleder og understøtter både applikationer og infrastrukturbehov. Kubernetes har følgende fordele:

- Stor adoption - allerede siden 2017 etableredes Kubernetes som facto industristandard
- Der findes managed Kubernetes-tjenester fra alle større cloud providere
- Bredt økosystem af understøttende værktøjer og teknologier
- Øget støtte til Kubernetes som implementeringsmål for kommercielle og open-source softwareprojekter
- Kubernetes er en populær teknologi, mange udviklere har erfaring med det, hvilket er vigtigt ifbm ekruttering og fastholdelse

### AWS ECS (Elastic Container Service)

  - Kan nemt integreres med andre AWS-tjenester såsom ALB, API Gateway, Security Groups, NACLs osv.
  - Ingen separate control plane omkostninger som ved EKS.
  - Lettere at administrere for rene applikationscontainer-skaleringer.
  - Mindre støttet i det bredere økosystem af værktøjer og teknologier sammenlignet med Kubernetes.
  - Begrænset til AWS, hvilket reducerer platformens agnostiske karakter.
  - Utilstrækkelig for drift af mere eksotisk software via operators.

### Docker Swarm

  - Indbygget i Docker, nem at sætte op og administrere.
  - God for simple container-koordineringsbehov.
  - Mangler mange af de avancerede funktioner og skaleringsmuligheder, som Kubernetes tilbyder.
  - Mindre community og økosystem sammenlignet med Kubernetes.
  - Ikke velegnet for komplekse og skalerbare produktionsmiljøer.

### On-Premises Løsning

  - Fuldstændig kontrol over hardwaren og softwaremiljøet.
  - Kan være økonomisk fordelagtigt ved meget store workloads.
  - Højere kapitalomkostninger og driftsomkostninger.
  - Reduceret skalerbarhed og fleksibilitet sammenlignet med cloud-løsninger.
  - Kræver dedikerede ressourcer til vedligeholdelse og administration.
  - Kan integreres i ECS/EKS Anywhere for hybrid løsning.

### CloudFoundry PaaS

  - Kører på toppen af Kubernetes og bringer PaaS funktionaliteter.
  - God til udviklerproduktivitet og hurtig applikationsudrulning.
  - Komplekst at administrere i store skalaer.
  - Mindre fleksibilitet i forhold til Kubernetes for specifikke tilpassede behov.

