# Decision record 


# 013-adgang.md
Dato: 2024-12-22

## Status

Forslag

##  Kontekst

For at sikre den bedste og sikreste DevEx skal vi vurdere hvordan adgang og tilladelser håndteres i IDP'en, herunder: 
- password rotation, 
- password kompleksitet, 
- mfa, 
- session timeouts og re-authentication, 
- roller, 
- lokation

Som beskrevet [tidligere](https://github.com/jppol-idp/internal-developer-platform/blob/main/architecture-decision-records/001-identity-provider.md) 
skal brugerstyring, og gerne adgang, administreres via EntraID.

##  Beslutning

Vi ønsker at alle IDP brugere betinges af:
1. 3 Måneders password rotation, reuse og complexity (default fra Entra).
1. SAML autentificering med 24 timers TTL (uden browser re-authentication som i githubs tilfelde)
1. MFA med 1 mdrs TTL uanset lokation.
1. Device state med Trend monitoreret.

Undtagelser:
1. AWS role-chaining max 8 timer TTL

## Konsekvens

SCIM har 40 minutters latency - fx i forbindelse med indbrud: kan [bypasses](https://medium.com/@nadav.shaham_94592/how-we-bypassed-microsoft-ad-provisioning-interval-ff03d17477ce)
eller [her](https://medium.com/i-love-my-local-farmer-engineering-blog/charting-our-identity-journey-in-aws-part-2-e4a99e6b1de3)
eller [her](https://wiki.resolution.de/doc/saml-sso/latest/all/knowledgebase-articles/technical/jit-and-microsoft-entra-id-formerly-azure-ad-sending-groups-via-saml-attributes)
eller [her](https://sharmanandmishra.medium.com/aws-sso-provide-just-in-time-access-using-azure-ad-pim-a6c46133f2ec)
eller [her](https://towardsaws.com/managing-jit-with-aws-iam-identity-center-and-azure-privileged-identity-management-8123375e1008)
eller [her](https://learn.microsoft.com/en-us/entra/identity/saas-apps/aws-single-sign-on-provisioning-tutorial)



## Detaljer

Roller:
1. Admin
1. Developer
1. Readonly

Betingelser for autentificering:
1. Bruger/gruppe
1. TTL
1. Device
1. Device state (Trend)
1. Lokation

Typer af autentificering
1. Password
1. MFA
1. VPN

IDP relaterede services:
1. AWS
1. EKS API
1. GitHub
1. Argo
1. Grafana


VPN beskytter potentielt mod trojaner og mitm, ved at filtrere udgående trafik og isolere vores devices på usikre netværk.
Desuden kan VPN gøre det lettere at tilgå private services, der dermed ikke behøver offentlig tilstedeværelse.
Vi har allerede en VPN struktur der ville gøre det nemt at indføre VPN krav, tilgengæld vil vi så være afhængige af at VPN virker.
