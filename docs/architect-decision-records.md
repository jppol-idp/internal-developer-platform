# Architect Decision Records (ADR)

**[ADR arkiv](https://github.com/test-jppolitikenshus/internal-developer-platform/tree/main/architecture-decision-records)**

Beslutninger registreres som Architect Descision Records (ADRs) og opbevares offentligt tilgængeligt i [git](https://github.com/test-jppolitikenshus/internal-developer-platform/tree/main/architecture-decision-records)

Beslutningsprocessen er beskrevet herunder:

### **Formål**

ADRs indeholder grundlæggende beslutninger om produkt- og teknologi valg og fravalg, og giver vores 
kunder mulighed for at tage højde for dem i deres planlægning samt bidrage med feedback og input.

Brugen af ADR skal sikre:  
- **Transparens:** Alle beslutninger er dokumenterede og let tilgængelige for dev teams og andre interesserede.
- **Historik:** Vi har en klar historik over beslutningernes udvikling og årsagerne bag dem.
- **Samarbejde:** Alle har mulighed for at bidrage med nye ADR'er, feedback og input til eksisterende beslutninger.
- **Konsistens:** Beslutningsprocessen er konsistent og veldokumenteret.

### **Hvordan bruger vi ADR**

Enhver ny eller ændret beslutning bør følges af en ADR, der dokumenterer beslutningsprocessen.
ADR-arkivet er åbent, alle kan bidrage med feedback eller input til eksisterende ADR'er - nye ADR'er kan oprettes i repositoriet. 

### **Hvordan er ADR processen** 

ADR-udvalget består af IDP teamet, som mødes når der er behov, og følger en process der kan inspireres af denne: 

- **Trigger:** En beslutning om en ny teknisk løsning, en ændring af eksisterende arkitektur, eller en vigtig afvejning for eller imod bestemte teknologier.
- **Ansvarlig:** Alle kan identificere et behov og foreslå en ADR.
- **Indledende evaluering:** Kan være teammedlemmer i platformteamet.
- **Møde:** Produktmanageren indkalder til et ADR evaluerings møde på baggrund af foreliggende udkast.
- **Feedback:** Reviewers læser udkast og kommer med kommentarer og forslag.
- **Diskussion:** I mødet diskuteres feedback åbent med fokus på fordele, ulemper og mulige forbedringer.
- **Godkendelse:** Hvis ADR’en accepteres efter review, opdateres den sidste version af ADR’en og en beslutningsstatus tilføjes.
- **Implementering:** Beslutningen dokumenteret i den godkendte ADR implementeres af teamet som planlagt.
- **Overvågning:** Platformteamet følger løbende op for at sikre, at implementeringen følger den beslutning, der er dokumenteret i ADR’en, og overvåger effekterne.
- **Reevaluering:** ADR'er bør periodisk reevalueres for at vurdere deres fortsatte relevans og nøjagtighed.
- **Opdatering:** Ved behov opdateres ADR'er med nye data og indsigt, eller beslutningen kan ændres, hvis nye informationer eller teknologiudviklinger gør det muligt.

![image](https://github.com/user-attachments/assets/fb38dae1-41fc-462b-836f-d2fb77862f5b)

Beslutningsprocessen er vedtaget her [000-registrering-af-beslutninger.md](https://github.com/test-jppolitikenshus/internal-developer-platform/blob/main/architecture-decision-records/000-registrering-af-beslutninger.md)

Referencer:   
https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions    
https://agiledojo.de/2023-03-06-how-to-write-a-good-adr/   
https://www.thoughtworks.com/en-us/radar/techniques/lightweight-architecture-decision-records   
https://ieeexplore.ieee.org/ielx7/52/9801712/09801811.pdf?tp=&arnumber=9801811&isnumber=9801712&ref=aHR0cHM6Ly9hZHIuZ2l0aHViLmlvLw==   
