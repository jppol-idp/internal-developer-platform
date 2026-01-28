---
title: Working with PostgreSQL
nav_order: 14
parent: How to...
domain: public
permalink: /how-to-postgresql
last_reviewed_on: 2026-01-28
review_in: 3 months
---
# Add Postgres Database [BETA FEATURE]

## Introduction

This guide shows how to add a PostgreSQL database to your application using the [idp-postgresql chart](https://github.com/jppol-idp/helm-idp/tree/main/charts/idp-postgresql).
Databases are provisioned inside an IDP-managed Aurora cluster and can be connected to your application through Kubernetes secrets.

If you want to learn more about what Aurora is and how it works, please refer to [the official documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.how-it-works.html).

This feature is considered **Beta**, meaning it is functional but still under active development. Some configuration options etc. may change in future releases, and there may be minor bugs or limitations. A list of known errors is presented in the [known errors section](#known-errors) and planned features are presented in the [WIP section](#work-in-progress-features). We recommend using this feature first in development or staging environments and welcome your feedback to help improve it.

If you have an interest in trying the Beta out, please reach out in the [idp-team Slack channel](https://jppol.slack.com/archives/C09JUREPVBP) and ask to have it enabled.

## Define your Database

In your apps repository add a new subfolder in the relevant namespace folder.

Now define a `values.yaml` file describing the database you want to provision:

```yaml
postgresqlDatabases:
  - name: my-db
    deletionProtection: false
```

**Deletion protection should be enabled for production databases.** Enabling deletion protection will ensure the database in the Aurora cluster is not deleted if the database definition in the apps repository is deleted. If a protected database is accidentally deleted from the apps repo, follow the guide in [restore](#restore).

Next you need to create an `application.yaml` in the same subfolder in order to instruct ArgoCD how to create your app and deploy the chart:

```yaml
apiVersion: v2
name: my-db
description: my-db
version: 0.1.0
slackChannel: my-slack-channel
helm:
  chart: helm/idp-postgresql
  chartVersion: "0.5.0"
```

Once this is committed, ArgoCD will automatically deploy the database.

## Grant privileges (optional)

**There are three different database roles created alongside your database: an admin role, a write role and a read role. Follow this section to configure the privileges of the read and write role if you want to use less permissive roles.**

Currently, the admin role can create tables and assign permissions to the other roles via grants while the read and write roles have no default permissions. Out of the box granular role permissions are work in progress. Use the following queries as a cheatsheet for granting privileges. Replace `ipd-dev` with your namespace and `kdb1` with the name of your database.

Grant schema access:

```
GRANT USAGE ON SCHEMA public TO "idp-dev-kdb1-write";
GRANT USAGE ON SCHEMA public TO "idp-dev-kdb1-read";
```

Grant privileges on existing tables:

```
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "idp-dev-kdb1-write";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "idp-dev-kdb1-read";
```

Grant privileges on existing sequences:

```
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO "idp-dev-kdb1-write";
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO "idp-dev-kdb1-read";
```

Set default privileges for future tables created by admin:

```
ALTER DEFAULT PRIVILEGES FOR ROLE "idp-dev-kdb1-admin" IN SCHEMA public         GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "idp-dev-kdb1-write";
```

```
ALTER DEFAULT PRIVILEGES FOR ROLE "idp-dev-kdb1-admin" IN SCHEMA public    GRANT SELECT ON TABLES TO "idp-dev-kdb1-read";
```

Set default privileges for future sequences created by admin:

```
ALTER DEFAULT PRIVILEGES FOR ROLE "idp-dev-kdb1-admin" IN SCHEMA public    GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO "idp-dev-kdb1-write";
```

```
ALTER DEFAULT PRIVILEGES FOR ROLE "idp-dev-kdb1-admin" IN SCHEMA public    GRANT SELECT ON SEQUENCES TO "idp-dev-kdb1-read";
```

## Connect your Application

Once the database is created, configure your application to use it. Depending on which type of role you need to act as, configure your yaml to use the appropriate one. Update your app’s values.yaml to load these as environment variables:

```yaml
env:
  - name: DB_NAME
    value: [namespace]-[database]
  - name: DB_USER
    valueFrom:
      secretKeyRef:
        name: [namespace]-[database]-admin
        key: username
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: [namespace]-[database]-admin
        key: password
  - name: DB_HOST
    valueFrom:
      secretKeyRef:
        name: [namespace]-[database]-admin
        key: endpoint
  - name: DB_PORT
    valueFrom:
      secretKeyRef:
        name: [namespace]-[database]-admin
        key: port
```

For example, when deploying `my-db` to the `idp-dev` namespace:

```yaml
env:
  - name: DB_NAME
    value: idp-dev-my-db
```

## Connect via local development environment or database tool

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

Alternatively, you can use the shared [pgAdmin](https://public.docs.idp.jppol.dk/how-to-pgadmin) deployment if you prefer a web-based interface.

## SSL configuration

It is required that connections to your database is established using SSL. As a minimum, you should set `sslmode` to `require` in your connection string / connection settings. When setting `sslmode` to `require`, data sent over the connection is encrypted but the identity of the server is not verified.

It is recommended, but not required, that connections to production databases are established using `sslmode` equals `verify-full`. This encrypts data sent over the connection, and the identity of the server is cryptographically verified. This does however require that you include and configure some extra certs in your container. A guide to this can be found on the following AWS docs page: [Using SSL with a PostgreSQL DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Concepts.General.SSL.html#PostgreSQL.Concepts.General.SSL.Connecting)

## Upgrade guide

### Version 0.4.1 to 0.5.0

This update changes the underlying resource API version and since no migration mechanism exists between versions, existing resources must be recreated and their data will be lost. Automated migration between resource versions is planned for a future release before general availability.

A few manual steps is required when upgrading a database from postgresqldatabase helm chart version 0.4.1 to 0.5.0. Because secrets prior to version 0.5.0 are soft deleted, they will have to be forcefully deleted in order for crossplane to successfully recreate all the required resources.

(1) Delete the database from your apps repo
(2) Delete the database secrets from aws secretsmanager

Deleting secrets requires elevated privileges, so please contact idp through your onboarding slack channel. For each secret (read, write, admin) run:

```bash
aws secretsmanager delete-secret --secret-id 'customer/NAMESPACE/SECRET' --force-delete-without-recov
ery
```

(3) Readd the database with the new version to your apps repo

## Work in progress features

WIP features:

- Backup and restore
- Monitoring
- PostgreSQL version upgrade strategy

## Restore

### Restore protected database which has been removed from apps repo

Contact IDP as some of these steps requires elevated privileges.

In case the database is accidentally deleted from the apps repo, the resources in Kubernetes is removed while the resources outside of Kubernetes lives on. The service using the database only strictly needs the secrets in Kubernetes to connect to the database. The secrets for the three roles (read, write, admin) can be restored using the following procedure.

The secret data can be found in the corresponding aws secretsmanager secrets.

```bash
kubectl create secret generic NAMESPACE-DB-ROLE -n NAMESPACE --from-literal=endpoint=foo --from-literal=port=5432 --from-literal=username=NAMESPACE-DB-ROLE --from-literal=password=foo
```

Create the secrets for the admin, write, and read roles.

## Known errors

### no pg_hba.conf entry for host

If you get an error saying:

```
no pg_hba.conf entry for host (...)
```

Then you need to set `sslmode` to `require` in your connection string / connection settings.

### Before version 0.5.0

When recreating a database, i.e. removing it from the apps repo and readding it, it currently fails because it will try to recreate the secrets in AWS which it can't do because secrets in AWS are soft-deleted. The solution is to forcefully delete the secrets in AWS and then deleting the PostgresqlDatabase resource in order to recreate all the resources. The following snippet can be used to circumvent soft deletion in order to forcefully delete secrets (BE CAREFUL WHEN FORCE DELETING SECRETS):

```bash
aws secretsmanager delete-secret --secret-id SECRET-ID --force-delete-without-recovery
```
