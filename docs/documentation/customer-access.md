# Customer access
When interacting with the IDP customers should interact with github, and IDP provided tools
wherever possible. The AWS Console is considered a last resort.

For daily operations we anticipate ArgoCD, Grafana and of course the customer application 
definition repositories, to be the main point of interaction.

# Access components
The main infrastructure component delivered to a team is a namespace in a cluster. 
A team can have multiple namespaces inside a cluster, to provide logical environments
or perhaps to divide between multiple products maintained by the same team. 

Each team onboardet on the IDP has access to a github repository in the `jppol-idp`
organisation, which allows them to define applications for all their namespaces on 
multiple clusters. 

Login to GitHub is a combination of the users github handle of choice, combined 
with an occasional validation of association to JP/Politikens Hus based on OIDC-login 
to jppol-entra. 

# Graphana and ArgoCD access
Access to Grafana and ArgoCD is controlled by AD-groups created per _namespace_. 

Group names are constructed as 
`<<namespace>>-<<product>>-<<access-level>>`. 

We currently have the following groups 
- koa-dev-grafana-write
- koa-dev-argocd-write
- koa-test-grafana-write
- koa-test-argocd-write
- koa-prod-grafana-write
- koa-prod-argocd-write
- ai-test-grafana-write
- ai-test-argocd-write
- ai-prod-grafana-write
- ai-prod-argocd-write

We don't provide customers admin access to any tooling anywhere. `write` simple signifies, 
that the user may be able to modify dashboards, restart a service or similar operations. 

We may need to introduce `read` access later, but currently expect to accomodate everybody
as readers.

# Secrets
We allow each team to define their own secrets in AWS Secrets Manager in the account holding their cluster. 

This access is granted based on resource names. The secrets name must start with `customer/` 
followed by a "namespace" defined per team/product. Defining this access happens in idp-main-setup 
where the namespace is chosen. This produces a role, that can be assumed from actions in 
a set of GitHub repositories defined by the customer. 

# ECR
All container images used by the customers should be pushed to the registry in 354918371398 
idp-jppol-shared. The registry is sectionaed by a namespaced defined on a per team/product basis. 

In the setup in idp-main-setup we define which accounts can _pull_ from the ECR registry. 
Some images like IDP defined halm charts should be available to everyone. Other images should 
be strictly available to certain teams and accounts. 

Access to push to ECR is granted to GitHub organisations/repos identified by the customer. 
Interaction with ECR should happen through github actions in the customers repositories. 
We have created two simple actions to aid with this. [Tagging and pushing](https://github.com/jppol-idp/tag-and-push-ecr)
and the less flexible [build and push](https://github.com/jppol-idp/build-and-push-ecr). (Both available
at GitHub Marketplace.)


# Setup - internal reminder
1. Groups for ArgoCD and Grafana should be created 
2. Users should be assigned to the correct groups
3. Groups _identifiers_ should be used to configure Grafana access in the repo `idp-eks-tooling`
4. Groups _name_ should be used to configure access to ArgoCD in `idp-main-setup`
5. The application repository is created and linked in idp-main-setup
6. Access to the application repository should be granted by creating a new github group in jppol-idp and assign access to relevant users. 


# Document revisions
2025-02-05: First version
