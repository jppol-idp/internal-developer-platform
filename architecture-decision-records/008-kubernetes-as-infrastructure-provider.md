### Architecture Decision Record (ADR)

#### Title: 008 Kubernetes som infrastruktur provider

#### Date: 2024-07-03

---

## Status

Forslag

## Kontekst

Vi skal vælge i hvor høj grad vi ønsker at levere vores infrastruktur services i Kubernetes eller med cloud-leverandørernes indbyggede tjenester (ex postgres). Dette valg påvirker vores driftsstrategi, administration og udviklingscyklus. Vi ønsker at vurdere fordelene og ulemperne ved begge tilgange og overveje, hvordan en hybrid løsning effektivt kan realiseres.

## Overvejelser

### Fordele ved at bruge Kubernetes Services
   - Med Kubernetes kan vi potentielt nemt **replikere produktionsmiljøer** for udviklings- og testformål, hvilket fremmer hurtigere fejlfinding og produktudvikling.
   - Integration med CI/CD pipelines er ligetil med Kubernetes, hvilket fremmer **automatiseret deployment** og øger hastigheden på udviklingslivscyklusser.

### Fordele ved at bruge Cloud Services
   - Cloud-leverandørernes tjenester som RDS (Managed Databases), EBS (Elastic Block Store), EFS (Elastic File System), S3 (Object Storage), SQS (Simple Queue Service), SNS (Simple Notification Service) og Secret Manager tilbyder **specialiseret funktionalitet, ydeevneoptimering og management**.
   - Anvendelse af managed services **reducerer operational overhead** ved at vedligeholde og opdatere systemerne, hvilket frigør ressourcer og reducerer risiciene.
   - Mange cloud-leverandører tilbyder certificerede **indbyggede sikkerheds- og compliance-funktioner**, hvilket kan være mere tidseffektivt end at skabe disse fra bunden i Kubernetes.
   - Cloud-tjenester er optimeret og skaleret til **høj ydeevne og belastning**, hvilket kan være svært at matche med selv-administrerede systemer.

## Hybrid Løsning

En hybrid løsning kan måske realiseres ved at kombinere de bedste elementer fra begge verdener - fx via produkter som localstack, score, eller infrastruktur kode kan skrives til at forholde sig til miljøet.
   
## Opsummering

Vi vil løbende tage stilling til balancen mellem at drive services som cloud-native og kubernetes-native.*Dette her synes jeg er den mest centrale beslutning lige nu. Jeg hører det som om vi er enige om Kubernetes osv. Men også at vi i temmelig høj grad kommer til at have en hybridløsning, for at få mest muligt ud af AWS.*
