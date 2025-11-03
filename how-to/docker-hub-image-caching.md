---
title: Docker Hub Image Caching
nav_order: 6
parent: How to...
domain: public
permalink: /docker-hub-image-caching
last_reviewed_on: 2025-11-03
review_in: 6 months
---

# Docker Hub Image Caching

## Background

Docker Hub enforces rate limits on image pulls to manage their infrastructure costs and prevent abuse:

- **Anonymous users**: 100 pulls per 6 hours per IP address
- **Authenticated free users**: 200 pulls per 6 hours per account

In shared Kubernetes environments, these limits can be quickly exceeded, causing:
- Failed pod deployments (ImagePullBackOff errors)
- Service disruptions during scaling events
- Deployment delays
- HTTP 429 "Too Many Requests" errors

To prevent these issues, we've implemented an automatic caching solution that stores Docker Hub images in our own AWS ECR registry.

## How It Works

When you deploy a workload that uses a Docker Hub image, the platform automatically:

1. **Rewrites the image reference** to use our ECR cache
2. **Pulls the image through ECR**, which caches it from Docker Hub on first use
3. **Serves subsequent pulls from the cache**, avoiding Docker Hub rate limits

This happens **transparently** - you don't need to change anything in your deployment manifests.

### Example

Your deployment manifest:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
        - name: app
          image: nginx:latest
```

What actually runs in the cluster:
```yaml
spec:
  containers:
    - name: app
      image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/docker-hub/library/nginx:latest
```

The image is automatically rewritten by the platform, and ArgoCD shows your application as "Synced" despite this difference.

## Supported Images

The caching works for all Docker Hub images:

| Image Type | Example | Automatically Cached |
|------------|---------|---------------------|
| Official images | `nginx:latest` | ✅ Yes |
| Official with docker.io | `docker.io/nginx:latest` | ✅ Yes |
| User/organization images | `grafana/grafana:latest` | ✅ Yes |
| Explicitly prefixed | `docker.io/bitnami/nginx:latest` | ✅ Yes |

Images from **other registries are not affected**:
- `gcr.io/project/image` - Google Container Registry
- `quay.io/organization/image` - Quay.io
- `ghcr.io/owner/image` - GitHub Container Registry
- Images already in ECR

## Opting Out

In rare cases, you may need to disable the caching for a specific workload. Add this annotation to your pod template:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    metadata:
      annotations:
        idp.jppol.dk/ecr-pull-through-cache: "disabled"
    spec:
      containers:
        - name: app
          image: nginx:latest  # Will pull directly from Docker Hub
```

**When to opt-out:**
- Debugging image pull issues
- Testing specific Docker Hub behavior
- Temporary workaround for cache-related problems

**Note**: Opting out makes your workload subject to Docker Hub rate limits again.

## Benefits

- **No rate limiting**: Eliminates Docker Hub 429 errors
- **Faster deployments**: Images are pulled from ECR in the same AWS region
- **Improved reliability**: Reduces dependency on Docker Hub availability
- **Zero configuration**: Works automatically without manifest changes
- **ArgoCD compatible**: Syncs correctly with GitOps workflows

## Troubleshooting

### My pod shows ImagePullBackOff

Check the pod events to see the specific error:
```bash
kubectl describe pod <pod-name> -n <namespace>
```

If the error mentions ECR authentication or "not found", contact the platform team via Slack (#idp-team).

### ArgoCD shows my application as OutOfSync

The platform is configured to ignore image field differences caused by caching. If you're still seeing OutOfSync status specifically related to image fields, contact the platform team.

### I want to verify my image is cached

You can check the actual image being used:
```bash
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].image}'
```

This should show an ECR URL starting with `354918371398.dkr.ecr.eu-west-1.amazonaws.com/docker-hub/`.

## Additional Information

For technical details about the implementation, see:
- [Technical Documentation](/dokumentation/ecr-pull-through-cache)
- [JIRA: IDP-656](https://jira-jppol.atlassian.net/browse/IDP-656)

For questions or issues, contact the platform team via:
- **Slack**: #idp-team
