# DNS migration

We have several problem sets, that need to be solved regarding DNS.

Some problem arises form..
 - the need to expose private endpoints in a uniform manner inside a cluster
 - migrating existing domains and DNS names to IDP controlled zones. 
 - Collaborating with other DNS zone owners when a domain cannot be migrated. 
 - Controlling traffic flow on hard-to-change DNS names while migrating. 
 - a desire to traffic optimize (avoiding NAT traffic when needed etc). 




## Traffic optimization (avoiding NAT traffic when needed etc). 
### What is is? 
If a service is exposed on a public DNS name and endpoint there may be requests to 
a service hosted in the same cluster. If multiple services inside a cluster need to 
connect to each other, using a public IP will cause traffic to NAT. This is both 
expensize as traffic cost increases, may also cause overhad in the clusters traffic 
handling and perhaps slow caonnections unnecessarily, as the traffic must perform unneeded 
network hops.  

### Conceptual solutions
- Split DNS with resolve of cluster-internal load balancer inside cluster
- Multiple DNS names and configuration handling where services uses the internal DNS name. 

### When and criticalization 
Problem is mostly from a cost perspective. 

## The need to expose private endpoints in a uniform manner inside a cluster
### What is is? 
Some services may be strictly internal and perhaps have a lower security level 
as service only expects requests from friendly and internal clients. 

### Conceptual solutions
- Expose service names in DNS with internal IP. 
- Block requests in load balancer. 
- Split dns where name only resolves internally
### When and criticalization 

## migrating existing domains and DNS names to IDP controlled zones. 
### What is is? 
For a more manageable DNS 
### Conceptual solutions
### When and criticalization 

## Collaborating with other DNS zone owners when a domain cannot be migrated. 
### What is is? 
### Conceptual solutions
### When and criticalization 

## Controlling traffic flow on hard-to-change DNS names while migrating. 
### What is is? 
### Conceptual solutions
### When and criticalization 

