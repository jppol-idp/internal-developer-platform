### Architecture Decision Record (ADR)

#### Title: 004 Valg af GitHub som Repository Platform

#### Date: 2024-06-03

---

## Status

Godkendt

## Kontekst

Vi har brug for en git-platform til at hoste, versionere og samarbejde om vores softwareprojekter i IDP og i DUT som helhed. 

## Beslutning

Vi vælger en github enterprise cloud model som kan samle alle eksisterende github organisationer, teams og repositories under èn konto.  
Implementations detaljer her: https://jira-jppol.atlassian.net/browse/IDP-67

## Konsekvenser

Vi vil få samlet alle vores repositories under en licens, og dermed potentielt spare licenser der i dag bruges på tværs af vores github organisationer. Fremadrettet vil vi kunne facilitere mulighed for fælles sikkerheds foranstaltninger, audits, Active Directory integration, sikkerheds scanning af repositories, samt CI/CD pipelines med GitHub Actions, og GitHub container registry til rådighed.

## Alternativer

Flere muligheder blev overvejet, herunder GitHub, GitLab, AWS CodeCommit, Bitbucket og Azure Repos.

**Github Enterprise Cloud (Valgt)**
- SSO via Entra
- Eksisterende organisationer og teams kan flyttes til enterprise konto med eksisterende konfiguration/rettigheder
- Eksisterende enterprise server kan blive, eller migreres til cloud med Enterprise Importer uden ekstra kost
- Decentral administration kan ske på organisations niveau (eller repos niveau)
- Commit name er personlig github konto, som er godt ifølge [michael nygard](https://www.michaelnygard.com/blog/2015/04/people-dont-belong-to-organizations/)
- Github EMEA flytter hosting til sverige i efteråret
- 50.000 CI/CD minutes/mdr + brugerens egne 2000 min, hvorfor vi sansynligvis ikke behøver self-hosted runners.
- Adgang til Advanced Security Scanning, som kan forhindre at sensitive data bliver commitet, samt kode scanning

Yderligere fordele ved Github:

- 95% af vores repositories ligger allerede i github
- Den største og mest kendte platform, betragtet som industri-standard
- Den største platform for open source, som vores udviklere får mulighed for at bidrage til.
- Vi benytter allerede github actions CI/CD
- Flest integrationer tilgængelig
- Indeholder wiki, issue tracking, projekt styring

**Github Enterprise Cloud Managed users**
- Brugere synkroniseres fra AD til Github med SCIM
- ingen personlige github konti
- public repos er ikke mulig
- migrering fra eksisterende organisations/teams er svær
- der skal skiftes bruger, hvis der skal tilgås github ressourcer med personlig konto
- Er typisk kun nødvendigt i banker eller andre hårdt regulerede butikker
- Vi mener enterprise management giver en usmidig oplevelse for de brugere, der allerede har en aktiv github handle - hvilket vil sige de fleste af vores udviklere. Samtidig udelukker det os fra samarbejder uden for koncernen, hvilket kan fungere usmidigt i forhold til eksterne samarbejdspartnere.

**AWS codecommit**
- Integrerer med AWS services, primært IAM og S3, men platformen mangler det samme niveau af brugerfællesskab og tredjepartsintegrationer som GitHub.
- Man får ikke noget foræret ved at bruge codecommit frem for github i AWS
- Vores AWS solution architects foretrækker github, og kalder det crem de la creme of repositories
- Bold bruger codecommit som de eneste i DUT. (4 brugere)
- Codecommit er markeret som end-of-life pr. juli 2024.

**Gitlab**
- Selvom GitLab tilbyder omfattende CI/CD og DevOps værktøjer, er det mere komplekst og kan være overvældende at konfigurere – dette er ikke undersøgt nærmere.

**Bitbucket**
- Holdet.dk bruger bitbucket som de eneste i DUT (3 brugere)
- God integration med Atlassian-værktøjer som Jira, men har en mindre brugervenlig grænseflade og et mindre aktivt samfund sammenlignet med GitHub.

**Azure Repos**
- Vi bruger det ikke i dag
- Bedre egnet til teams der allerede bruger Azure
