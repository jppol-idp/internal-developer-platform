### Architecture Decision Record (ADR)

#### Title: 010 Valg af Fælles Artifact Repository

#### Date: 2024-07-03

---

## Status

Forslag

## Kontekst

Vi overvejer valg af fælles repository til håndtering af Docker images. Dette valg vil påvirke vores build-, deployment- og release-processer. Fire primære muligheder er relevante: Docker Hub, Amazon Elastic Container Registry (ECR), GitHub Container Registry (GHCR), Google Container Registry (GCR), Azure Container Registry (ACR), og selv-hostede løsninger som Harbor.

### Beslutning

Vi vil benytte **Amazon Elastic Container Registry (ECR)** som vores primære Container repository. Dette valg er baseret på følgende årsager:
   - Giver en problemfri integration med vores eksisterende AWS-infrastruktur, såsom ECS, EKS, og IAM.
   - Understøttelse af IAM roller og politikker giver granular adgangskontrol.
   - ECR håndterer automatisk skalering og kapacitet, hvilket sikrer, at vi ikke møder kapacitetsbegrænsninger.
   - Betalingsmodellen baseret på brugt lagerplads og datatransport er økonomisk fordelagtig for vores anvendelsestilfælde.

## Hybrid Løsning

Selvom ECR bliver vores primære repository, er der muligvis noget at hente ved at bruge github, hvis vi lægger os fast på github enterprise cloud som fælles code repository.


## Overvejelser

### Docker Hub

   - Udviklerfællesskabets førstevalg, hvilket betyder brede integrationsmuligheder med mange CI/CD-værktøjer.
   - Tilbyder både offentlige og private repositories, hvilket giver fleksibilitet afhængigt af brugsscenariet.
   - God tilgængelighed og ydeevne på tværs af geografier på grund af global CDN.
   - Begrænsninger på antallet af push/pull-kommandoer for gratis brugere, hvilket kan påvirke CI/CD pipelines.
   - Selvom sikkerheden er forbedret, er der stadig bekymringer omkring sikkerhed og mulige brud.
   - Private repositories kræver betalte planer, som kan være dyre ved storskala brug.

### Amazon Elastic Container Registry (ECR)

   - Tæt integration med AWS tjenester som ECS, EKS, og IAM, hvilket forenkler det samlede setup.
   - Understøtter IAM roller og politikker for adgangskontrol, hvilket giver stærke sikkerhedsfunktioner.
   - Håndterer autoskalering og lagerplads, så du ikke skal bekymre dig om kapacitetsgrænser.
   - Betal for brugt lagerplads og datatransport, hvilket kan være omkostningseffektivt ved stor skala.
   - Er tæt bundet til AWS, hvilket kan begrænse fleksibilitet ved multi-cloud eller hybrid-cloud strategier.
   - Kan kræve mere konfiguration og opsætning sammenlignet med Docker Hub.

### GitHub Container Registry

   - Nem integration med GitHub repositories og GitHub Actions, hvilket forenkler CI/CD workflows.
   - Understøtter flere package formater herunder Docker images, npm, Maven, nuget, og RubyGems.
   - GitHub's sikkerhedsfunktioner og adgangskontrol kan anvendes til repositories.
   - Tilbyder både offentlige og private repositories, hvilket gør det nemt at dele artifacts internt og eksternt.
   - Private repositories kræver GitHub's betalte planer, hvilket kan være en omkostningsfaktor ved omfattende brug.
   - Begrænsninger på API-anmodninger som kan påvirke pipelines ved intensiv brug.
   - Tæt bundet til GitHub økosystemet, hvilket kan være en ulempe hvis der på sigt skal bruges andre VCS providers.

### Google Container Registry (GCR)
   - Integrerer tæt med Google Cloud Platform, hvilket forenkler brugen med GKE og andre GCP-tjenester.
   - Konkurrencedygtige priser og betalingsmodel baseret på lagerplads og dataoverførsel.
   - Kan føre til binding til GCP's økosystem.

### Azure Container Registry (ACR)
   - Optimeret til brugere af Azure tjenester, integreres godt med AKS, Azure DevOps osv.
   - Stærke sikkerhedsfunktioner og compliance muligheder.
   - Tæt afhængig af Azure platformen.

### Selv-hostede løsninger (som Harbor)
   - Giver fuld kontrol over data og konfiguration af repositories.
   - Mulighed for høj sikkerhed og compliance tilpasset virksomhedens behov.
   - Kræver dedikerede ressourcer til opsætning, vedligeholdelse og drift.


