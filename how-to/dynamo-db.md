---
title: Working with DynamoDB
nav_order: 5 
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

### Example: Table with Local Secondary Indexes (LSIs) via Helm values

The chart supports Local Secondary Indexes through the `localSecondaryIndex` array on each table. According to the chart schema, each LSI requires `name`, `projectionType`, and `nonKeyAttributes` fields; include `rangeKey` to specify the alternate sort key for the LSI. Remember that LSIs:
- Share the same partition key as the base table (the table’s `hashKey`).
- Must be defined at table creation time (they cannot be added later by DynamoDB).
- Require any index key attributes to be declared in `attributes`.

```yaml
# Example values.yaml fragment
# Define a table with two LSIs: one on TotalAmount and one on Status

tables:
  - name: Orders
    useIdpPrefix: true
    hashKey: CustomerId
    rangeKey: OrderDate
    attributes:
      - name: CustomerId
        type: 'S'
      - name: OrderDate
        type: 'S'
      - name: TotalAmount
        type: 'N'
      - name: Status
        type: 'S'
    billingMode: PAY_PER_REQUEST

    # Local Secondary Indexes (same HASH key: CustomerId)
    localSecondaryIndex:
      - name: AmountIndex
        rangeKey: TotalAmount
        projectionType: INCLUDE
        nonKeyAttributes: ["items", "shippingAddress"]
      - name: StatusIndex
        rangeKey: Status
        projectionType: ALL
        nonKeyAttributes: []

    # Optional: grant access to existing IAM roles
    serviceAccountReadRoles: ["access-service-koa-dev"]
    serviceAccountWriteRoles: ["access-service-koa-dev"]
```

Tips for LSIs
- For `projectionType: INCLUDE`, list the attributes you want to project in `nonKeyAttributes` (up to 20).
- For `projectionType: ALL` or `KEYS_ONLY`, this chart’s schema still expects `nonKeyAttributes`; set it to an empty list (`[]`) if you don’t need additional attributes.
- Keep each partition key’s item collection (table + LSIs) under DynamoDB’s 10 GB limit.

See the schema and docs for precise field definitions:
- ../../helm/helm-idp-dynamodb/values.schema.json
- ../../helm/helm-idp-dynamodb/README.md

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

*NB*: If you attempt to grant access to non-existing role or a role that has not been created by our helm charts, you will experience an error saying, that 
no role based policy allows the assignment. Please double check role names, if this error occurs.

## Backup and restore
By default, point-in-time recovery (PITR) is enabled, allowing restore to any point in time within the last 35 days. If you need a restore, contact the IDP team. See official AWS docs on PITR for DynamoDB for more details.

Point in time recovery only supports rollback to a specific point in time. You can enable regular AWS backup which will perform a nightly backup of the table, that can be restored to another table name and leave the 
original table unmodified. Again restores must be performed by the IDP team.
