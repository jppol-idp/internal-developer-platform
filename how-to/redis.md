---
title: Working with Redis
nav_order: 13
parent: How to...
domain: public
permalink: /how-to-redis
last_reviewed_on: 2025-12-01
review_in: 6 months
---
# Deploying Redis

Deploy Redis in your IDP cluster. The `idp-redis` Helm chart supports two deployment modes: standalone Redis (single instance) and Redis with replication and automatic failover via Sentinel.

**Chart**: `helm/idp-redis` from https://github.com/jppol-idp/helm-idp-redis

## Create your deployment files

Create two files in your namespace directory:

### 1. application.yaml

```yaml
apiVersion: v2
name: my-redis-deployment
description: Redis deployment with replication
version: 0.1.0
helm:
  chart: helm/idp-redis
  chartVersion: "0.3.5"              # Use latest available version
```

Replace:
- `my-redis-deployment` with your deployment name
- `0.3.5` with the desired chart version

### 2. values.yaml

This file configures your Redis deployment. Start with either **standalone** or **replication** mode below.

## Deployment modes

### Standalone mode

Single Redis instance for development or non-critical caching.

```yaml
# values.yaml
type: standalone

standalone:
  # Resource requests and limits (important for Redis memory management!)
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      memory: 256Mi

  persistence:
    enabled: false              # no disk storage (memory only)
    # size: 1Gi                 # if enabled=true, storage size

monitoring:
  enabled: true                 # enable Prometheus metrics
```

### Replication mode (recommended for production)

Master-slave Redis with automatic failover via Sentinel.

```yaml
# values.yaml
type: replication

replication:
  size: 3                        # 1 master + 2 slaves

  # Resource requests and limits (important for Redis memory management!)
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      memory: 256Mi

  persistence:
    enabled: true
    size: 10Gi                   # storage per Redis pod

sentinel:
  size: 3                        # 3 Sentinel instances

  # Resource requests and limits for Sentinel instances
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      memory: 128Mi

  persistence:
    enabled: true
    size: 1Gi                    # storage per Sentinel pod

monitoring:
  enabled: true                  # enable Prometheus metrics
```

**What you get**:
- 3 Redis pods: 1 master, 2 slaves
- 3 Sentinel pods for automatic failover
- Services for master, slave, and sentinel access
- Automatic metrics export to Prometheus

**Note**: The Sentinel master name is configured as `myMaster` (not the default `mymaster`). Use this name when connecting to Redis via Sentinel.

## Resource management

Redis is a memory-based key-value store, so setting appropriate resource requests and limits is critical for:
- Preventing out-of-memory errors
- Ensuring fair resource allocation in shared clusters
- Maintaining predictable performance
- Controlling QoS class (Quality of Service)

### Understanding QoS classes

Kubernetes assigns QoS classes based on requests and limits:

- **Guaranteed**: `requests == limits` for all containers. Highest priority, never evicted under memory pressure.
- **Burstable**: `requests < limits` or only requests set. Medium priority, evicted if needed.
- **BestEffort**: No requests or limits. Lowest priority, evicted first under memory pressure.

For production Redis deployments, **Guaranteed QoS is recommended** to prevent evictions.

### Recommended values

**Development/Non-critical:**

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    memory: 256Mi           # Burstable QoS
```

**Production (recommended):**

```yaml
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    memory: 1Gi             # Guaranteed QoS (request == limit)
```

Apply these values to `standalone`, `replication`, and `sentinel` sections as shown in the examples above.

## Customizing your deployment

### Redis version

Override the Redis version in `values.yaml`:
More configuration options can be found in the [repositorys values.yaml](https://raw.githubusercontent.com/jppol-idp/helm-idp-redis/refs/heads/main/values.yaml?token=GHSAT0AAAAAADPEM222HW6JIHFNPFK7LWPK2JNV5WA)

```yaml
global:
  image:
    tag: "8.0.4"                # change from default 8.2.2
```

### Storage size

Adjust storage per pod:

```yaml
replication:
  persistence:
    size: 20Gi                  # storage per Redis pod

sentinel:
  persistence:
    size: 2Gi                   # storage per Sentinel pod
```

### Number of replicas

Change replication factor (number of slaves):

```yaml
replication:
  size: 5                        # 1 master + 4 slaves
```

Apply changes by committing your updated `values.yaml` to git. ArgoCD will detect and apply changes automatically.

## Accessing Redis

Services are created automatically for different use cases:

| Service | Port | Use case |
|---------|------|----------|
| `redis` | 6379 | Any Redis node (includes master and slaves) |
| `redis-master` | 6379 | Master only (for writes) |
| `redis-replica` | 6379 | Slaves only (for reads) |
| `redis-sentinel` | 26379 | Sentinel for monitoring/failover |

Use the service name from within your namespace:

```
redis-master:6379                    # master for writes
redis:6379                           # any node for reads
redis-sentinel:26379                 # sentinel (master name: myMaster)
```

**Important**: When connecting via Sentinel, the master name is `myMaster` (not the default `mymaster`).

### Example: Connecting from your application

From a pod in your namespace, connect using service DNS:

```python
import redis

# Connect to master
r = redis.Redis(host='redis-master', port=6379, decode_responses=True)

# Or to any node
r = redis.Redis(host='redis', port=6379, decode_responses=True)
```

## Authentication (optional)

The chart supports two methods for Redis authentication:

### Method 1: AWS Secrets Manager via ExternalSecret (recommended for production)

This method automatically syncs passwords from AWS Secrets Manager to Kubernetes.

**Prerequisites:**
- SecretStore `aws-secrets-{{ namespace }}` configured in your cluster
- Secret created in AWS Secrets Manager via GitHub Action
- Pod IAM role (IRSA) configured for AWS access

**How to set up:**

1. **Create secret in AWS Secrets Manager**

   Use the GitHub Action in your customer repository. See your namespace's `secrets.md` file for instructions.

   Example for `idp-dev` namespace: https://github.com/jppol-idp/apps-idp/blob/main/apps/idp-dev/secrets.md

   When creating the secret, specify:
   - `secretsmanager_name: redis-password`
   - `password: <your-secure-password>`

   This creates the secret at: `customer/{{ namespace }}/redis-password`

2. **Enable authentication in values.yaml:**

   ```yaml
   auth:
     enabled: true
     secretName: redis-password    # Matches the secretsmanager_name from GitHub Action
   ```

3. **Commit and deploy**

   Commit changes to git. ArgoCD will detect and apply the deployment. The chart automatically generates an ExternalSecret resource that syncs your password from AWS Secrets Manager.

### Method 2: Existing Kubernetes Secret (alternative)

If you already have a Kubernetes secret you want to use instead of ExternalSecret:

**Configuration in values.yaml:**

```yaml
auth:
  enabled: true
  secretName: my-redis-password
  externalSecretDisabled: true    # Disable ExternalSecret generation
```

**Requirements:**
- Kubernetes secret must exist with key `password`
- Secret name must match: `{{ release-name }}-password`

For details on how to create and manage the Kubernetes secret, contact your platform team.

### Accessing authenticated Redis

Use the password in your application connection strings:

```python
import redis

# Connect to master
r = redis.Redis(
    host='redis-master',
    port=6379,
    password='<your-secure-password>',
    decode_responses=True
)
```

Connection string format:
```
redis://default:<password>@redis-master:6379
```

## Monitoring with Prometheus

Metrics are automatically exported when enabled:

```yaml
monitoring:
  enabled: true
```

Metrics are scraped every 30 seconds and include:
- Redis memory usage
- Commands per second
- Connected clients
- Replication lag
- Sentinel status

### Grafana dashboard

A pre-built Grafana dashboard is available in all clusters: **"Redis Dashboard for Prometheus Redis Exporter (helm stable/redis-ha)"**

Use this dashboard to visualize Redis metrics without additional setup configuration.

## Troubleshooting

### Pods stuck in Pending

Usually temporary during startup. Wait 1-2 minutes and refresh.

### Services show no endpoints

Redis Operator is configuring pods. Wait 30-60 seconds for all pods to be Ready.

### Sentinel not deploying (replication mode)

Ensure all Redis pods are `Running` first. Sentinel waits for Redis to be ready.

## Support

For issues or questions:
1. Check your ArgoCD application status
2. Verify pod logs show successful startup
3. Ensure all pods are in `Running` state
4. Contact idp-support.
