# Requirements for AI prod

## Participants
Kristoffer, Kasper, Fæster, Julian, Jonas K

## Expectations 
AI builds the recommender systems to be able to bootstrap from zero. 
It is not critical if the system is down as it will not cause down time 
on the web sites, although the user experience will be impeded. 

## State 
Magna has its state in Redis Cloud that handles the persistance requirements.

Recommenders will need some real persistance. We have a persistant storage class 
but will need to investigate how to remount certain volumes. This requirement is 
related to database storage and needs to be on EBS. 

Kasper will look into persistance and back. 

ML Ops needs access to EFS, but this can be back filled and is not critical data.

## Backup 
We will look into backup of EBS storage classes when storage is marked as 'retain'. 

Backup should not be a historical archive but an option to recover from human errors: 
Ie we will not retain backups for more than a couple of weeks.

## Non-idp Aws resources
We need to provide a model for provisioning resources in the idp-accounts. 

## VPC peering 
VPC peering will be needed. We have some experiene for the db peering in KOA. 

We seem to agree that peering is part of cluster setup. This also implies that 
the responsipolity is responsibility of IDP. 

There may be situations where ip ranges overlap between vpcs. We will handle this 
on a per case basis.

## Cross account access
The pods running inside idp cluster have a deterministic role name. If the pods need 
to access resources in other accounts, we expect the "other account" to be handling 
the access configuration.
