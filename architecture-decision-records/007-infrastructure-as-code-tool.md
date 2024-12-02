### Architecture Decision Record (ADR)

#### Title: 007 GitOps og Infrastruktur som kode

#### Date: 2024-07-03

---

## Status

Forslag

## Kontekst

For at opnå bedst mulig administration af vores platform, ønsker vi at benytte [gitops](https://www.gitops.tech) i kombination med infrastruktur som kode (IaC). Vi skal vælge, om vi ønsker at implementere Infrastructure as Code (IaC) ved brug af Kubernetes-native løsninger eller tradionelle værktøjer. Dette valg vil påvirke vores deployment-strategi, automation, og administration af drift.

 Følgende produkter/teknologier er relevante i denne kontekst:

- **Crossplane**: Kubernetes-native IAC. Understøtter vores målsætning om at implementere et GitOps baseret workflow, hvor som helst - dog er Crossplane er en ukendt teknologi i jppol.
- **AWS Controllers for Kubernetes (ACK)**: Kubernetes-native IAC. Tæt integration med AWS-økosystemet, og dermed skræddersyet til specifikke applikationer og underliggende infrastruktur.
- **Kubernetes Operators**: Skræddersyede controllers til at automatisere styring af applikations-specifikke ressourcer.
- **Terraform**: Agnostisk IAC-værktøj. Sammen med CDK er TF velkendt og vi har en del kompetencer in-house.
- **OpenTofu**: CNCF støttet opensource drop-in replacement version af Terraform v1.6 
- **AWS Cloud Development Kit (CDK)**: IAC framework for at definere AWS cloud resources vha. programmerings-sprog. Velkendt in-house
- **Pulumi**: IAC-værktøj, der bruger almindelige programmeringssprog og kan understøtte Kubernetes.

## Beslutning

**OpenTofu** fremstår organisatorisk robust med potentiale for bedre funktionalitet, da det ikke er bundet af behovet for at konkurrere med et kommercielt produkt.
**Crossplane** understøtter via kubernetes gitops workflow til at orkestrere applikationer og infrastruktur hvor som helst.

## Konsekvens

Vores eksisterende værktøjer, Terraform og CDK, fravælges fremadrettet, men kan potentielt fortsat bruges under særlige omstændigheder som [crossplane providers](https://marketplace.upbound.io/providers/upbound/provider-terraform/v0.3.0) eller i forbindelse med fx cold-starts.





