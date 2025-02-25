# Shared accounts 

We expect each team to have a set of accounts dedicated to dev, test and production environments. 

On top of that we have some shared accounts that are mainly handled by the IDP team. 

These accounts are

| Name             | id         | Description |
| ---------------- | ---------- | ---------------|
| jppol-idp-shared |354918371398| Contains state in s3 and state locks in DynamoDB. |
| jppol-idp-test   |971422674709| Testing stuff internally  |
| jppol-idp-main   |692859947694| ECR repositories and (probably) a shared route53 zone.  |



# OIDC from repos

When an account is setup, we allow a number of repos to use an Identity Provider in the account 
with a role, that can assume a deploy role. This makes it possible for github actions in selected
repositories to perform terraform actions on the account. 

# Console maintenance
In the `jppol-idp-main` account a `main-deploy-role` is configured. This can be assumed 
by jppol-idp-main admins (IDP team) to easily perform CLI operations and apply OpenTofu 
declarations on multiple accounts. (TODO: Do we need this role or is ti ok with the slightly 
more involved assume-role-pr-account approach?)

# Route53 maintenance
The account `jppol-idp-shared` contains a zone for `idp.jppol.dk`. Each child account 
can maintain a subdomain on this zone. Using the module `idp-subdomain` in the idp-main-setup 
repository, the zone will be created with a set of tags and a role, that allows read access 
from shared. Then shared is applied, the subaccounts zones will be queried for idp-zones and 
attached to `idp.jppol.dk` in the shared account.
