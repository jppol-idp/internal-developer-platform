### Architecture Decision Record (ADR)

#### Title: 001 Valg af Identity Provider

#### Date: 2024-08-03

---

## Status

Godkendt

## Kontekst

Vi skal sikre at vores brugere nemt kan opnå adgang til platformen, samt at de automatisk fjernes igen når de ikke længere skal have adgang.
Microsoft Entra benyttes allerede som IdP i huset.

## Beslutning

Vi vil bruge Microsoft Entra IdP, da det allerede er integreret i vores eksisterende systemer, inklusive AWS, hvilket giver os den fordel, at vores brugere kun eksisterer èt sted. Desuden tilbyder Microsoft Entra Single Sign-ON (SSO). På længere sigt vil vi potentielt kunne administrere rettigheder til platformen direkte fra platformen.

## Konsekvenser

Microsoft Entra SCIM provisionerer typisk brugere og grupper hver 40. minut.  
Single Sign-On (SSO) kan implementeres ved hjælp af OIDC og SAML.  
ADFS er blevet udfaset.

## Alternativer

Selvom der findes mange alternaltiver, fx. GitHub, AWS, Okta, Google, nævnes disse ikke nærmere da vi allerede har en gennemgribende og  velfungerende integration med Microsoft Entra.
