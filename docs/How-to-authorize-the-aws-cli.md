# Retrieving AWS credentials to your local laptop

We strictly use JP/Politikens Hus AD via AWS SSO to granting access to the IDP maintained accounts. 

You will be allowed a set of roles that can be assumed. These have limited access, but should allow daily 
use cases. 

## TLDR
You need to 
1. Setup aws sso (once): `aws configure sso`
2. Login to the profile selected `aws sso login --profile koa-dev-customer`
3. Export the credentials to your current session `(aws configure export-credentials --profile koa-dev-customer)`.


## Setting up SSO
Setting up the profile can be done using `aws configure sso` which will guide you through the setup and set the necessary 
configuration files on the local system. 

The most important element is the `SSO Start URL`, which should be *`https://jppol-sso-awsapps.com`* regardless of the account you want to login to. 

`region` is likewise a constant setting as we always use `eu-west-1`. 

For regular IDP customer access we maintain the permission set `idp_customer_access`. Choose this when prompted. 

```
# aws configure sso 
SSO session name (Recommended): koa-dev-customer
SSO start URL [None]: https://jppol-sso.awsapps.com/start
SSO region [None]: eu-west-1
SSO registration scopes [sso:account:access]: sso:account:access
Using the role name "idp_customer_access"
CLI default client Region [None]: eu-west-1
CLI default output format [None]: json
CLI profile name [idp_customer_access-931827427725]: koa-dev-customer
```
The `aws configure sso` stores configuration in `~/.aws/config`
```
[profile koa-dev-customer]
sso_session = koa-dev-customer
sso_account_id = 931827427725
sso_role_name = idp_customer_access
region = eu-west-1
output = json
[sso-session koa-dev-customer]
sso_start_url = https://jppol-sso.awsapps.com/start
sso_region = eu-west-1
sso_registration_scopes = sso:account:access
```

## Assuming SSO configured roles 
AWS sso login can be obtained with various tools. We will focus on the vanilla aws cli. 

The base login command is `aws sso login` with a profile parameter matching one of the already configured profiles. 
In the previous example we configured the profile `koa-dev-customer`, why the entire statement would become. 
``` 
aws sso login --profile koa-dev-customer
```

These credentials can be used in aws cli referencing the same profile. Try `aws sts get-caller-identity --profile koa-dev-customer` to check 
which role you act as against AWS using the profile. 

## Setting environment credentials 
Rather than specifying the `profile` parameter the credentials can also be exported to the environment using 
`aws configure`. The output can be executed/evaluated to modify current environment variables: 

```
aws configure export-credentials --profile koa-dev-credentials --format powershell
```
provides an output similar to 
```

aws configure export-credentials --profile koa-dev-customer --format powershell
$Env:AWS_ACCESS_KEY_ID="ASIA5R5J6FGGZ4HLPB4X"
$Env:AWS_SECRET_ACCESS_KEY="ja4.............................My8"
$Env:AWS_SESSION_TOKEN="IQoJb3.............................XSgA"
$Env:AWS_CREDENTIAL_EXPIRATION="2025-02-07T19:11:00+00:00"
```

To actually set the values in the environment: 
PowerShell - surround by parenthesis: 
```
$(aws configure export-credentials --profile koa-dev-credentials --format powershell )
```




AWS SSO can be used an manipulated in various ways. This document mainly focuses on _Windows_, but aws cli 
is identical on both Linux, MacOS and Windows.
