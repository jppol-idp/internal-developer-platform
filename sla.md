---
title: SLA
nav_order: 1
permalink: /sla/
domain: public
layout: sla
last_reviewed_on: 2026-10-14
review_in: 12 months
---

# Service Level Agreement (SLA)

**Version 2.0.0**

Her er en oversigt over de SLA'er (Service Level Agreements), som IDP-teamet stiller til rådighed for jer, kunden.

SLA'en gælder for brug af services placeret i IDP-cluster.

## Prioriteter

| | Normal | Lav |
|---|---|---|
| **Beskrivelse** | • Standardaftalen til **PROD**, som dækker services i produktion. | • Til **DEV**- og **TEST**-miljøer, som har lille påvirkning på organisationen, hvis de er nede. |
| **Overvågning af platformen** | • IDP-teamet overvåger alarmer kl. **08.30-16.30** på hverdage.\* | • *Samme som* **Normal** |
| **Support** | • Support via jeres `#idp-team-slack-kanal` kl. **08.30-16.30** på hverdage.\* | • Support via jeres `#idp-team-slack-kanal` kl. **10-15** på hverdage.\* |
| **Generelt om incidents** | • Metrikker og alarmer opsættes for jeres services, som I selv håndterer, før I eventuelt kontakter os.<br>• Vi tilstræber altid at kommunikere større nedbrud i de relevante `#idp-slack-kanaler`. Vi håber, I vil gøre det samme. | • *Samme som* **Normal** |
| **Kritiske incidents** | • Kritiske incidents besvares kl. **08.30-16.30** på hverdage.\*<br>• Kritiske incidents oprettes af jer via incident.io-formularen (via Slack).<br>• Processen for kritiske incidents køres via incident.io og er synlig i Slack. I tilfælde hvor servicedesk er involveret, sørger vi også for at kommunikere i Teams.<br>• Responstid: inden for 15 min<br>• Påbegynder løsning: så hurtigt som muligt - inden for 60 min | • *Samme som* **Normal** |
| **Ikke-kritiske incidents** | • Ikke-kritiske incidents oprettes i jeres `#idp-team-slack-kanal` eller via incident.io-formularen og besvares kl. **08.30-16.30** på hverdage.\* | • Incidents oprettes i jeres `#idp-team-slack-kanal` eller via incident.io-formularen og besvares kl. **10-15** på hverdage.\* |

\* Gælder ikke helligdage.

## Definition: Hvad er en kritisk alarm i IDP-kontekst?

En kritisk alarm er enhver hændelse i IDP-platformen, hvor:

- **Brugere mister adgang til at deploye, bygge eller køre workloads.** Platformen leverer så ikke længere sit kerneprodukt: "bring a container to life".
- **Produktionstrafik for teams er påvirket** i en grad, hvor kundeoplevelsen forværres målbart, fx nedetid, alvorligt forhøjet fejlrate eller services, der ikke skalerer.
- **Platformens kontrolplane eller GitOps-flow ikke fungerer**, fx hvis Argo CD er nede, GitOps-synkronisering fejler, ECR-push er brudt, eller Kubernetes API er utilgængeligt.
- **Sikkerhed er kompromitteret, eller der er høj risiko for kompromittering**, fx hvis secrets eksponeres, uautoriseret adgang er muligt, eller der er kritiske CVE'er i platformens fundamentale komponenter.
- **Datatab eller risiko for permanent datatab**, fx hvis Aurora failover ikke sker, RW-volumes ikke mountes, S3-politikker utilsigtet giver adgang, eller EBS-volumes fejler.
- **Observability er helt eller delvist utilgængelig.** Når metrics eller logs ikke længere leveres, bliver platformen "blind", hvilket øger risikoen for cascading failures.

## Ansvar og drift

| | Normal | Lav |
|---|---|---|
| **Compliance og GDPR** | • Kunden har det fulde ansvar for alle data, der behandles af deres egne services, applikationer og databaser.<br>• Det er udelukkende kundens eget ansvar at sikre og dokumentere, at deres løsninger overholder GDPR, databehandleraftaler og øvrig relevant lovgivning.<br>• Det er kundens ansvar at sikre JP/POLs brugeres ret til indsigt i den data, I har om dem, jf. GDPR art. 15.<br>• IDP-teamet er ansvarligt for, at den underliggende platforminfrastruktur, som kunderne benytter, drives i overensstemmelse med relevante databeskyttelseskrav.<br>• Al data, der håndteres af IDP, lagres i AWS-datacentre i EU. | • *Samme som* **Normal** |
| **Sikkerhed** | • Kunden er ansvarlig for sikkerheden i de løsninger, de selv udvikler, deployer og drifter på platformen.<br>• IDP-teamet er ansvarligt for sikkerheden i selve platformen og den underliggende infrastruktur.<br>• Alle IDP's kundevendte applikationer benytter JP/POL Entra SSO. | • *Samme som* **Normal** |
| **Databaser** | • Vi anbefaler brug af en managed database service.<br>• IDP tilbyder DynamoDB og en managed Aurora Postgres-database, som vi står for.<br>• Opgraderinger af databaser sker automatisk ved mindre opdateringer. Ved major versions med breaking changes informerer vi minimum 30 dage før og planlægger sammen med jer.<br>• Vi fraråder og supporterer ikke databaser inde i clusteret. Hvis I ønsker det, står I selv for det. | • *Samme som* **Normal** |

## Backup, data retention og restore af data

| | Normal | Lav |
|---|---|---|
| **EBS** | • IDP står for backup af virtuelle diske (EBS-volumes), hvis de er defineret som persistente.<br>• Backup af EBS køres én gang i døgnet, og vi gemmer de sidste 5 uger. | • *Samme som* **Normal** |
| **PostgreSQL (Aurora)** | • IDP står for backup af Aurora Postgres-databaser leveret af IDP.<br>• Backup af PostgreSQL-produktionsdatabaser køres én gang i døgnet, og vi gemmer de seneste 35 daglige kopier.<br>• IDP laver ikke backup af jeres eventuelle egne databaser i clusteret. | • *Samme som* **Normal**<br>• Dog kun 7 dages backup af PostgreSQL-databaser i staging-, test- og dev-miljøer. |
| **DynamoDB** | • IDP står for backup af DynamoDB-databaser leveret af IDP.<br>• Backup af DynamoDB gemmes som point-in-time-gendannelse (PITR), og vi gemmer de seneste 35 dage. Det gør det muligt at gendanne til et hvilket som helst tidspunkt inden for de seneste 35 dage. | • *Samme som* **Normal** |
| **Applikationslogs** | • Applikations-logfiler gemmes i 30 dage for at sikre GDPR-compliance.<br>&emsp;◦ Hvis I har brug for data i mere end 30 dage, og det er godkendt af jura, kan I kontakte os, så vi kan justere retention for jer. Alternativt kan I lagre data i en IDP-managed Postgres-database med egen applikationsstyret retention. Så kan I slette personoplysninger, når I modtager sletteanmodninger fra JP/POLs brugere, jf. GDPR art. 17. | • *Samme som* **Normal** |
| **Container images (ECR)** | • Container images i ECR, der er ældre end 90 dage og samtidig ikke er blevet pulled i 90 dage, bliver arkiveret. De ligger i arkivet i 90 dage, før de slettes endeligt.<br>• Untaggede container images i ECR slettes generelt efter 30 dage. | • *Samme som* **Normal** |
| **S3** | • Der tages ikke backup af S3, og versionering er ikke slået til. | • *Samme som* **Normal** |

## Omkostninger og fakturering

| | Normal | Lav |
|---|---|---|
| **Omkostninger og fakturering** | • Afregning til kundens afdeling er baseret på faktisk forbrug, hvis I er placeret på jeres eget cluster.<br>• Hvis I er placeret på et delt cluster med andre teams uden for jeres afdeling, bliver omkostningen afholdt af DUT. Det er planlagt at ændre dette, når vi har en afregningsmetode. | • *Samme som* **Normal** |
| **Opsigelse, ændringer og fornyelse** | • Aftalen kan ændres og opsiges med 30 dages varsel.<br>• Afregningsmetoden kan ikke ændres uden aftale. | • *Samme som* **Normal** |

## Standardaftaler over individuelle aftaler

For at gøre livet lettest for alle ønsker vi, at alle benytter de standardaftaler, vi har. Hvis der er behov for en ændring, bliver den rullet ud til alle, så alle kører på den nyeste aftale.

## Ændringer til aftalen

Vi informerer jer altid om opdateringer i aftalen. I godkender automatisk aftaleopdateringer, medmindre I aktivt vælger at afvise dem.

Ved større ændringer sørger vi selvfølgelig for at inddrage jer i processen.

Typiske opdateringer vil være ved opgraderinger af IDP.

## Kommunikation og gennemsigtighed

Vi tilstræber at være transparente og melder opdateringer og større nedbrud ud i de relevante `#idp-slack-kanaler`. Vi håber, I også vil følge det eksempel.

## Early Life Support

Før SLA'en træder i kraft, vil der være en "early life support"-fase, hvor vi sammen med jer analyserer jeres service i produktion. Her kan vi lære, justere og blive klogere på, hvilke metrikker der skal opsættes.

Vi aftaler med jer, hvornår "early life support"-fasen er slut.

## Versionering

Vi følger semantisk versionering. Et versionsnummer som 1.2.3 betyder:

- **1** = Major (store ændringer, bagudkompatibilitet brudt)
- **2** = Minor (nye funktioner, bagudkompatibel)
- **3** = Patch (fejlrettelser)

---

## Bilag A: Undtagelser fra standardaftalen

{% comment %}
TODO: Afklar om KOA's 60 dages log-retention gælder hele KOA's prod-tenant eller kun ét namespace.
documentation/log-retention-and-deletion.md beskriver præcedensen som 60 dage på ét enkelt namespace
(juridisk journalisering). Ret formuleringen nedenfor, så den passer, og fjern denne kommentar.
{% endcomment %}

{: .note }
> Standardaftalen ovenfor gælder for alle kunder. Her står de få **undtagelser**, der er aftalt med enkelte kunder. Står en kunde ikke nedenfor, gælder standardaftalen uændret.

### KOA

- **Log-retention i produktion:** 2 måneder i stedet for de 30 dage, der er standard.
