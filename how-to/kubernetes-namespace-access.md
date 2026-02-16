---
title: Kubernetes Namespace Access via AWS SSO
nav_order: 7
parent: How to...
domain: public
permalink: /kubernetes-namespace-access
last_reviewed_on: 2025-11-28
review_in: 3 months
---

# Access to Individual Kubernetes Namespaces via AWS SSO (Early Rollout)
We have rolled out an early version of a new way to grant access to individual namespaces over the last few days. There may still be issues, but it is mature enough to start using. We appreciate feedback.

In the various cluster accounts, at the AWS access portal, you will see new Permission Sets that grant access to specific namespaces in Kubernetes. Generally, mapping is to the "argo-write" group from the same account, so you should already have the relevant access.

The intent is not primarily to sign in via the AWS Console, but to use these permissions to obtain kubectl access for viewing pods and logs and doing port-forwarding to services.

If you use helm/idp-advanced ≥ 2.4.1, you can also assume your deployments’ IRSA roles from your laptop to debug access or read (for example) DynamoDB tables provisioned via idp.

## Before you start (prerequisites)
- AWS CLI v2 installed and configured
- kubectl and kubectx installed
- For IRSA role assumption from your laptop: helm/idp-advanced ≥ 2.4.1 in your deployment

## Quick start
Looking at your apps-"team" repository you will find the scripts and examples for your specifix namespaces. The README.md in each namespace is updated at all times and contain cluster-specific information (DNS domains, links, etc.). The READMEs are located in your apps-"team" repository at `apps-"team"/apps/"team"-"env"` (for example, for idp-dev it would be `apps-idp/apps/idp-dev`).

## RBAC baseline and production notes (aligned with platform docs)
- Current Kubernetes RBAC within the namespace is minimal: get on Pods/Services and create on the pods/portforward subresource. This will evolve; validate with kubectl auth can-i.
- Production environments: we do not expect to grant assume-role permissions. You can still perform selected GET operations via kubectl.
- Access mapping on prod systems may not yet be complete; check the namespace-specific README.

## Secrets access
You can view secret metadata for your namespace in the AWS Console or via AWS CLI. While you can see all secret names in the account, you can only retrieve additional information (versions and secret values) for entries under the path customer/<<namespace>>.

## Troubleshooting
- Ensure aws sso login is done against the correct profile (idp-ns-<namespace>).
- Verify your context: kubectl config get-contexts and kubectx.
- Check authorization with:
```
kubectl auth can-i get pods -n <namespace> --context idp-ns-<namespace>
kubectl auth can-i create pods/portforward -n <namespace> --context idp-ns-<namespace>
```

As mentioned, adjustments are expected and some of the documentation may be insider-oriented. The foundation is in place and your feedback will help improve the system.
