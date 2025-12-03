# PostgreSQL Database Provisioning - User Guide

## Overview

This guide explains how to provision a PostgreSQL database in the IDP AWS Aurora Serverless cluster. Each Kubernetes cluster has access to its dedicated Aurora database cluster.

## Provisioning a Database

### Step 1: Create Application Directory

Create a directory for your database application in the appropriate namespace:

```bash
mkdir -p apps-idp/apps/<namespace>/<your-database-app>
cd apps-idp/apps/<namespace>/<your-database-app>
```

Example:
```bash
mkdir -p apps-idp/apps/idp-dev/my-app-db
cd apps-idp/apps/idp-dev/my-app-db
```

### Step 2: Create `application.yaml`

Create an `application.yaml` file with the following content:

```yaml
Version: v2
name: my-app-db
description: Database for my application
version: 0.1.0
slackChannel: your-slack-channel
helm:
  chart: helm/idp-tenantdatabase
  chartVersion: "3.7.0"  # Use latest version
```

### Step 3: Create `values.yaml`

Create a `values.yaml` file to configure your database:

**Production Database (recommended):**
```yaml
tenantDatabases:
  - name: my-app-db
    namespace: my-namespace
    # Production defaults - all protection enabled
    # deletionProtection: true (default)
    # roleDeletionPolicy: Orphan (default)
    # dbDeletionPolicy: Orphan (default)
```

**Test/Development Database:**
```yaml
tenantDatabases:
  - name: my-test-db
    namespace: my-namespace
    deletionProtection: false
    roleDeletionPolicy: Delete
    dbDeletionPolicy: Delete
```

### Step 4: Commit and Deploy

1. Commit your changes to git
2. ArgoCD will automatically detect and deploy your database
3. Monitor deployment status in ArgoCD UI or CLI

### Step 5: Verify Database Creation

Check database status:

```bash
# List all tenant databases
kubectl get tenantdatabases -n <namespace>

# Get detailed status
kubectl describe tenantdatabase <db-name> -n <namespace>

# Check if database is ready
kubectl get tenantdatabase <db-name> -n <namespace> -o jsonpath='{.status.conditions}'
```

### Step 6: Connect Your Application

After successful creation, configure your application with these environment variables:

```yaml
env:
  - name: DB_NAME
    value: my-app-db
  - name: DB_USER
    valueFrom:
      secretKeyRef:
        name: my-app-db-secret  # Auto-generated secret
        key: username
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: my-app-db-secret
        key: password
  - name: DB_HOST
    valueFrom:
      secretKeyRef:
        name: my-app-db-secret
        key: endpoint
  - name: DB_PORT
    valueFrom:
      secretKeyRef:
        name: my-app-db-secret
        key: port
```

## Configuration Parameters

| Parameter | Description | Default | Values |
|-----------|-------------|---------|--------|
| `name` | Database name (unique per namespace) | Required | String |
| `namespace` | Kubernetes namespace | Required | String |
| `deletionProtection` | Enable deletion protection finalizer | `true` | `true`, `false` |
| `roleDeletionPolicy` | Role deletion behavior | `Orphan` | `Orphan`, `Delete` |
| `dbDeletionPolicy` | Database deletion behavior | `Orphan` | `Orphan`, `Delete` |

## Deletion Protection

### Default Protection (Production)

All databases are protected by default with three layers:

1. **Deletion Protection Finalizer** - Must be manually removed by platform engineers
2. **Orphan Deletion Policy** - Database and roles preserved even if Kubernetes resource is deleted
3. **ArgoCD Sync Protection** - Cannot be deleted via ArgoCD sync operations

### Deleting a Database

**Users cannot delete databases directly.** Contact platform engineers with:

- Database name and namespace
- Business justification
- Backup confirmation
- Approval from team lead

Platform engineers will follow the deletion procedure documented in `DELETION_GUIDE.md`.

### Test Databases

For non-production databases, you can disable protection:

```yaml
tenantDatabases:
  - name: my-test-db
    namespace: test-namespace
    deletionProtection: false
    roleDeletionPolicy: Delete
    dbDeletionPolicy: Delete
```

This allows normal deletion via ArgoCD/kubectl.

## Backup

**TODO:** Automated backup procedures are planned.

Current state:
- Aurora cluster has automated snapshots (AWS managed)
- Point-in-time recovery available via AWS
- Application-level backups: implement manually if needed

## Monitoring

**TODO:** Monitoring dashboards and alerts are planned.

Current monitoring options:
- CloudWatch metrics via AWS Console
- Database connection status via kubectl
- Application-level monitoring via your own tools

## Troubleshooting

### Database Not Ready

```bash
# Check detailed status
kubectl describe tenantdatabase <db-name> -n <namespace>

# Look for unready resources in the message
# Common issues: secretsmanager secrets, role creation, connectivity
```

### Connection Issues

1. Verify secret exists:
```bash
kubectl get secret <db-name>-secret -n <namespace>
```

2. Check secret contents (base64 encoded):
```bash
kubectl get secret <db-name>-secret -n <namespace> -o yaml
```

3. Verify network connectivity from your pod to Aurora cluster

### Force Delete Stuck Resource (Platform Engineers)

```bash
# Remove finalizers
kubectl patch tenantdatabase <db-name> -n <namespace> \
  --type json \
  -p='[{"op": "remove", "path": "/metadata/finalizers"}]'

# Delete resource
kubectl delete tenantdatabase <db-name> -n <namespace>
```

## Support

- **Slack:** #idp-support or your configured slackChannel
- **Documentation:** `helm-idp-postgresql/README.md`
- **Deletion Guide:** `helm-idp-postgresql/DELETION_GUIDE.md`

## Quick Reference

```bash
# List all databases across namespaces
kubectl get tenantdatabases --all-namespaces

# Check database status
kubectl get tenantdatabase <name> -n <namespace>

# View database details
kubectl describe tenantdatabase <name> -n <namespace>

# List Crossplane database resources
kubectl get databases.postgresql.sql.crossplane.io -A
```
