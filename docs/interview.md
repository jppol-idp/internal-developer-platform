## Interview template

udkast

Vi vil gerne identificere de største tidsrøvere og frustrationer udviklere oplever i dagligdagen, og 
afdække sammenfald blandt applikations teams, med henblik op at opbygge vores roadmap.
Vi er også interesserede i at identificere optimale arbejdsgange som vi kan inspireres af.

### Intro  
Hvad er jeres team ansvarlig for?  
Hvad er din rolle på holdet?

### Nuværende miljø  
Kan du give os indblik i jeres udviklingsmiljø, samt de værktøjer og tjenester I bruger?  
Hvordan ser dit lokale udviklingsmiljø ud?

### Planlægning og definition af arbejde  
Når du begynder at arbejde på et nyt projekt, hvad er det første skridt du tager i planlægningen af det?  
Hvad gør du efter at have opnået det?  
Tænk tilbage på sidste gang du påtog dig et nyt projekt. Hvordan identificerede du kravene?

### Udvikling - Nye applikationer  
Hvornår oprettede du sidst en ny applikation?  
Hvilke skridt fulgte du for at oprette den applikation?  
Hvor lang tid tog det at få applikationen op og køre?  
Hvor ofte gør du dette?

### Udvikling - Eksisterende applikationer  
Hvilke nuværende applikationer arbejder du på?  
Hvilke skridt fulgte du for at sætte dit miljø op?  
Har du arbejdet på andre applikationer?  
Hvad var den sidste applikation, du arbejdede på før denne?  
Hvordan var det at skifte fra at arbejde på den sidste applikation til den nuværende?  

### Udvikling - Debugging  
Hvad var en nylig vanskelig fejl, som du stødte på?  
Hvordan gik du frem med at debugge den?  
Kunne du gøre det lokalt?  
Hvordan debugger du produktionsproblemer?  
Har du logget ind på produktions-servere eller adgang til produktions-databaser for at løse problemer?  
Hvis ja, fortæl mig om sidste gang du gjorde det. Hvilke produktionstjenester havde du brug for at få adgang til?  

### Drift af dine tjenester  
Hvor får du besked fra når en service har problemer eller er utilgængelig?  
Hvordan ved du, at dine services virker ?  
Hvordan måler du ydeevne ?  
Bruger du Software Delivery Performance-metrics som DORA, (andre?)  

### Test  
Hvordan tester eller validerer du dit arbejde lokalt?  
Hvordan tester du dine ændringer i kombination med andre udvikleres ændringer?  
Hvordan ved du, at en ændring er klar til at blive udrullet til produktion?  
Hvor lang tid bruger du normalt på at bygge tests til dine ændringer?  
Hvor lang tid tager dine tests normalt at køre?  
Hvilken type ændringer er de sværeste at teste eller tager længst tid?  

### Sikkerhed  
Hvordan sikrer du dig mod sikkerhedssårbarheder i din kode?  
Håndterer din tjeneste nogen GPDR eller andre følsomme data?  
Hvis du skulle foregive at være en hacker for et øjeblik, på hvilke måder ville du angribe dine services ?  
Hvilken information eller adgang kunne du forestille dig, at du kunne få?  
Hvilke adgangs krav skal du opfylde for at udvikle/deploye ?  

### Business Continuity
Foretager du risiko analyse af dine applikationer ?  
Herunder acceptable nedetider og tolerencer for datatab ?  
Forholder du dig til disaster recovery-planer og backup strategier ?  
Registrerer du applikationer i et centralt register og kortlægger afhængigheder ?   


---

### Huskeliste

**Infrastruktur:**  
> fx: on-prem, AWS, Azure, GCP, Oracle     

**Observability:**   
> fx: Solarwinds, Datadog, Elastic, Splunk, Nagios, cloudwatch, pingdom   

**Infrastructure as Code ?**   
> fx: Terraform, Pulumi, CDK, CDKTF, bicep, cloudformation   

**Hvilken Version Control:**   
> fx: Github, Gitlab, Enterprise Git, Codecommit   

**CI/CD ?**  
> fx: Github actions, octopus deploy, jenkins, argoCD   

**Artifactx**   
> ECR, GHCR, dockerhub

**Security**   
> snyk, github advanced security, 

**Secrets**   
> AWS SSM, 

**Network** 
> fx: vpc peering, transitgateway, On-prem  

**Container Orchestration**   
> ECS, EKS, 
