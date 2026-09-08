---
title: Kubernetes Namespace Access via AWS SSO
nav_order: 16
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-09-08
review_in: 12 months
---

# Access to Individual Kubernetes Namespaces via AWS SSO

In each cluster account, the AWS access portal shows Permission Sets that grant access to specific Kubernetes namespaces. Access is generally mapped to the "argo-write" group from the same account, so if you already have that group you already have the relevant access.

These permissions are primarily meant for obtaining kubectl access (viewing pods and logs and port-forwarding to services) rather than for signing in to the AWS Console.

If your deployment uses helm/idp-advanced ≥ 2.4.1 and the namespace is configured for it, you can also assume your deployments' IRSA roles from your laptop to debug access or work with resources (for example DynamoDB tables) provisioned via idp.

## Before you start (prerequisites)
- AWS CLI v2 installed and configured
- kubectl and kubectx installed
- Bash (macOS/Linux) or PowerShell (Windows); login scripts are provided for both
- For IRSA role assumption from your laptop: helm/idp-advanced ≥ 2.4.1 in your deployment

## Quick start
Your apps-"team" repository holds the scripts and examples for your namespaces. Each namespace has a README.md that is kept up to date with cluster-specific information (DNS domains, links, etc.). The READMEs live at `apps-"team"/apps/"team"-"env"` (for koa-dev, for example, `apps-koa/apps/koa-dev`).

To connect, run the login script for your namespace:
```
./scripts/idp-ns-<namespace>.sh
```
This sets up an AWS profile and a kubectl context, both named `idp-ns-<namespace>`. On Windows, use the PowerShell equivalents under `scripts/powershell/`. The namespace README documents the exact commands and options.

## What the access allows
Within your own namespace you get read access and port-forwarding, but no write access.

| Operation | Allowed? |
|---|---|
| View pods, services, config, deployments, jobs, ingresses (`get`/`list`/`watch`) | Yes |
| Read pod logs (`kubectl logs`) | Yes |
| Pod and container metrics (`kubectl top`) | Yes |
| Port-forward to a pod or service in your namespace | Yes |
| Port-forward via the `rds-proxy` namespace | Yes |
| List the cluster's namespaces (`kubectl get namespaces`) | Yes |
| Exec into or attach to a pod (`kubectl exec`, `kubectl attach`) | No |
| Create, edit, delete or scale any resource | No |
| Read Secret objects (`kubectl get secret`, see [Secrets](#secrets) below) | No |
| Access another team's namespace | No |
| Nodes or other cluster-scoped resources | No |

Validate what you have with `kubectl auth can-i`:
```
kubectl auth can-i get pods -n <namespace> --context idp-ns-<namespace>
kubectl auth can-i create pods/portforward -n <namespace> --context idp-ns-<namespace>
```

### Production notes
Assuming deployment (IRSA) roles is enabled per namespace and is typically not granted in production; where it is not, you can still perform the read operations above. Access mapping can differ between clusters, so check your namespace-specific README. If you do not see a Permission Set for your namespace at all, it may not be configured for SSO login yet; reach out to the IDP team in your onboarding channel.

## Secrets
Kubernetes Secret objects are not readable through kubectl. To read the values behind your app's secrets (database logins and other credentials), use AWS Secrets Manager: you can see all secret names in the account, but you can only retrieve versions and values for entries under the path `customer/<namespace>`. See [Working with Secrets](/how-to/secrets.html).

## Related guides
- [Aurora RDS Proxy Local Access Setup Guide](/how-to/aurora-rds-proxy.html) and [pgAdmin Database Management](/how-to/pgadmin.html): using the `rds-proxy` port-forward to reach your database
- [Working with Secrets](/how-to/secrets.html)

## Troubleshooting
- Ensure `aws sso login` is done against the correct profile (`idp-ns-<namespace>`).
- Verify your context: `kubectl config get-contexts` and `kubectx`.
- Check authorization with:
```
kubectl auth can-i get pods -n <namespace> --context idp-ns-<namespace>
kubectl auth can-i create pods/portforward -n <namespace> --context idp-ns-<namespace>
```
