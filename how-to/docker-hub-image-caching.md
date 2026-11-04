---
title: Docker Hub Image Caching
nav_order: 14
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-11-02
review_in: 6 months
---

# Docker Hub Image Caching

## Background

Docker Hub enforces [rate limits on image pulls](https://docs.docker.com/docker-hub/usage/pulls/), counted per IP address for anonymous pulls.

In shared Kubernetes environments, these limits can be quickly exceeded, causing:
- Failed pod deployments (ImagePullBackOff errors)
- Service disruptions during scaling events
- Deployment delays
- HTTP 429 "Too Many Requests" errors

To prevent these issues, we've implemented an automatic caching solution that stores Docker Hub images in our own AWS ECR registry.

## How It Works

To use the ECR cache for your Docker Hub images, you need to update your deployment manifests to point to the cache:

1. **Update your image reference** to use the ECR cache URL
2. **Deploy the updated manifest** to your cluster
3. **The image is pulled through ECR**, which caches it from Docker Hub on first use
4. **Subsequent pulls are served from the cache**, avoiding Docker Hub rate limits

### Image Path Mapping

The path structure depends on the image type:

**Official Docker Hub images** (nginx, redis, postgres, etc.) require the `/library/` prefix:
```yaml
# Original
image: nginx:latest

# ECR cache path
image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/docker-hub/library/nginx:latest
```

**User or organization images** (no `/library/` prefix):
```yaml
# Original
image: grafana/grafana:latest

# ECR cache path
image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/docker-hub/grafana/grafana:latest
```

### Examples

**Official image (nginx):**
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
          image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/docker-hub/library/nginx:latest
```

**Organization image (Grafana):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoring
spec:
  template:
    spec:
      containers:
        - name: grafana
          image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/docker-hub/grafana/grafana:latest
```

## Supported Images

The cache works for all Docker Hub images, once the image reference points to the ECR cache path:

| Image Type | Example | ECR cache path |
|------------|---------|----------------|
| Official images | `nginx:latest` | `docker-hub/library/nginx:latest` |
| Official with docker.io | `docker.io/nginx:latest` | `docker-hub/library/nginx:latest` |
| User/organization images | `grafana/grafana:latest` | `docker-hub/grafana/grafana:latest` |
| User/organization with docker.io | `docker.io/grafana/grafana:latest` | `docker-hub/grafana/grafana:latest` |

Images from **other registries cannot be pulled through this cache**:
- `public.ecr.aws/owner/image` - Amazon ECR Public
- `gcr.io/project/image` - Google Container Registry
- `quay.io/organization/image` - Quay.io
- `ghcr.io/owner/image` - GitHub Container Registry
- Images already in ECR


## Benefits

- **No rate limiting**: Eliminates Docker Hub 429 errors
- **Faster deployments**: Images are pulled from ECR in the same AWS region
- **Improved reliability**: Reduces dependency on Docker Hub availability
- **ArgoCD compatible**: Syncs correctly with GitOps workflows

## Troubleshooting

### My pod shows ImagePullBackOff

Check the pod events to see the specific error:
```bash
kubectl describe pod <pod-name> -n <namespace>
```

If the error mentions ECR authentication or "not found", check that the image path follows the mapping above (official images need `/library/`). If it still fails, write to the IDP team in your team's onboarding channel on Slack.


### I want to verify my image is cached

You can check the actual image being used:
```bash
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].image}'
```

This should show an ECR URL starting with `354918371398.dkr.ecr.eu-west-1.amazonaws.com/docker-hub/`.

## Additional Information

For questions or issues, write to the IDP team in your team's onboarding channel on Slack.
