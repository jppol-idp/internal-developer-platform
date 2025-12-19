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

## Table Of Contents

- [Create your deployment files](#create-your-deployment-files)
- [Deployment modes](#deployment-modes)
  - [Standalone mode](#standalone-mode)
  - [Replication mode (recommended for production)](#replication-mode-recommended-for-production)
- [Resource management](#resource-management)
  - [Understanding QoS classes](#understanding-qos-classes)
  - [Recommended values](#recommended-values)
- [Customizing your deployment](#customizing-your-deployment)
  - [Redis version](#redis-version)
  - [Storage size](#storage-size)
  - [Number of replicas](#number-of-replicas)
- [Accessing Redis](#accessing-redis)
  - [Finding your service names](#finding-your-service-names)
  - [Which service to use](#which-service-to-use)
  - [Connecting with tools](#connecting-with-tools-redis-insights-redisinsight-redis-cli)
  - [Connecting from your application](#connecting-from-your-application)
- [Authentication (optional)](#authentication-optional)
  - [Method 1: AWS Secrets Manager via ExternalSecret](#method-1-aws-secrets-manager-via-externalsecret-recommended-for-production)
  - [Method 2: Existing Kubernetes Secret](#method-2-existing-kubernetes-secret-alternative)
  - [Accessing authenticated Redis](#accessing-authenticated-redis)
- [Monitoring with Prometheus](#monitoring-with-prometheus)
  - [Grafana dashboard](#grafana-dashboard)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

**Chart**: `helm/idp-redis` from https://github.com/jppol-idp/helm-idp

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
  chartVersion: "0.5.2"
```

Replace:
- `my-redis-deployment` with your deployment name
- `0.5.2` with the latest chart version, which can be found [here](https://github.com/jppol-idp/helm-idp/releases)

### 2. values.yaml

This file configures your Redis deployment. All options can be found [here](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-redis/values.yaml)

Start with either **standalone** or **replication** mode below.

## Deployment modes

### Standalone mode

Single Redis instance for development or non-critical caching.

```yaml
# values.yaml
type: standalone

standalone:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      memory: 256Mi

  persistence:
    enabled: false

monitoring:
  enabled: true
```

### Replication mode (recommended for production)

Master-slave Redis with automatic failover via Sentinel.

```yaml
# values.yaml
type: replication

replication:
  size: 3
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      memory: 256Mi

  persistence:
    enabled: true
    size: 10Gi

sentinel:
  size: 3
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      memory: 128Mi

  persistence:
    enabled: true
    size: 1Gi

monitoring:
  enabled: true
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

Available versions can be found [here](https://quay.io/repository/opstree/redis?tab=tags)

Override the Redis version in `values.yaml`:
More configuration options can be found in the repository's [values.yaml](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-redis/values.yaml)

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

### Finding your service names

When you deploy Redis via Helm, services are automatically created with names based on your **release name** (the `folder-name` of your application in your argo-cd apps folder).

The service naming pattern is: `<release-name>-<service-type>`

**Example**: If your `folder-name` is: my-redis-deployment`, the main services will be:
- `my-redis-deployment-service` (standalone) or `my-redis-deployment-master` (replication)
- `my-redis-deployment-replica` (replication mode only)
- `my-redis-deployment-sentinel` (replication mode only)

**To see your actual service names**, use one of these methods:

1. **ArgoCD GUI** (recommended for developers):
   - Open your application in ArgoCD
   - Look under "Services" - all service names are listed there

2. **kubectl command**:
   ```bash
   kubectl get services -n <your-namespace> | grep redis
   ```

### Which service to use

The service you connect to depends on your deployment mode and use case:

#### Standalone mode

| Service | Port | Use Case |
|---------|------|----------|
| `<release-name>-service` | 6379 | All Redis operations (read and write) |

**Connection example**:
```
<release-name>-service:6379
```

#### Replication mode (with Sentinel)

| Service | Port | Use Case |
|---------|------|----------|
| `<release-name>-master` | 6379 | **Write operations** and direct master access |
| `<release-name>-replica` | 6379 | **Read operations** from slaves |
| `<release-name>-sentinel` | 26379 | **Sentinel monitoring** (not for data operations!) |

**For application connections**:
```
<release-name>-master:6379      # For writes
<release-name>-replica:6379     # For read-only queries
```

**Important**:
- Use `-master` for writes or when you need consistent reads
- Use `-replica` for read-heavy workloads to distribute load
- **Do NOT use `-sentinel` for data operations** - it's only for monitoring and failover coordination

### Connecting with tools (Redis Insights, RedisInsight, redis-cli)

When using tools like Redis Insights with `kubectl port-forward`, connect to the **master service**, not sentinel:

```bash
# Port-forward to master (correct)
kubectl port-forward -n <namespace> svc/<release-name>-master 6379:6379

# Then connect Redis Insights to localhost:6379
```

**Do NOT port-forward to the sentinel service** - it won't give you access to your data.

### Connecting from your application

From a pod in your namespace, use the full service DNS name:

**Standalone mode**:
```python
import redis

# Replace 'my-redis-deployment' with your actual release name
r = redis.Redis(
    host='my-redis-deployment-service',
    port=6379,
    decode_responses=True
)
```

**Replication mode**:
```python
import redis

# For writes - connect to master
r_write = redis.Redis(
    host='my-redis-deployment-master',
    port=6379,
    decode_responses=True
)

# For reads - connect to replicas
r_read = redis.Redis(
    host='my-redis-deployment-replica',
    port=6379,
    decode_responses=True
)
```

**Using Sentinel for automatic failover** (advanced):
```python
from redis.sentinel import Sentinel

# Connect to sentinel for automatic failover handling
sentinel = Sentinel([
    ('my-redis-deployment-sentinel', 26379)
], decode_responses=True)

# Get master for writes (master name is 'myMaster')
master = sentinel.master_for('myMaster', socket_timeout=0.1)

# Get slave for reads
slave = sentinel.slave_for('myMaster', socket_timeout=0.1)
```

**Note**: When using Sentinel in your application, the master name is configured as `myMaster` (not the default `mymaster`).

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

   This creates the secret at: `customer/<namespace>/redis-password`

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

Use the password in your application connection strings with the full service name:

```python
import redis

# Standalone mode
r = redis.Redis(
    host='my-redis-deployment-redis',
    port=6379,
    password='<your-secure-password>',
    decode_responses=True
)

# Replication mode - connect to master
r = redis.Redis(
    host='my-redis-deployment-redis-master',
    port=6379,
    password='<your-secure-password>',
    decode_responses=True
)
```

Connection string format:
```
# Standalone
redis://default:<password>@<release-name>-redis:6379

# Replication (master)
redis://default:<password>@<release-name>-redis-master:6379
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
