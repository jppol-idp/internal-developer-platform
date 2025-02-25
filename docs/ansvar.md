# Ansvarsområder

IDP team bør vedligholde tydelig ansvars fordeling. 

IDP Platformen kræver en delt ansvars model:

## Adgang og ansvar for udvikler teams

Som udgangspunkt, betyder adgang at man har ansvar, fx:
- Slette data: Kan du slette data, har du ansvar for backup, og at data kan gendannes hvis nødvendigt.
- Slette resourcer: Hvis du har adgang til at slette resourcer, har du ansvar for at kunne genetablere dem i samme tilstand som før.
- Fjerne infrastrukturkomponenter: Hvis du kan fjerne system komponenter, har du ansvar for at systemet fungerer, uden nødvendig funktionalitet går tabt.

Ansvarlige personer bør vedligeholde dokumentation af risikoanalyse, adgang, kontrol og rapportering af pågældende system eller service.

## IDP teamets ansvar

IDP teamet varetager som udgangspunkt adgang til, og drift af, IDP platformen, herunder:
- Container platform (EKS)
- Deployment tool (ArgoCD)
- Repositories (GitHub/ECR) 
- Intern monitorering (Grafana)
- Adgang og tilslutning til netværk, herunder VPN, on-prem, AWS services og internet.
- 

## Delt ansvar

IDP team og udvikler team aftaler individuelt ansvarsfordeling for andre services, herunder:
- AWS managed services, fx RDS, SQS
- Notifikationer, 
- Container sikkerheds scanninger
- Kode sikkerheds scanninger
- Endpoint sikkerheds scanninger
- Disaster recovery (RPO, RTO)
- Endpoint benchmark, stresstest
- Ekstern monitorering
- Cross-platform metric and latency monitoring
- Kost og budget
- Incident og post-mortem håndtering
- 

## IDP Ansvarsmatrix


| Område        | Beskrivelse                                                        | AWS Team | IDP Team | DEV Team |
| ------------- | ------------------------------------------------------------------ | -------- | -------- | -------- |
| **AWS konti** | Provisionering                                                     | ✅       |          |          |
|               | Afvikling                                                          | ✅       |          |          |
|               | Root konto management (QR/MFA/Pengeskab)                           | ✅       |          |          |
|               | SCP management                                                     | ✅       |          |          |
|               | Organisations                                                      | ✅       |          |          |
|               | ControlTower/RAM                                                   | ✅       |          |          |
| **AWS AD**    | SSO, Entrè integration                                             | ✅       |          |          |
|               | IAM Identitycenter                                                 | ✅       |          |          |
|               | Rolle definition                                                   | ✅       |          |          |
| **AWS Netværk** | Transit gateway                                                  | ✅       |          |          |
|               | VPNs                                                               | ✅       |          |          |
|               | Routing                                                            | ✅       |          |          |
| **AWS Sikkerhed** | Assistere Niels m. adgangs restriktioner, notifikationer, SSO  | ✅       |          |          |
|               | AWS Cloudtrail                                                     | ✅       |          |          |
|               | AWS Config                                                         | ✅       |          |          |
|               | AWS Inspector                                                      | ✅       |          |          |
|               | AWS Security Hub                                                   | ✅       |          |          |
| **AWS Kost**  | Faktura håndtering                                                 | ✅       |          |          |
|               | Kost overvågning                                                   | ✅       |          |          |
|               | Discounts, funding, account manager                                | ✅       |          |          |
|               | CO2 rapportering                                                   | ✅       |          |          |
| **AWS Support** | Assistere produkt teams, Netværk, Infrastruktur og notificere    | ✅       |          |          |
| **Incidents** | incl. event notificering                                           | ✅       | ✅       | ✅       |
| **IDP**       | AWS account security                                               | ✅       | ✅       |          |
|               | Sikkerhed, adgang, authorization, authentication & data compliance |          | ✅       |          |
|               | Infrastruktur, AWS (EKS, RDS, mv)                                  |          | ✅       |          |
|               | Infrastruktur (etableret via EKS)                                  |          | ✅       |          |
|               | Portal & Interfaces, incl. avail products                          |          | ✅       |          |
|               | Tenancy isolation                                                  |          | ✅       |          |
|               | Github repsitory                                                   |          | ✅       |          |
|               | Code scanning                                                      |          | ✅       |          |
|               | Artifact repository                                                |          | ✅       |          |
|               | Artifiact scanning                                                 |          | ✅       |          |
|               | CI pipeline                                                        |          | ✅       |          |
|               | CD pipeline                                                        |          | ✅       |          |
|               | Omkostnings monitorering                                           |          | ✅       |          |
|               | Backups (infras & repos)                                           |          | ✅       |          |
|               | End-to-end observability                                           |          | ✅       |          |
|               | Skalering                                                          |          | ✅       |          |
|               | Service reliablity                                                 |          | ✅       |          |
|               | Produkt, roadmaps, strategi, interessent og behovsstyring          |          | ✅       |          |
| **Applikation** | Design, code, test & deploy features                             |          |          | ✅       |
|               | Security best practice (eg. owasp)                                 |          |          | ✅       |
|               | Data retention/compliance                                          |          |          | ✅       |
|               | Performance optimization                                           |          |          | ✅       |
|               | Dokumentation                                                      |          |          | ✅       |
|               | Omkostninger                                                       |          |          | ✅       |
| **Produkt**   | ProduktOps
|               | Roadmaps
|               | Produktstrategi
|               | Interessent-kommunikation og -management
|               | Afdække brugerbehov og problemer


## AWS' shared responsability model 
AWS' shared responsability model kunne være et udgangspunkt

<img width="749" alt="Screenshot 2024-08-16 at 07 59 15" src="https://github.com/user-attachments/assets/8b017e60-29d7-4406-b747-16c08e1c03d5">

Ideelt burde man have en løs definition der giver sig selv - er det muligt ?

<img width="591" alt="Screenshot 2024-08-16 at 08 00 36" src="https://github.com/user-attachments/assets/e26457e8-216c-4e71-ba6a-97bb12b70568">



## RACI 

"RACI" står for de forskellige typer af ansvar, der kan tildeles:

* **Responsible (R):** Personen eller teamet, der er ansvarlig for at udføre opgaven.
* **Account responsible (A):** Personen eller teamet, der er endeligt ansvarlig for den korrekte og grundige gennemførelse af opgaven. Der må kun være én Account responsible per opgave.
* **Consult (C):** Personerne, der giver input eller rådgivning i form af tovejs kommunikation.
* **Information (I):** Personerne, der skal holdes opdateret om fremdrift, ofte kun i form af envejs kommunikation.

### Roller

1. **Product Manager** (PM)
2. **Platform Team** (PT)
3. **Infrastruktur Team** (IT)
4. **Sikkerheds Team** (ST)
5. **Udviklere** (DV)


### Aktiviter

1. **Kravindsamling:** Forståelse af behov og ønsker fra interne udviklere og interessenter.
2. **Platform Arkitekturdesign:** Design af platformens overordnede arkitektur, så den opfylder både nuværende og fremtidige behov.
3. **Platformudvikling:** Kodning og opbygning af platformens komponenter.
4. **Infrastruktur Provisionering:** Opsætning af den nødvendige infrastruktur (servere, databaser osv.) til at hoste platformen.
5. **Sikkerhedsvalidering:** Sikring af at platformen overholder sikkerhedsstandarder og -reguleringer.
6. **Kvalitetssikringstest:** Test af platformen for at sikre, at den er fejlfri og opfylder de nødvendige kvalitetsstandarder.
7. **Platform deployment:** Udrulning af platformen til de interne brugere.
8. **Brugeruddannelse og Support:** Uddannelse af interne udviklere i brugen af platformen og løbende support.
9. **Overvågning og Vedligeholdelse:** Kontinuerlig overvågning af platformen og udførelse af nødvendige vedligeholdelsesopgaver.
10. **Feedback Indsamling og Iteration:** Indsamling af feedback fra brugere og iteration af platformen for at forbedre den.
