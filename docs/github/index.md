---
title: GitHub
nav_order: 2
---

# Overblik over GitHub i DUT.

Status på onboarding af eksisterende GitHub Organisationer til vores nye GitHub Enterprise Cloud [her](https://jira-jppol.atlassian.net/browse/IDP-103)

# Konsekvenser ved at flytte til GitHub Enterprise Cloud:
- Efter GitHub organisation er flyttet, bliver brugere automatisk bedt om SAML authentication ved første login - herefter skal authentication bekræftes hver 24. time.
- Brugere skal godkende deres personlige SSH nøgle(r) og PAT(s) til SSO, evt. efterfulgt af `gh auth login` for at kunne tilgå/skrive til repos med SSH (og Visual Studio mv). 
- External collaborators uden MFA bliver fjernet.
- Brugere uden SAML ID kan konverteres til external collaborators men beholder kun rettigheder defineret via et team - hvis brugeren er tildelt adgang direkte fra et repository, mistes adgangen.
- Jeg kan ikke se hvordan i authenticater terraform til github idag - en app ?





## Github Enterprise Cloud Indstillinger:
Alle settings er default, dog:

- MFA og SAML påkræves fra Enterprise niveau. 
- Adgang uden SAML identitet er mulig som Outside Collaborator - denne funktionalitet kan deaktiveres af GitHub Organisation Admin.
- GitHub Advanced Security (49USD/month) pr aktiv comitter (gælder 3 mdr bagud) slås som udgangspunkt fra på interne og private repositories. 
- Alle github actions tillades, inkl. eksterne actions.
- Øvrige rettigheder, konfigurationer og tilkøb administreres som udgangspunkt af Organisation Admins.

## Onboarding af eksisterende GitHub organisation til Github Enterprise Cloud:
1. Der sendes en invite fra Enterprise Cloud
1. Organisations admin godkender
1. Enterprise admin godkender
1. Konsekvenser af evt. ændring af org navn [her](https://docs.github.com/en/organizations/managing-organization-settings/renaming-an-organization) 
Kort sagt: 
  - organisationens endpoint url bliver fjernet eg. https://github.com/jppol-organisation
  - hvis organisationens navn bliver gen-registrereret og der oprettes repositories med samme navne, vil redirects blive overskrevet 
  - så registrer evt det gamle org navn efter migrering - det burde løse problemet - Det bedste er selvf at opdaterer url i local settings.

## Fakturering:
Betaling for GitHub licenser (21USD/month) og relaterede services (actions, advanced security, mv) via Azure subscription ID: cd441771-16a2-4166-a6c8-d6aca36129f0 (JPPOL EA - GITHUB)
- Via API kan man tilknytte brugere til et kostcenter og opdele kost i månedlig rapport, ex: 
```bash 
gh api   --method POST -H "Accept: application/vnd.github+json"   -H "X-GitHub-Api-Version: 2022-11-28"   /enterprises/jp-politikens-hus/settings/billing/cost-centers/17e71f8d-fbd7-42dd-8cdb-9c2558c72bd7/resource    -f "users[]=plexdk"
```

Der findes 2 slags brugere, Medlemmer og Outside Collaborators:

## Onboarding af Medlemmer
- Medlemmer uden MFA bliver bedt om at aktivere MFA på deres personlige konto.
- Når brugeren forsøger at opnå adgang til organisationens repositories, bliver der forwarderdet til SAML authenticate via EntreID. 
Hvis brugeren ikke har adgang, skal der forespørges om adgang til ad gruppen **kit-roodom-dk** som alle i DUT er blevet medlem af
(TODO: denne bør omdøbes til noget meningsfuldt, fx github-members hos ServiceDesk - det bliver den ikke da denne gruppe også bruges 
til andre ting, men så bør der oprettes en ny, ifb IDM projekt v. Kenneth). Ved succesfuld authentication, bliver brugerens SAML 
identitet tilknyttet brugerens GitHub handle. 
- Brugeren skal herefter godkende evt. SSH nøgler eller Personal Access Tokens til den pågældende organisation, herefter køres ‘gh auth login’.
- Public repositories vil fortsat være synlige for alle.
- Hvis brugeren vil afkoble deres GitHub handle fra deres SAML identitet, kan Organisation Admin ophæve tilknytningen.
- Medlemmer uden SAML identitet kan konverteres til Outside Collaborator, men bibeholder i så fald kun adgang til private repositores 
defineret via et Team. Dvs. hvis adgang er givet direkte til repositories, skal brugeren inviteres igen.

## Onboarding af Outside collaborators
- Outside Collaborators uden MFA bliver fjernet fra organisationen og modtager en mail herom.
- Outside Collaborators behøver ikke SAML identitet.
- Outside Collaborators kan tilføjes direkte til 1 eller flere repos, men kan ikke være med i et Team, eller en organisation.
- Koster en licens ved adgang til mindst èt privat repos (21USD/month)
- Organisation admins kan deaktivere muligheden for outside collaborators

## Offboarding 
- Medlemmer: Team sync will not remove users from an organization when they are removed from a team, this must be done by admin. 
- Outside collaborators: skal fjernes manuelt
- Ophævning af sso tilknytning: Når bruger fjernes via AD, kan vedkommende ikke længere logge ind, men koster stadig licens - ssh nøgler vil stadig være aktive.
- licens: Der bliver opkrævet licens for alle enterprise brugere, også inaktive - sletning af brugere er manuel, se nedenfor.
- Håndtering af **inaktive brugere**: Hvis brugere ikke er aktive jvf [rapport](https://docs.github.com/en/enterprise-cloud@latest/admin/managing-accounts-and-repositories/managing-users-in-your-enterprise/managing-dormant-users)
kan enterprise admin fjerne dem. Rapport over brugere findes under compliance rapport “Dormant Users”.
- SSH keys is still active when sso is disabled user has to be removed from enterprise - [link](https://docs.github.com/en/enterprise-cloud@latest/authentication/authenticating-with-saml-single-sign-on/authorizing-an-ssh-key-for-use-with-saml-single-sign-on)

## Team synkronisering
- For at en bruger kan tilgå et repository, skal brugeren manuelt tilføjes github organisation, enten af en organisation admin eller en enterprise admin. Medlemmer tilføjes eller inviteres IKKE til organisationen automatisk via EntraID sync.
- Hvis et GitHub Team linkes med en AD gruppe, kan medlemmer kun styres via EntraID, og dermed ikke fra Github. 
- Synkronisering mellem GitHub Teams og AD sker en gang i timen.
- GitHub Team synkronisering med EntreID administreres af GitHub Organisations Admin.
- Der oprettes fx AD grupper svarende til de roller der skal bruges, se: https://github.com/jppol-idp/idp-main-setup?tab=readme-ov-file#create-ad-groups
- Herefter kan organisations admins tilknytte dem til GitHub Teams.
- En måde at invitere alle enterprise brugere:

# Get all enterprise members
users=$(gh api --paginate /enterprises/YOUR_ENTERPRISE/members | jq -r '.[].login')

# Send invitations to all users
```yaml
for user in $users; do
  gh api --method PUT -H "Accept: application/vnd.github+json" \
    /orgs/YOUR_ORG/memberships/$user
done
```
herefter kan der løbende inviteres nye brugere: 
```yaml
name: Invite Enterprise Users
on:
  schedule:
    - cron: "0 0 * * *"  # Runs daily at midnight
jobs:
  invite_users:
    runs-on: ubuntu-latest
    steps:
      - name: Get Enterprise Users and Invite
        run: |
          users=$(gh api --paginate /enterprises/YOUR_ENTERPRISE/members | jq -r '.[].login')
          for user in $users; do
            gh api --method PUT -H "Accept: application/vnd.github+json" \
              /orgs/YOUR_ORG/memberships/$user
          done
        env:
          GH_TOKEN: ${{ secrets.GH_ADMIN_TOKEN }}  # Use a PAT with admin:org scope
</code>
``` 
## Copilot
Organisations admin kan bevillige copilot licens til medlemmer i enten business (19USD/month) eller enterprise (39USD/month) version
Enterprise inkluderer:
- Generate a description of the changes in a pull request
- Create and manage collections of documentation, called knowledge bases, to use as a context for chatting with Copilot

GitHub Copilot lever op til følgende organisatoriske krav, og er dermed tilladt for udviklere:
- GDPR - “Yes. GitHub and customers can enter a [DPA](https://github.com/customer-terms/github-data-protection-agreement) that supports compliance with the GDPR and similar legislation. 
[Copilot](https://github.com/features/copilot#faq)(tryk FAQ → Privacy) **TODO: eller dækker vores nuværende microsoft agreement?**
- Model træning - vi benytter Copilot Business: “GitHub does not use either Copilot Business or Enterprise data to train its models.“
- tredje part - der må ikke uploades 3. parts software. (se ovenfor)
- **TODO: afvent Tanja/Nanna afklaring og gennemsyn**

## Billing og rapportering
GitHub tillader billing managers uden beregning
Rapportering er i beta, men der kan hentes usage report fra Billing & Licensing under Usage.
Det er muligt at etablere kost centre, hvis gruppering ud over organisations niveau er ønsket.

## Sikkerhed
Der kræves ikke VPN eller IP whitelisting for at tilgå GitHub.
Aktivering af sikkerheds kontroller i GitHub, som secret scanning, push protection, advanced security, dependabot, skal aktiveres og/eller konfigureres af organisations admins.

## GitHub App
Efter sso identitet er aktiveret, skal der logges ind igen for at få adgang.

## GitHub Kontrakt
Afventer Nanna og Natasha ift kontrakt og data protection agreement
Github ligger i US - der findes en EU lokation, men den kræver ny URL og Enterprise Managed Users.
