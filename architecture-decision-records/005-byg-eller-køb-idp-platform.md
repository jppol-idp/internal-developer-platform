### Architecture Decision Record (ADR)

#### Title: ADR 005 Byg en IDP-platform eller køb en eksisterende

#### Dato: 2024-08-15

---

## Status

Forslag

## Kontekst

Beslutningen om at bygge en IDP selv eller bruge en eksisterende løsning eller framework involverer først en vurdering af vores behov, se [IDP Manifest](https://github.com/test-jppolitikenshus/internal-developer-platform/wiki/Manifest) og [FAQ](https://github.com/test-jppolitikenshus/internal-developer-platform/wiki/FAQ), samt vurdering af tilgængelige produkter:

**rig.dev**:
- **Helmchart-generator**: Automatiserer og forenkler generering af Helm Charts til Kubernetes.
- **Multi-cluster interface**: Centraliseret grænseflade til styring og overvågning af flere Kubernetes-klynger.
- **Multi-tenant cluster**: Understøtter isoleret ressource- og applikationsstyring for forskellige brugere/teams inden for den samme klynge.

**otomi.io, kratix.io, cycloid.io og quory.io**:
- Disse tilbyder en self-service platform, der enten understøtter eller integrere med Kubernetes.
- Otomi er købt af akamai for nylig

**cnoe.io, backstack.dev**
- Disse samler opensource og CNCF værktøjer i en "let" tilgængelig pakke.

## Beslutning




(Detaljer om den endelige beslutning, når denne er truffet)

## Alternativer

(Listning af mulige alternativer, der kan overvejes):  
https://platformengineering.org/platform-tooling
