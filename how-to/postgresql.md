---
title: Working with PostgreSQL
nav_order: 14
parent: How to...
domain: public
permalink: /how-to-postgresql
last_reviewed_on: 2025-09-11
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

**Deletion protection should be enabled for production databases.** Enabling deletion protection will ensure the database in the Aurora cluster is not deleted if the database definition in the apps repository is deleted. If the database is accidentally deleted, follow the guide in [restore](#restore).

Next you need to create an `application.yaml` in the same subfolder in order to instruct ArgoCD how to create your app and deploy the chart:

```yaml
apiVersion: v2
name: my-db
description: my-db
version: 0.1.0
slackChannel: my-slack-channel
helm:
  chart: helm/idp-postgresql
  chartVersion: "0.4.1"
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

## Connect via local database viewer

Request an rds-proxy in your namespace if it doesn't already exist.

Start by following [this guide](https://public.docs.idp.jppol.dk/kubernetes-namespace-access) to get kubectl access. Then port-forward the rds-proxy running inside the cluster using the following command:

```bash
kubectl port-forward pod/rds-proxy 5432:5432 -n NAMESPACE
```

Let the terminal run to keep the connection alive. Retrieve the username and password of the role you want to connect as by reading the corresponding secret using:

```bash
kubectl get secret SECRET-NAME -n NAMESPACE -o yaml | grep 'username: ' | sed 's/ //g' | cut -d ':' -f 2 | base64 -d
```

```bash
kubectl get secret SECRET-NAME -n NAMESPACE -o yaml | grep 'password: ' | sed 's/ //g' | cut -d ':' -f 2 | base64 -d
```

Finally, create a new connection to the database from your local database viewer using localhost, port 5432, the name of the database, and the username and password of the role you want to connect as.

## Work in progress features

WIP features:

- Backup and restore
- Monitoring
- pgAdmin
- PostgreSQL version upgrade strategy

## Restore

### Restore protected database which has been removed from apps repo

Contact IDP as some of these steps requires elevated privileges.

In case the database is accidentally deleted from the apps repo, the resources in Kubernetes is removed while the resources outside of Kubernetes lives on. The service using the database only strictly needs the secrets in Kubernetes to connect to the database. The secrets for the three roles (read, write, admin) can be restored using the following procedure.

*The `endpoint` can be found in the `ClusterProviderConfig` while the `password` can be found in the corresponding secret in AWS.*

```bash
kubectl create secret generic NAMESPACE-DB-ROLE -n NAMESPACE --from-literal=endpoint=foo --from-literal=port=5432 --from-literal=username=NAMESPACE-DB-ROLE --from-literal=password=foo
```

Create the secrets for the admin, write, and read roles.

## Known errors

When recreating a database, i.e. removing it from the apps repo and readding it, it currently fails because it will try to recreate the secrets in AWS which it can't do because secrets in AWS are soft-deleted. The solution is to forcefully delete the secrets in AWS and then deleting the PostgresqlDatabase resource in order to recreate all the resources. The following snippet can be used to circumvent soft deletion in order to forcefully delete secrets (BE CAREFUL WHEN FORCE DELETING SECRETS):

```bash
aws secretsmanager delete-secret --secret-id SECRET-ID --force-delete-without-recovery
```
