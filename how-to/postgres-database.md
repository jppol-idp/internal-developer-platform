---
title: Add Postgres Database
nav_order: 3 
parent: How to...
domain: public
permalink: /add-postgres-database
last_reviewed_on: 2025-09-11
review_in: 3 months
---
# Add Postgres Database [BETA FEATURE]

## Introduction
This guide shows how to add a PostgreSQL database to your application using the [idp-tenantdatabase chart](https://github.com/jppol-idp/helm-idp-postgresql).
Databases are provisioned inside an IDP-managed Aurora cluster and can be connected to your application through Kubernetes secrets.

If you want to learn more about what Aurora is and how it works, please refer to [the official documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.how-it-works.html).

This feature is considered **Beta**, meaning it is functional but still under active development. Some configuration options etc. may change in future releases, and there may be minor bugs or limitations. We recommend using this feature first in development or staging environments and welcome your feedback to help improve it.

Being a Beta feature, it is not automatically enabled in all accounts. If you have an interest in trying it out, please reach out in the [idp-team Slack channel](https://jppol.slack.com/archives/C07TZPBHFUL) and ask to have it enabled.


## Define your Database
In your apps repository add a new subfolder in the relevant namespace folder.

Now define a `values.yaml` file describing the database you want to provision:

```yaml 
tenantDatabases:
  - name: my-db
    namespace: my-namespace
    roleDeletionPolicy: Orphan
    dbDeletionPolicy: Orphan
```

Next you need to create an `application.yaml` in the same subfolder in order to instruct ArgoCD how to create your app and deploy the chart:

```yaml
apiVersion: v2
name: my-db
description: my-db
version: 0.1.0
slackChannel: my-slack-channel
helm:
  chart: helm/idp-tenantdatabase
  chartVersion: "1.1.1"
```

Once this is committed, ArgoCD will automatically deploy the database.

## Connect your Application
Once the database is created, configure your application to use it. 
There are three different database roles created alongside your database: An admin role, a write role and a read role.

Depending on which type of role you need to act as, configure your yaml to use the appropriate one.
Using the example configuration, `my-db` above with write privileges, database access would be configured using the connection details from the K8s secret `my-db-write`.

Update your app’s values.yaml to load these as environment variables:

```yaml 
env:
  - name: DB_NAME
    value: my-db
  - name: DB_USER
    valueFrom:
      secretKeyRef:
        name: my-db-write
        key: username
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: my-db-write
        key: password
  - name: DB_HOST
    valueFrom:
      secretKeyRef:
        name: my-db-write
        key: endpoint
  - name: DB_PORT
    valueFrom:
      secretKeyRef:
        name: my-db-write
        key: port
```
