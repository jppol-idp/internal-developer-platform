---
title: Auto updating deployments
nav_order: 2 
parent: How to...
domain: public
permalink: /how-to-dynamodb
last_reviewed_on: 2025-09-17
review_in: 6 months
---
# Working with DynamoDB

Using the Helm chart [helm-idp-dynamodb](https://github.com/jppol-idp/helm-idp-dynamodb) you can declaratively create and manage DynamoDB tables that are accessible from workloads in our Kubernetes clusters.

The chart also supports granting read and/or write access to existing AWS IAM roles. This integrates cleanly with roles created by the idp-advanced chart (via IRSA). The chart now generates a single aggregated IAM managed policy per role, combining access across all tables you list for that role.

## Defining tables

The values file contains a top-level array named `tables`, where each item defines one DynamoDB table. Each item maps closely to DynamoDB settings (hashKey, rangeKey, attributes, billingMode, optional indexes, etc.). For the full schema, see the chart docs in ../../helm/helm-idp-dynamodb/.

Examples from ../../apps-koa/apps/koa-dev/dynamo-tables/values.yaml:

- Minimal table with hash key only and read/write access for the access service role:

```yaml
# apps-koa/apps/koa-dev/dynamo-tables/values.yaml

tables:
  - name: AAUserAccess-v3
    useIdpPrefix: true
    hashKey: SsoId
    attributes:
      - name: SsoId
        type: 'S'
    billingMode: PAY_PER_REQUEST
    serviceAccountReadRoles: ["access-service-koa-dev"]
    serviceAccountWriteRoles: ["access-service-koa-dev"]
```

- Table with both hash and range keys, and read/write access for the same role:

```yaml
# apps-koa/apps/koa-dev/dynamo-tables/values.yaml

tables:
  - name: IpAccessAgreement-v2
    useIdpPrefix: true
    hashKey: Ip
    rangeKey: Brand
    attributes:
      - name: Ip
        type: 'S'
      - name: Brand
        type: 'S'
    billingMode: PAY_PER_REQUEST
    serviceAccountReadRoles: ["access-service-koa-dev"]
    serviceAccountWriteRoles: ["access-service-koa-dev"]
```

- Paired “shadow” tables follow the same structure; they are often used for staged migrations or dual-write patterns:

```yaml
# apps-koa/apps/koa-dev/dynamo-tables/values.yaml

  - name: IpAccessAgreement-v2-shadow
    useIdpPrefix: true
    hashKey: Ip
    rangeKey: Brand
    attributes:
      - name: Ip
        type: 'S'
      - name: Brand
        type: 'S'
    billingMode: PAY_PER_REQUEST
    serviceAccountReadRoles: ["access-service-koa-dev"]
    serviceAccountWriteRoles: ["access-service-koa-dev"]
```

Notes
- Table names in AWS are derived from the Kubernetes namespace and the logical table name, optionally prefixed with `idp-` when `useIdpPrefix: true` is set.
- Default region for policies is eu-west-1 unless overridden per table.
- For advanced options (LSI/GSI, throughput, PITR), see the chart documentation in ../../helm/helm-idp-dynamodb/README.md and ../../helm/helm-idp-dynamodb/ACCESSING_TABLE.md.

## Granting access to Dynamo tables.

Grant access by listing existing IAM role names on each table:
- `serviceAccountReadRoles`: roles that should have read permissions on this table
- `serviceAccountWriteRoles`: roles that should have write permissions on this table

The chart aggregates all of a role’s table grants into a single managed policy and creates one RolePolicyAttachment per role. For example, the values above grant both read and write to the IAM role `access-service-koa-dev` across all listed tables.

If you are using idp-advanced to provision workloads, the service account role name typically follows `<application-name>-<namespace>`. In the examples, `access-service-koa-dev` is the role associated with the Access Service deployed in the `koa-dev` namespace.

Refer to ../../helm/helm-idp-dynamodb/ACCESSING_TABLE.md for details on policy naming, scoping, and how aggregation avoids AWS’ 10-managed-policies-per-role limit.

## Backup and restore
By default, point-in-time recovery (PITR) is enabled, allowing restore to any point in time within the last 35 days. If you need a restore, contact the IDP team. See official AWS docs on PITR for DynamoDB for more details.
