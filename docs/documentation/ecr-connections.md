# ECR repositories

To connect a docker image to a service in IDP, the image must 
be pushed to a repository in the registry in account 354918371398 
jppol-idp-shared. 

Repositories are for now defined in the GitHub repository jppol-idp/idp-main-setup

In this document, we will use KOA as example. 

# Overall structure 
Push access to ECR is granted  using GitHubs OIDC provider and access can be granted to 
either organisations or specific repositories. 

Access from EKS is granted as a resource policy on each repository in ECR. This is granted 
to the set of accounts running the clusters for a given department. 

# Examples 
Repositories and access for KOA repositories is defined in the file 
(infrastructure/(account )[https://github.com/jppol-idp/idp-main-setup/blob/main/infrastructure/accounts/jppol-idp-shared/354918371398/01.koa-ecr/main.tf]

## Repository configuration

Then this file was created the ECR definitons for KOA was as shown below. 

The `ecr-repositories` simply contains all repositories to be created. (And cannot 
collide with existing repository names in the account.) This is the most likely
candidate to be changed as more repositories are needed.

`account_access` is setup at creation time and maintained by EDP. 

`github_access` defines which github repositories can push to the ECR repositories 
listed. Both `organisation` and `repository` can contain a wildcard in the form of an asterisk. 

```
module "ecr-koa" {
  source = "../../../../modules/ecr-repos"

  ecr-repositories = [ "giftcard-service" ]

  account_access = [
    {
      description = "aws-koa-dev"
      account_id  = "931827427725"
      can_write   = false
    },
    {
      description = "aws-koa-test"
      account_id  = "615205931730"
      can_write   = false
    },
    {
      description = "aws-koa-prod"
      account_id  = "151484623076"
      can_write   = false
  }]

  github_access = {
    role_name = "koa-github-ecr-access"
    github_repositories = [
      {
        "organisation" = "JPPOL-KOA"
        "repository"   = "GiftCardService"
      }
    ]
  }
}
```

After a GitHub repository has been granted access to a specific ECR repository, 
images can be built and pushed using an action with the steps illustrated below. 


## Building and pushing 
The following example demonstrates how to build and push an image from a GitHub action. 

The structure is: 
- Checkout code
- Configure AWS credentials
- Login to ECR
- Build and push docker image

The most interesting steps are of course "Configure AWS credentials" where the input 
`role-to-assume` is important. This is output from the Tofu code in the above mentioned 
definition file. (The role is static after first apply.)

The "Login to Amazon ECR" uses input `registries` with value `354918371398`. This is the `jppol-idp-shared`
account which will be used by all IDP hosted clusters. 

```
name: Build docker image
on:
  push:
jobs:
  build_and_push:
    runs-on: ubuntu-24.04
    permissions: write-all
    strategy:
      fail-fast: false
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::354918371398:role/idp-test-access
          aws-region: eu-west-1
          role-skip-session-tagging: true

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2
        with:
          registries: 354918371398
      - name: Build image
        id: build-image
        shell: bash
        env:
          DOCKER_IMAGE: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/monkey-business
          IMAGE_TAG: latest
        run: |
          docker build . -t $DOCKER_IMAGE:$IMAGE_TAG
          docker push  $DOCKER_IMAGE:$IMAGE_TAG
```
