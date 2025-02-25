# Opstartsmøde 21/11 2024
Kasper, Martin, Kristoffer, Kristian, Morten

## DB 
I JPs miljøer hoster man en meget stor mængde RDS-instanser, hvor man har et rds-instans per service. 

I dev og test kører der en mængde meget små (t3.micro) instanser. Disse vokser i prod. 

Forestillingen hos IDP var at man kørte et (eller i hvert fald "få") flustre pr environment.  


### Databaseopgraderinger: 
Ansvaret ligger hos 
UAFKLARET....


Behov for åben forbindelse over DNS. 


## Deployments 
Vi vil gerne hen til Helm-charts. Values-fil pr miljø afgør hvilke specifikke versioner, der skal være aktive i de enkelte miljøer. 


## ECR
Vi laver et fælles ECR, som bliver indgangen til deployments i IDP-regi. 

ECR kan også indeholde Helm-chart. 

Charts kan også være relevante i forhold til udviklernes lokale miljøer. 

## Kubeconfig

Vi regner med at man har read-adgang til de relevante clustre. Modifikationen af clusteret skal ikke ske via kubectl...

## Deploystrategier 
Der kan være behov for at services kører maximum 1 instans. Flertallet/normen er at services kører stateless med mulighed for horisontal skalering. 

## Statisk analyse 
Kristian spørger om der på sigt kommer tjek af om de forskellige services har fornuftige indstillinger. 

Vi har talt om muligheden for at lave templates, der sikrer mod de værste problemer ved at give et begrænset set af parametre, der skal være udfyldt. 

## Adgange 
Vi bliver inviteret til jp-koa i github, så vi kan orientere os lidt i kode og deployments. 

Vi skal have en præsentation af eksisterende pipelines. 


## Loadbalancers
JP stiller tre ALB'er til rådighed pr miljø. 

De giver basalt intern og ekstern adgang - derudover findes der en ip-limiteret lb, hvor man kan nå "interne" services fra udviklermaskiner. 


## DNS 
Der er "forudsigelige" navne på alle services af formen <<servicenavn>>.<<miljø>>.<<noget-fælles-standard>>

Derudover er der behov for at services kan tilknytte alias'er.

### Certifikater
I forhold til https giver det udfordringer med certifikatudstedelse på domæner man ikke ejer. 


### Intern kommunikation 
Der kan være fordele i at benytte interne navne i clusteret til intern trafik mellem services. 



# Kommunikation 
KOA bruger Teams. 

Det er hensigtsmæssigt med en fælles kanal i enten Teams eller Slack.  


# CRON 
KOA benytter CRON i dag. Vi har Argo events klar i clusteret.

KOA bruger Airflow i dag, men er interesserede/villige til at skifte til Argo Events.

Vi skal undersøge hvordan vi konverterer enkelt. 

# Tidszoner
Clusteret kører UTC. Hvis der er behov for lokale tidszoner må man sætte det i containeren. 

# Next steps
- Etablering af AWS konto til TEST miljø
- Provisionering af EKS cluster service, inkl. observability, ingress, kubecost, argo, ?
- Etablering af infrastruktur repository, inkl. evt pipeline
- Etablering af fælles ECR
- Deploy af giftcard service
- Etablering af netværks adgang til afhængigheder
- Etablering af slack support



