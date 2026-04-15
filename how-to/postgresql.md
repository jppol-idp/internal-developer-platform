---
title: Working with PostgreSQL
nav_order: 21
parent: How to...
domain: public
permalink: /how-to-postgresql
last_reviewed_on: 2026-01-28
review_in: 3 months
---
# Working with Postgres

## Introduction

This guide shows how to add a PostgreSQL database to your application using the [idp-postgresql chart](https://github.com/jppol-idp/helm-idp/tree/main/charts/idp-postgresql). Databases are provisioned inside an IDP-managed Aurora Serverless v2 cluster and can be connected to your application through Kubernetes secrets. If you want to learn more about what Aurora is and how it works, please refer to [the official documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.how-it-works.html).

One Aurora Serverless v2 cluster is provisioned per Kubernetes cluster. Each Aurora cluster will therefore contain multiple tenants. To ensure a level of separation between tenants, databases are prefixed with the tenants' Kubernetes namespace, and the roles provisioned with each database are only granted privileges to the database they belong to.

If you are interested in getting started with Postgres, please reach out in your idp onboarding Slack channel and ask to have it enabled.

---

## Table of contents

{: .no_toc }

- TOC
{:toc}

---

## Define your Database

In your apps repository add a new subfolder in the relevant namespace folder.

Now define a `values.yaml` file describing the database you want to provision:

```yaml
postgresqlDatabases:
  - name: my-db
    mode: standard
```

Mode can be either `standard` or `protected`. Using mode protected enables deletion protection. **Deletion protection should be enabled for production databases.** Enabling deletion protection will ensure the database in the Aurora cluster is not deleted if the database definition in the apps repository is deleted. If a protected database is accidentally deleted from the apps repo, follow the guide in [backup and restore](#restore-protected-database-which-has-been-removed-from-apps-repo). For a list of all possible configuration options in values.yaml see [README](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-postgresql/README.md).

Next you need to create an `application.yaml` in the same subfolder in order to instruct ArgoCD how to create your app and deploy the chart:

```yaml
apiVersion: v2
name: my-db
description: my-db
version: 0.1.0
slackChannel: my-slack-channel
helm:
  chart: helm/idp-postgresql
  chartVersion: "1.0.1" # Check https://github.com/jppol-idp/helm-idp/tree/main/charts/idp-postgresql for the latest version
```

Once this is committed, ArgoCD will automatically deploy the database. Expect the database to be fully ready in 1-3 minutes.

### Database roles

In addition to the database, multiple other resources are created. Namely 3 different roles:

- `[namespace]-[database]-read`
- `[namespace]-[database]-write`
- `[namespace]-[database]-admin`

The `admin` role is the owner of the public schema and is able to create more schemas in the database. However, when creating schemas besides public, the read and write users are not automatically granted privileges to the schemas.

The `read` role is granted read privileges (SELECT) on all tables created by the admin user in the public schema.

The `write` role is granted write privileges (SELECT, INSERT, UPDATE, DELETE, TRUNCATE) on all tables created by the admin user in the public schema.

The credentials for the roles are stored as AWS secrets along with the connection details. The secrets are stored as `customer/[namespace]/[role]`.

## Connect to Postgres

You can connect to Postgres either via your application in the Kubernetes cluster, a managed pgAdmin instance, or by proxying through RDS proxy.

### Connect your Application

Once the database is created, configure your application to use it. Consider what level of privileges your app requires and select a role accordingly. Update your app’s values.yaml to load these as environment variables:

```yaml
env:
  - name: DB_NAME
    value: [namespace]-[database]
  - name: DB_USER
    valueFrom:
      secretKeyRef:
        name: [namespace]-[database]-[read/write/admin]
        key: username
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: [namespace]-[database]-[read/write/admin]
        key: password
  - name: DB_HOST
    valueFrom:
      secretKeyRef:
        name: [namespace]-[database]-[read/write/admin]
        key: endpoint
  - name: DB_PORT
    valueFrom:
      secretKeyRef:
        name: [namespace]-[database]-[read/write/admin]
        key: port
```

For example, when deploying `my-db` to the `idp-dev` namespace:

```yaml
env:
  - name: DB_NAME
    value: idp-dev-my-db
  - name: DB_USER
    valueFrom:
      secretKeyRef:
        name: idp-dev-my-db-write
        key: username
(...)
```

### Connect via pgAdmin

You can use the shared [pgAdmin](https://public.docs.idp.jppol.dk/how-to-pgadmin) deployment if you prefer a web-based interface.

### Connect via local development environment or database tool

The IDP platform provides a shared RDS proxy that allows you to connect to your database from your local machine. This is useful for:

- Running your application locally against a real database
- Using database tools like pgAdmin, DBeaver, or DataGrip

Start by following [this guide](https://public.docs.idp.jppol.dk/kubernetes-namespace-access) to get kubectl access. Then port-forward the rds-proxy to your local machine:

```bash
kubectl port-forward -n rds-proxy svc/rds-proxy-idp-rds-proxy 5432:5432
```

Let the terminal run to keep the connection alive.

Retrieve the username and password for your database role from the corresponding secret in aws secretsmanager.

Connect your local application or database tool using:

- **Host:** localhost
- **Port:** 5432
- **Database:** NAMESPACE-DATABASE (e.g., `idp-dev-my-db`)
- **Username/Password:** from the secret above

## Monitoring

[Prometheus Postgres Exporter](https://grafana.com/oss/prometheus/exporters/postgres-exporter/) collects Postgres specific metrics, while CloudWatch metrics provide health and performance metrics from the shared Aurora serverless v2 cluster. Metrics from both sources can be viewed in Grafana. For an example on how to use the metrics, see the `PostgreSQL database example` dashboard.

## Backup and Restore

### Snapshot retention

Automated snapshots are taken daily by the Aurora cluster between 02:00 and 04:00 CEST:

- **Production/Staging:** 35 days of snapshots
- **Test/Dev:** 7 days of snapshots

### Disaster recovery from snapshot using pgAdmin

To restore a database from a snapshot using pgAdmin, follow these steps:

1. **Contact the IDP team** via the [idp-team Slack channel](https://jppol.slack.com/archives/C09JUREPVBP) and request a restore.
2. **Find a suitable snapshot** together with the IDP team.
3. **IDP initializes a restore cluster** from the selected snapshot.
4. **Connect to the restore cluster** using pgAdmin:
   - Get the new restore Aurora RDS cluster endpoint from the IDP team.
   - Use the web version of pgAdmin at [https://pgadmin.<namespace>.idp.jppol.dk/browser/](https://pgadmin.<namespace>.idp.jppol.dk/browser/).
5. **Take a backup of the desired database** from the restore cluster:
   - In pgAdmin, right-click the database and select *Backup*.
   - Select **Custom** as the format.
   - **Important:** Select the correct admin role for the database (e.g. `NAMESPACE-DATABASE-admin`).
   - Click *Backup*.
6. **Connect to the primary DB cluster** in pgAdmin.
7. **Restore the database** on the primary cluster:
   - In pgAdmin, right-click the database and select *Restore*.
   - Select the backup file from step 5.
   - Under *Query Options*, **enable "Clean before restore"**.
   - Select the admin role for the database.
   - Click *Restore*.
8. **Notify the IDP team** so they can shut down the restore cluster.

### Disaster recovery without pgAdmin, using psql scripts directly from restore container

pgAdmin is likely not a suitable tool for restoring large databases. The restore procedure for large databases is a work in progress.

### Restore protected database which has been removed from apps repo

*The import of protected databases is not yet an automated process as of idp-postgresql helm chart version 1.0.1*

If a deletion protected database has accidentally been deleted from your apps repo, the actual database in the Aurora cluster and the other resources have not been deleted. Only the Kubernetes objects which represents the resources have been deleted.

To "restore" the protected database in this context means to bring it under management again. This scenario can be compared to deleting the Terraform state without letting Terraform reconcile the infrastructure, and then importing the infrastructure into the state to be able to control it with Terraform again.

The first step is to contact IDP as some of these steps requires elevated privileges.

The service using the database only strictly needs the secrets in Kubernetes to connect to the database. As mentioned previously, there is currently no automated way to import protected databases. The quick fix is to create 3 externalsecrets (one for each role) so that the service is still able to connect to the database after a restart. Create the externalsecrets similar to:

```bash
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: [namespace]-[database]-[read/write/admin]
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets
    kind: ClusterSecretStore
  target:
    name: [namespace]-[database]-[read/write/admin]
  data:
    - secretKey: username
      remoteRef:
        key: customer/[customer]/[database]-[read/write/admin]
        property: username
    - secretKey: password
      remoteRef:
        key: customer/[customer]/[database]-[read/write/admin]
        property: password
    - secretKey: endpoint
      remoteRef:
        key: customer/[customer]/[database]-[read/write/admin]
        property: endpoint
    - secretKey: port
      remoteRef:
        key: customer/[customer]/[database]-[read/write/admin]
        property: port
```

## SSL configuration

It is required that connections to your database are established using SSL. As a minimum, you should set `sslmode` to `require` in your connection string / connection settings. The different SSL modes are documented in the [Postgres docs](https://www.postgresql.org/docs/11/libpq-ssl.html#LIBPQ-SSL-SSLMODE-STATEMENTS). When setting `sslmode` to `require`, data sent over the connection is encrypted but the identity of the server is not verified.

It is recommended, but not required, that connections to production databases are established using `sslmode` equals `verify-full`. This encrypts data sent over the connection, and the identity of the server is cryptographically verified. This does however require that you include and configure some extra certs in your container. Note that the certificates might already be baked into your container image or installed via a package manager. A guide to installing AWS' certs can be found on the following AWS docs page: [Using SSL with a PostgreSQL DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Concepts.General.SSL.html#PostgreSQL.Concepts.General.SSL.Connecting)

## Database engine updates

The IDP team manages all PostgreSQL engine updates on the shared Aurora cluster. Routine maintenance runs nightly between 02:00–04:00 UTC.

**OS patches and minor version updates** are applied during the maintenance window using zero-downtime patching. OS patches take under 5 minutes; minor version upgrades typically complete in a few seconds. A very small number of active connections may be dropped during the cutover.

**Major version updates** are performed using blue-green deployments outside the regular maintenance window. A fully replicated copy of the cluster is created, verified, and then switched over with a cutover that takes under 5 minutes. The IDP team will announce the window in advance. During the replication phase, **DDL changes (schema changes, `CREATE`/`DROP TABLE`, etc.) must not be applied** — they will block the switchover. The IDP team will coordinate with you on timing.

If you have questions about an upcoming update, reach out in your onboarding Slack channel.

## Migrating an existing database to IDP

If you have an existing PostgreSQL database outside the IDP platform and want to move it onto the IDP-managed Aurora cluster, the general approach is to provision a new IDP database, migrate the data, and then update your application to point to the new connection details.

KOA has documented their migration experience in a playbook that is a useful reference: [Postgres DB IDP Migration Playbook](https://jira-jppol.atlassian.net/wiki/spaces/KOA/pages/4238114819/Postgres+DB+IDP+Migration+Playbook).

## Common errors

### no pg_hba.conf entry for host

If you get an error saying:

```
no pg_hba.conf entry for host (...)
```

Then you need to set `sslmode` to `require` in your connection string / connection settings. See section on [SSL configuration](#ssl-configuration) for a more in detail explanation.
