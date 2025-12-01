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
  persistence:
    enabled: true
    size: 10Gi                   # storage per Redis pod

sentinel:
  size: 3                        # 3 Sentinel instances
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

## Customizing your deployment

### Redis version

Override the Redis version in `values.yaml`:

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
```

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

To add password protection:

1. Ask your platform team to create a Kubernetes secret:
   ```
   redis-password secret with key "password"
   ```

2. Enable auth in `values.yaml`:
   ```yaml
   auth:
     enabled: true
     secretName: redis-password
     secretKey: password
   ```

3. Commit changes. ArgoCD will update the deployment.

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

View metrics in your Prometheus/Grafana dashboard.

## Troubleshooting

### Pods stuck in Pending

Usually temporary during startup. Wait 1-2 minutes and refresh.

If persistent, check storage class:
```
Storage class exists and has available capacity
```

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
