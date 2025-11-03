---
title: Working with S3 Buckets
nav_order: 12
parent: How to...
domain: public
permalink: /how-to-s3
last_reviewed_on: 2025-11-02
review_in: 6 months
---
# Working with S3 Buckets

Use the Helm chart helm-idp-s3-bucket to declaratively create and manage S3 buckets via Crossplane in IDP clusters.

- Chart docs: ../../helm/helm-idp-s3-bucket/charts/idp-s3-bucket/README.md

## Define buckets
Specify buckets in the `buckets` array in your values.yaml:

```yaml
buckets:
  - name: my-team-artifacts
    region: eu-west-1      # optional, defaults to eu-west-1
    acl: private           # optional, defaults to private
    tags:
      - key: environment
        value: dev
```

Notes
- Bucket names must be globally unique in AWS, 3–63 lowercase alphanumeric or `-`.
- The chart renders three Crossplane resources per bucket: Bucket, BucketOwnershipControls, and BucketACL.

### ACL options
The `acl` field accepts the following canned ACLs (default: `private`):
- private: Only the bucket owner has access. Recommended default.
- public-read: Anyone on the internet can read objects. Use with caution.
- public-read-write: Anyone can read and write objects. Almost never appropriate.
- aws-exec-read: Owner has full control; AWS services (e.g., EC2) can read objects.
- authenticated-read: Any authenticated AWS user can read objects. Rarely appropriate.
- bucket-owner-read: Object writer has full control; bucket owner gets read access.
- bucket-owner-full-control: Object writer and bucket owner both have full control.
- log-delivery-write: Grants the Log Delivery group write access (for access logs target buckets).

## Crossplane policies
Control how Crossplane manages these resources via top-level settings in values.yaml:

```yaml
managementPolicies: Control   # Control = Create/Update/LateInitialize (+Observe); Observe = read-only

deletionPolicy: Delete       # Delete = allow deletions; Orphan = leave AWS resources when removed
```

- managementPolicies
  - Control: Crossplane may create and update S3 resources.
  - Observe: Crossplane only reads existing resources (useful for adopting existing buckets).
- deletionPolicy
  - Delete: Includes Delete in managementPolicies. Removing a bucket from values attempts to delete it in AWS.
  - Orphan: Excludes Delete. Removing a bucket from values leaves the AWS bucket untouched.

Important
- AWS will not delete non-empty buckets. With Delete, Crossplane’s deletion will fail until the bucket is emptied; consider using Orphan during migrations.
- Policies apply to all three rendered resources (Bucket, OwnershipControls, ACL).

## Access from workloads (IRSA)
This chart does not create IAM access for applications. To access a bucket from pods, grant permissions to your service account role via idp-advanced (IRSA) `iamPolicyStatements`, for example:

```yaml
serviceAccount:
  create: true
  irsa:
    enabled: true
    iamPolicyStatements:
      - Effect: Allow
        Action:
          - s3:ListBucket
        Resource:
          - arn:aws:s3:::my-team-artifacts
      - Effect: Allow
        Action:
          - s3:GetObject
          - s3:PutObject
          - s3:DeleteObject
        Resource:
          - arn:aws:s3:::my-team-artifacts/*
```

Replace `my-team-artifacts` with your actual bucket name. Ensure your application uses the service account created by idp-advanced.
