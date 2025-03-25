# 000 Registrering af beslutninger

Dato: 2024-04-29

## Status

Godkendt

## Kontekst

Mens vi bygger IDP platformen vil vi træffe fælles beslutninger om grundlæggende arkitektur, processer, services og værktøjer.

For at huske hvorfor vi har truffet disse beslutninger, og samtidig sikre en transparant beslutnings process, bør vi registrere disse beslutninger.

Som skitseret i vores IDP designprincipper, bør disse være offentligt tilgængelige, da åbenhed skaber ansvarlighed, transparens, sammenhæng og fællesskab.

Samtidig kan disse dokumenter fungere som reference dokumentation for nye team medlemmer eller andre der måtte have interesse.

## Beslutning

Vi vil bruge Architecture Decision Records, som beskrevet af Michael Nygaard i artiklen [Documenting architecture decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)   
Dokumentation af vores ADR process er beskrevet i vores [wiki](https://github.com/jppol-idp/internal-developer-platform/wiki/architect-decision-records)

## Konsekvenser

1. ADR arkivet bør være let tilgængelig, fx i platformens Git repository.
1. Pull requests medfører en velkendt review process og er en naturlig del af udviklernes workflow.
1. Én ADR beskriver én væsentlig beslutning for en bestemt service - noget der har betydning for hvordan hele platformen drives.
1. Konsekvenserne af én ADR vil med stor sandsynlighed blive konteksten for efterfølgende ADRs.
1. Motivationen bag tidligere beslutninger er synlig for alle, nu og i fremtiden.
1. Når gamle beslutninger ændres vil ændringerne fremgå i platformens kontekst, også selvom team struktur og organisation ændrer sig over tid.
1. Det letter kommunikationen på tværs af teams ved at give en klar forklaring på, hvorfor bestemte beslutninger blev truffet.

