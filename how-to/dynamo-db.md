---
title: Working with DynamoDB
nav_order: 26
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-09-24
review_in: 6 months
---
# Working with DynamoDB

Using the Helm chart [idp-dynamodb](https://github.com/jppol-idp/helm-idp/tree/main/charts/idp-dynamodb) you can declaratively create and manage DynamoDB tables that are accessible from workloads in our Kubernetes clusters.

The chart also supports granting read and/or write access to existing AWS IAM roles. This integrates cleanly with roles created by the idp-advanced chart (via IRSA). The chart generates a single aggregated IAM managed policy per role, combining access across all tables you list for that role.

## Crossplane policies (managementPolicies and deletionPolicy)
The chart exposes Crossplane policy controls that decide whether resources are created/updated and whether they are deleted when removed from values:

```yaml
managementPolicies: Control   # Control (create/update) or Observe (read-only)
deletionPolicy: Orphan        # Delete or Orphan
```

- managementPolicies
  - Control: Crossplane may Create, Update and LateInitialize resources (plus Observe).
  - Observe: Crossplane only reads existing resources; nothing is created or changed. Useful for importing/adopting.
- deletionPolicy
  - Delete: Removing a table (or uninstalling the chart) deletes the AWS resource and its data.
  - Orphan: Removing a table from values leaves the AWS resource in place.

Notes
- Neither setting has a default. If you omit `managementPolicies`, the chart only renders `Observe` and nothing is created. If you omit `deletionPolicy`, resources are orphaned when removed.
- These settings apply to the Table, generated IAM Policy, and RolePolicyAttachment resources rendered by the chart.
- `Orphan` protects your tables against accidental deletion, and is what the examples on this page use. With `Delete`, removing a table from values deletes the table and its data.

## Defining tables

The values file contains a top-level array named `tables`, where each item defines one DynamoDB table. Each item maps closely to DynamoDB settings (hashKey, rangeKey, attributes, billingMode, optional indexes, etc.). For the full schema, see the [chart documentation](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-dynamodb/README.md).

The examples below use a fictional customer, Webshop. Webshop has the repository `apps-webshop` and runs a service called `orders` in the namespace `webshop-test` on the cluster `idp-shared-test`:

- The service itself is deployed with idp-advanced from `apps/webshop-test/orders/app`.
- Its tables are defined in `apps/webshop-test/orders/dynamodb/values.yaml`.
- The service's IAM role is `orders-app-webshop-test` (see [Granting access to Dynamo tables](#granting-access-to-dynamo-tables)).
- The table `Orders` is created in AWS as `webshop-test-Orders`.

Next to the values file, the `dynamodb` directory needs an `application.yaml` that tells ArgoCD to deploy the idp-dynamodb chart with the values file next to it:

```yaml
# apps/webshop-test/orders/dynamodb/application.yaml

apiVersion: v2
name: orders-dynamodb
description: DynamoDB tables for the orders service
version: 0.1.0  # version of this deployment definition, not the chart
helm:
  chart: helm/idp-dynamodb
  chartVersion: "2.1.11"
```

Always check the [changelog](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-dynamodb/CHANGELOG.md) for the latest chart version. This page is based on version 2.1.11.

All tables for a service go in the same `tables` list in one values file. The first example shows a complete values file; the following examples are additional entries in the same list.

Examples:

- Minimal table with hash key only and read/write access for the service's role:

```yaml
# apps/webshop-test/orders/dynamodb/values.yaml

# Required: without Control, nothing is created
managementPolicies: Control
deletionPolicy: Orphan

tables:
  - name: Orders
    hashKey: OrderId
    attributes:
      - name: OrderId
        type: 'S'
    billingMode: PAY_PER_REQUEST
    # IAM role of the orders service: <service>-<app dir>-<namespace>
    serviceAccountReadRoles: ["orders-app-webshop-test"]
    serviceAccountWriteRoles: ["orders-app-webshop-test"]
```

- Table with both hash and range keys, and read/write access for the same role:

```yaml
# apps/webshop-test/orders/dynamodb/values.yaml

  - name: OrderLines
    hashKey: OrderId
    rangeKey: LineId
    attributes:
      - name: OrderId
        type: 'S'
      - name: LineId
        type: 'S'
    billingMode: PAY_PER_REQUEST
    serviceAccountReadRoles: ["orders-app-webshop-test"]
    serviceAccountWriteRoles: ["orders-app-webshop-test"]
```

- Paired “shadow” tables follow the same structure; they are often used for staged migrations or dual-write patterns:

```yaml
# apps/webshop-test/orders/dynamodb/values.yaml

  - name: OrderLines-shadow
    hashKey: OrderId
    rangeKey: LineId
    attributes:
      - name: OrderId
        type: 'S'
      - name: LineId
        type: 'S'
    billingMode: PAY_PER_REQUEST
    serviceAccountReadRoles: ["orders-app-webshop-test"]
    serviceAccountWriteRoles: ["orders-app-webshop-test"]
```

### Example: Table with Local Secondary Indexes (LSIs)

The chart supports Local Secondary Indexes through the `localSecondaryIndex` array on each table. According to the chart schema, each LSI requires `name`, `rangeKey`, `projectionType`, and `nonKeyAttributes` fields. `rangeKey` is the alternate sort key for the LSI. Remember that LSIs:
- Share the same partition key as the base table (the table’s `hashKey`).
- Must be defined at table creation time (they cannot be added to an existing table).
- Require any index key attributes to be declared in `attributes`.

```yaml
# apps/webshop-test/orders/dynamodb/values.yaml
# A table with two LSIs: one on TotalAmount and one on Status

  - name: CustomerOrders
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
        nonKeyAttributes: ["Items", "ShippingAddress"]
      - name: StatusIndex
        rangeKey: Status
        projectionType: ALL
        nonKeyAttributes: []

    # Optional: grant access to existing IAM roles
    serviceAccountReadRoles: ["orders-app-webshop-test"]
    serviceAccountWriteRoles: ["orders-app-webshop-test"]
```

Tips for LSIs
- For `projectionType: INCLUDE`, list the attributes you want to project in `nonKeyAttributes` (up to 20).
- For `projectionType: ALL` or `KEYS_ONLY`, this chart’s schema still expects `nonKeyAttributes`; set it to an empty list (`[]`) if you don’t need additional attributes.
- Keep each partition key’s item collection (table + LSIs) under DynamoDB’s 10 GB limit.

### Example: Table with Global Secondary Indexes (GSIs)

Global Secondary Indexes let you query a table on a different partition key than the table's own `hashKey`. Define them in the `globalSecondaryIndex` array on each table. Each GSI requires `name`, `hashKey` and `projectionType`, and the chart expects a `rangeKey` as well. As with LSIs, the index key attributes must be declared in `attributes`.

```yaml
# apps/webshop-test/orders/dynamodb/values.yaml
# A table of shipments that can also be looked up by order

  - name: Shipments
    hashKey: ShipmentId
    attributes:
      - name: ShipmentId
        type: 'S'
      - name: OrderId
        type: 'S'
      - name: ShippedAt
        type: 'S'
    billingMode: PAY_PER_REQUEST
    globalSecondaryIndex:
      - name: OrderIndex
        hashKey: OrderId
        rangeKey: ShippedAt
        projectionType: ALL
    serviceAccountReadRoles: ["orders-app-webshop-test"]
    serviceAccountWriteRoles: ["orders-app-webshop-test"]
```

For `projectionType: INCLUDE`, list the projected attributes in `nonKeyAttributes`. For `ALL` and `KEYS_ONLY` you can leave it out.

### Time to live (TTL)

With TTL, DynamoDB deletes items automatically once the time stored in an attribute on the item has passed. The attribute must hold the expiry time as a Unix timestamp in seconds. DynamoDB deletes expired items in the background, typically within a few days of expiry.

```yaml
# apps/webshop-test/orders/dynamodb/values.yaml

  - name: Carts
    hashKey: CartId
    attributes:
      - name: CartId
        type: 'S'
    billingMode: PAY_PER_REQUEST
    ttl:
      attributeName: ExpiresAt
      enabled: true
    serviceAccountReadRoles: ["orders-app-webshop-test"]
    serviceAccountWriteRoles: ["orders-app-webshop-test"]
```

Do not add the TTL attribute to `attributes` unless it is also used as a key. `attributes` only lists attributes used as table or index keys.

### Provisioned capacity

The examples use `billingMode: PAY_PER_REQUEST`, where you pay per request and do not plan capacity. If you want fixed capacity instead, set `billingMode: PROVISIONED` together with `readCapacity` and `writeCapacity`:

```yaml
# apps/webshop-test/orders/dynamodb/values.yaml

  - name: Products
    hashKey: ProductId
    attributes:
      - name: ProductId
        type: 'S'
    billingMode: PROVISIONED
    readCapacity: 5
    writeCapacity: 5
    serviceAccountReadRoles: ["orders-app-webshop-test"]
    serviceAccountWriteRoles: ["orders-app-webshop-test"]
```

The chart does not currently set capacity on Global Secondary Indexes, so use `PAY_PER_REQUEST` for tables with GSIs.

See the schema and docs for precise field definitions:
- [values.schema.json](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-dynamodb/values.schema.json)
- [README.md](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-dynamodb/README.md)

Notes
- Table names in AWS are derived from the Kubernetes namespace and the logical table name, optionally prefixed with `idp-` when `useIdpPrefix: true` is set. `useIdpPrefix` exists for legacy tables only; omit it for new tables.
- Default region is eu-west-1. To create a table in another region, set `region` on the table, for example `region: eu-north-1`. The generated IAM policies follow the table's region.
- For all options, see the [chart README](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-dynamodb/README.md) and [ACCESSING_TABLE.md](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-dynamodb/ACCESSING_TABLE.md).

## Granting access to Dynamo tables

Grant access by listing existing IAM role names on each table:
- `serviceAccountReadRoles`: roles that should have read permissions on this table
- `serviceAccountWriteRoles`: roles that should have write permissions on this table

The chart aggregates all of a role’s table grants into a single managed policy and creates one RolePolicyAttachment per role. For example, the values above grant both read and write to the IAM role `orders-app-webshop-test` across all listed tables.

If you are using idp-advanced to provision workloads, the service account role has the same name as the ArgoCD application. For an application in `apps/<namespace>/<service>/<app dir>`, the name is `<service>-<app dir>-<namespace>`. In the examples, Webshop's orders service lives in `apps/webshop-test/orders/app`, so its role is `orders-app-webshop-test`. If in doubt, look up the application name in ArgoCD.

Refer to [ACCESSING_TABLE.md](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-dynamodb/ACCESSING_TABLE.md) for details on policy naming, scoping, and how aggregation avoids AWS’ 10-managed-policies-per-role limit.

*NB*: If you grant access to a role that does not exist, or to a role that was not created by our Helm charts, you will get an error saying that no role-based policy allows the assignment. If this happens, double check the role names.

## Backup and restore
By default, point-in-time recovery (PITR) is enabled, allowing restore to any point in time within the last 35 days. If you need a restore, contact the IDP team. You can turn PITR off for a table with `pointInTimeRecovery: false`. See the [AWS documentation on PITR for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Point-in-time-recovery.html) for more details.

Point in time recovery only supports rollback to a specific point in time. In addition, all tables created by the chart are included in a nightly AWS Backup, kept for 35 days. A backup can be restored to another table name, leaving the original table unmodified. Again, restores must be performed by the IDP team.
