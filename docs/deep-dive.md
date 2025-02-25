# IDP deep-dive 

udkast


## Idealer

> Vores idealer er ultimative designs. De er måske ikke hensigtsmæssige at virkeliggøre, men beskriver scenarier med betydelige fordele som vi ønsker at forholde os til løbende, fx:

- **Al funktionalitet er tilgængelig i Kubernetes**  
  Dette indebærer, at alle systemer og applikationer kan fungere inden for Kubernetes økosystem. Det sikrer ensartethed og forenkler administration og skalerbarhed.
  
- **Al funktionalitet udstilles, og konfigureres, via Kubernetes API**  
  At kunne konfigurere og tilpasse alle aspekter af systemet gennem Kubernetes API'en maksimerer automatisering og effektivitet, hvilket reducerer behovet for manuelle indgreb.
  
- **Al funktionalitet kan selvbetjenes af udviklerne**  
  Selvbetjening fremmer udviklerproduktivitet ved at gøre det muligt for dem at udnytte Git, grafiske brugerflader (GUI) og kommandolinjegrænseflader (CLI) til deres arbejde uden direkte afhængighed af systemadministratorer.

- **Alle services fra alle cloud providere kan potentielt provisioneres**  
  Denne fleksibilitet giver mulighed for at vælge og benytte de bedste cloud-tjenester fra enhver udbyder baseret på specifikke behov og præferencer. Det øger mulighederne for optimering af omkostninger, ydeevne og funktionalitet.

<img width="994" alt="Screenshot 2024-06-10 at 14 08 50" src="https://github.com/user-attachments/assets/762005c2-6770-408b-b4ab-841a87a3b89b">

## Målsætninger

> Vores målsætninger definerede mål med indbyggede succes kriterier, fx:

- **Let tilgængeligt udviklingsmiljø**  
  Udviklingsmiljøet skal være klart defineret, let at sætte op og bruge for alle udviklere, hvilket minimerer frustration og reducerer tid til produktivitet.

- **Gyldne stier & Standardisering**  
  Definere og implementere standardiserede arbejdsmetoder og værktøjer, der gør det nemmere for udviklere at følge bedste praksis og sikre konsistens på tværs af projekter.

- **Hurtig onboarding**  
  Onboarding processen for nye udviklere skal være effektiv og hurtig, så de kan begynde at bidrage til projekter inden for kort tid. Dette kan opnås ved at have dokumenterede procedurer og automatiserede processer.

- **Fra kode til deploy på 30 minutter**  
  Sikre at hele workflowet fra at skrive kode til at deploye i produktion tager maksimalt 30 minutter. Dette involverer automatisering af build, test og deploy processer for at forøge hastighed og reducere risiko for fejl.

- **Effektiv fejlsøgning på tværs af services**  
  Implementere værktøjer og metoder, der gør det muligt for udviklere og operationelle teams at effektivt diagnosticere og løse problemer, uanset hvilken service de opstår i. Dette inkluderer centraliseret logging, tracing og monitoring.

- **Indbygget sikkerhed og observability**  
  Sikkerhed og observability skal være integreret i alle dele af udviklings- og driftsprocesserne. Dette omfatter automatiserede sikkerhedstests, kontinuerlig overvågning og alarmering for at sikre systemernes integritet og ydeevne.

[![Diagram](https://github.com/test-jppolitikenshus/internal-developer-platform/blob/main/architecture-decision-records/img/idp_diagram.png)](https://raw.githubusercontent.com/test-jppolitikenshus/internal-developer-platform/main/architecture-decision-records/img/idp_diagram.png)

## Principper

> Vores design principper er overordnede retningslinjer der ligger til grund for de beslutninger vi tager, fx:

- **Developer Experience**  
  Fokus på at skabe en brugervenlig og produktiv oplevelse for udviklere ved at sikre, at de har adgang til de nødvendige værktøjer og ressourcer for at udføre deres arbejde effektivt.

- **Painpoints & Feedback Loops**  
  Aktivt identificere og adressere smertepunkter gennem kontinuerlig feedback fra brugerne. Dette hjælper med at skabe en iterativ forbedringsproces, hvor udviklernes oplevelser bruges til at forbedre platformen løbende.

- **Self-Service**  
  Tilbyde selvbetjeningsmuligheder, så udviklere selv kan udføre nødvendige opgaver uden afhængighed af andre teams. Dette fremmer hurtigere workflows og øger udviklerens autonomi.

- **GitOps**  
  Anvende GitOps-principper ved at håndtere al infrastructure-as-code og applikationskode gennem Git repositories. Dette sikrer versionering, sporbarhed og automatiserede deployments, hvilket øger både sikkerhed og hastighed.

- **Open Source**  
  Fremme brugen af og bidrag til open source-projekter for at udnytte fællesskabets innovationer og ressourcer og reducere afhængigheden af proprietære løsninger. Dette bidrager samtidig til et større økosystem og samarbejde.

- **End-to-end Observability**  
  Implementere avancerede overvågnings- og logningsværktøjer for fuld synlighed i hele systemet fra udvikling til produktion. Dette gør det muligt hurtigt at identificere og løse problemer, hvilket sikrer stabil drift og hurtig fejsøgning.

- **Golden Paths & Standardisation**  
  Definere og etablere "gyldne veje" og standarder for udvikling, build, test og deploy-processer. Dette sikrer konsistens, kvalitet og effektivitet på tværs af alle projekter, making best practices let tilgængelige for alle udviklere.

## Teknologier

> Centrale teknologier vi agter at bruge som fundamentale ingredienser i IDP, og som løbende bliver opdateret på vores [teknologi radar](https://test-jppolitikenshus.github.io/techradar/)

- **GitHub.com**  
  Bruges som central repository for al kildekode, versionering og samarbejde i hele DUT.
  
- **GitHub Actions**  
  Automatisering af workflows som Continuous Integration (CI) og Continuous Deployment (CD).

- **Kubernetes**  
  Platform for orkestrering af containeriserede applikationer, som sikrer skalerbarhed og effektiv ressourceudnyttelse.

- **Containers**  
  Brug af container-teknologier som Docker til at sikre konsistente miljøer fra udvikling til produktion.

- **ArgoCD**  
  Helm Chart: [ArgoCD Helm Chart](https://github.com/argoproj/argo-helm/tree/main/charts/argo-cd)  
  Værktøj til GitOps-baseret Continuous Deployment til Kubernetes.
  
- **AWS**  
  Vores fortrukne infrastruktur leverandør.

- **PostgreSQL**  
  Relationsdatabase valgt for dens alsidighed, avancerede funktioner og omkostningseffektivitet.

- **Crossplane**  
  Dokumentation: [Crossplane Install Guide](https://docs.crossplane.io/latest/software/install/)  
  Multi-cloud control-plane til at administrere cloud-ressourcer via Kubernetes API.

  - **Crossplane Provider AWS**  
    Installation: [Provider AWS](https://marketplace.upbound.io/providers/upbound/provider-family-aws/v1.8.0)  
    
  - **Crossplane Provider AWS EKS**  
    Installation: [Provider AWS EKS](https://marketplace.upbound.io/providers/upbound/provider-aws-eks/v1.8.0)

- **Backstage**  
  Helm Chart: [Backstage Helm Chart](https://github.com/backstage/charts)  
  Platform til etablering af udviklerportaler, der forbedrer overblik og adgang til services og værktøjer.

- **Grafana**  
  Helm Chart: [Grafana Helm Chart](https://github.com/grafana/helm-charts)  
  Dashboarding-værktøj til at visualisere metrics og log data.

- **OpenTelemetry**  
  Helm Chart: [OpenTelemetry Helm Chart](https://github.com/open-telemetry/opentelemetry-helm-charts)  
  Observability-framework til at samle sporingsdata, logning og metrics.

- **Falco**  
  Helm Chart: [Falco Helm Chart](https://github.com/falcosecurity/charts)  
  Open source værktøj til at opdage og respondere på trusler i realtid.

- **Trivy**  
  Dokumentation: [Trivy CLI Scanning](https://aquasecurity.github.io/trivy/v0.28.1/docs/kubernetes/cli/scanning/)  
  Open source sikkerhedsscanner til container images og filsystemer.

- **Kyverno**  
  Dokumentation: [Kyverno Documentation](https://kyverno.github.io/kyverno/)  
  Policy-engine til Kubernetes til at validere, mutere og håndhæve konfigurationer.

- **SPIRE / SPIFFE**  
  Helm Chart: [SPIRE Installation](https://spiffe.io/docs/latest/spire-helm-charts-hardened-about/installation/)  
  Framework til administration af tjenesteidentiteter.

- **Cilium**  
  Dokumentation: [Cilium Installation](https://docs.cilium.io/en/stable/installation/k8s-install-helm/)  
  Netværk og sikkerhed på container-niveau for Kubernetes.

- **Istio**  
  Dokumentation: [Istio Installation](https://istio.io/latest/docs/setup/install/helm/)  
  Service mesh der sikrer reliable, sikre og observable mikrotjenester.

- **Karpenter**  
  Dokumentation: [Karpenter Getting Started](https://karpenter.sh/v0.37/getting-started/getting-started-with-karpenter/)  
  Automatisk skalering af Kubernetes nodes baseret på applikationsbehov.


## Support og Tooling

> IDP-teamet stiller support og tooling til rådighed

- **jppol-cli**  
  [Why you should write a CLI tool for your org](https://surminus.com/blog/why-you-should-write-a-cli-tool-for-your-org/)
  
  CLI-værktøj udviklet til at forenkle og strømligne processer inden for organisationen.

- **Tech Radar**  
  [Tech Radar Plugin](https://backstage.io/blog/2020/05/14/tech-radar-plugin/)
  
  Et værktøj til at visualisere og spore teknologivalg og deres evolution over tid, bygget på Backstage-platformen.

- **Software Templates**  
  [Software Templates](https://backstage.io/docs/features/software-templates/)
  
  Skabeloner til at skabe nye projekter og tjenester hurtigt og konsistent ved hjælp af Backstage.

- **GitOps**  
  [Rethinking GitOps: Moving Beyond Branch-Based Deployment](https://akkireddy.medium.com/rethinking-gitops-moving-beyond-branch-based-deployment-4605f078ef0e)
  
  En tilgang til Continuous Deployment centreret omkring Git repositories som "single source of truth" for infrastructure og applikationskode.

- **Slack som primær kommunikationskanal**  
  Slack bruges til daglig kommunikation, hurtige spørgsmål og svar samt teamkoordinering.

- **Mailgruppe til notifikationer**  
  En mailgruppe bruges til at sende vigtige notifikationer og opdateringer til teams.

- **Ugentlige teammøde referater**  
  Referater fra ugentlige teammøder distribueres for at sikre, at alle er opdaterede med de seneste beslutninger, fremskridt og næste skridt.


### Operationelle grænser

Teamet bevæger sig inden for kubernetes og AWS blabla... [ansvar](ansvar.md)

## Hvad er Internal Developer Platform (IDP) i Digital Udvikling & Teknologi ?

En fælles portal der skal gøre udviklere i stand til at bygge og vedligeholde deres applikationer i overensstemmelse med principperne for digital bæredygtighed (som beskrevet i [JP/Politikens Hus' strategi for 2024-2026](https://www.jppol.dk/strategi-2024-2026)).
Kort fortalt skal IDP'en minimere kompleksiteten for udviklerne ved at stille infrastruktur til rådighed med indbygget sikkerhed, observability, standardiserede workflows, support og selvbetjening.

## IDP'ens historie i JP/Politikens Hus.

Efter mange år med AWS vækst bliver IDP en del af en større strategi i forbindelse med etablering af DUT i 2024 for at skabe en mere bæredygtig og effektiv udviklingsproces, 
hjælpe med at reducere kompleksiteten og øge hastigheden på udviklingsprocessen.

## Hvad bruger man IDP til ?

IDP'en er beregnet til at i at give udviklere adgang til:

- Ensartet CI/CD workflow
- Ensartet konfiguration af infrastruktur
- Indbygget sikkerhed
- Mulighed for end-to-end observability
- Standardiserede teknologivalg, workflows og best practices
- Support
- Selvbetjening
- Kost kontrol

## Hvilke problemer løser IDP ?

IDP'en skal hjælpe med at løse følgende problemer:

- Sænke den kognitive load for udviklere
- Hurtigere onboarding af nye udviklere
- Fokus på lavere time to market
- Ensartede værktøjer og sikkerhedspraksis
- Fokus på transparens og vidensdeling

## Hvordan opnår IDP'en sine mål?

Ved initiativer der analyserer, kortlægger og dokumenterer epics og features, herunder:

- **Wardley Mapping**  
  [Kortlægning af strategiske positioner og bevægelser](https://learnwardleymapping.com/introduction/)  
  Bruges til at visualisere og analysere det strategiske landskab af organisationen, identificere muligheder og informere beslutningstagning.

- **Capability Mapping**  
  [Analyse af evner og kapaciteter i organisationen](https://acorn.works/enterprise-learning-management/capability-mapping)  
  Kortlægger organisationens eksisterende og nødvendige kapaciteter for at identificere styrker og svagheder og styre ressourceallokering.

- **Topology Mapping**  
  [Kortlægning af team- og service snitflader med brugerbehov](https://teamtopologies.com/key-concepts-content/exploring-team-and-service-boundaries-with-user-needs-mapping)  
  Analysere teamstrukturer og deres interaktioner for at optimere arbejdsflow og forbedre samarbejde og effektivitet.

- **Event Modelling**  
  [Visualisering af event-drevne systemer](https://eventmodeling.org/)  
  Bruges til at beskrive systemadfærd gennem sekvenser af events, hvilket hjælper med at designe og forstå komplekse systemer.

- **Logical Architecture**  
  Dokumentation af logiske komponenter såsom ADRs (Architectural Decision Records), capabilities, modeller, schemas og softwarekataloger. Dette sikrer en klar og systematisk forståelse af systemets design og rationaler bag beslutninger.

- **Physical Architecture**  
  Beskrivelse af teknologier, infrastruktur, sikkerhed, services og observability. Dette giver en detaljeret oversigt over de fysiske og tekniske krav og komponenter, der understøtter systemet.

- **Knowledge Architecture**  
  Opbygning af knowledge domains, learning paths, playbooks og undervisningsmaterialer for at sikre, at teamet har de nødvendige færdigheder og viden til at opnå succes. Dette fremmer en kultur af kontinuerlig læring og forbedring.

Disse initiativer skal sikrer at IDP er både strategisk og operationelt effektiv, og at alle mål bliver klart defineret, analyseret og opnået gennem en struktureret tilgang.

