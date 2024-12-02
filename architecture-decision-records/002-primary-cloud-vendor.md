### Architecture Decision Record (ADR)

#### Title: 002 Valg af Primær Cloud Leverandør

#### Date: 2024-08-03

---

## Status

Godkendt

## Kontekst

Vi har i øjeblikket 95% af vores cloud-infrastruktur placeret i AWS, og vores eksisterende know-how afspejler dette med en tilsvarende vægtning på AWS-teknologier. Til specifikke formål som fx OpenAI og Active Directory anvender vi også minimalt andre cloud-platforme.
Vi ønsker èn primær cloud leverandør, men ønsker samtidig at være leverandør uafhængige, som beskrevet i vores [manifest](https://github.com/jppol-idp/internal-developer-platform/wiki/manifest#cloud)

## Beslutning

AWS har vist sig at være førende inden for markedet med det bredeste udvalg af tjenester og den højeste tilgængelighed. 
AWS fastholdes som vores primære cloud leverandør på grund af vores omfattende eksisterende infrastruktur og in-house erfaring med deres brede udbud af tjenester. 

## Konsekvenser

Vi skal minimere risikoen for vendor lock-in, men vi anderkender, at det aldrig helt kan undgås. Vi skal løbende evaluere udviklingen inde for cloud teknologi og vores behov og overveje muligheden for at anvende andre cloud-udbydere, hvor det er relevant og fordelagtigt.

## Alternativer

Alternativt kunne vi vælge en anden primær cloud leverandør, at satse på on-prem eller at fokusere på multicloud - Vi ser det som fordelagtigt at fokusere vores indsats på èn udbyder til at starte med. 





