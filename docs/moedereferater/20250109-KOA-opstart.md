# Opstartsworkshop
Jonas, Kristian True, Kristoffer, Nicolaj, Kasper KN, Kasper Ø, Martin


# Konfig
Rækkefølgen: 
- jsonfil
- secrets
- environmentvariable

# NB
- Hvordan deployer man secrets?
- Behov for scheduled tasks? (Bruger AirFlow i dag.)
- IT og AT (tests med afhængigheder)


# Deployments
TF apply manuel proces der udføres af udvikleren efter behov. 

Deploy af ny service: 
 - Bygger image 
 - Push image og flyt environment tag i repo
 - genstart service (forced redeploy)

# Udvikleres miljøer
- Docker compose
- Bridge to Kubernetes


# Styring af environment 
Benytter i dag paths `ServiceNavn/EnvironmentName/SecretNavn` 
Måske ønsker vi os at komme af med environmentname eller bytte rækkefølgen. 
Vi kan lave et præfix og KOA kan kalde alle envs for `IDP` `EnvironmentName/ServiceNavn/IDP/SecretNavn`
men vi skjuler første del af path, så koden ikke skal ændres pr environment. 


# Databaser
Bevare den eksisterende databasestruktur med en rds-server pr database, der kærer på meget små instanser. 

Vi skal i det nye setup understøtte, Postgres, MSSQL og DynamoDB. 

Hvorfor bruger vi 20 mikro-instanser i stedet for en enkelt databaseserver: 
- dev-postgres, test-postgres. (deles)
- Access Service 
- Opstart er at det nye dev-cluster skal kalde eksisterende dev-databaser. 
  - DOG må Hangfire-databassen ikke være delt mellem. 
  - Hangfire er en egenskab i mange services, så man kan ikke isolere den til opstart. 
  - Måske skal vi lave en fire-and-forget-database til Hangfire.
- Behov for at VPC-peere med eksisterende databasemiljø.


# Lige nu og her
IDP skal have etableret VPC-peering
KOA skal sende deres docker images til IDP-ECR. 

