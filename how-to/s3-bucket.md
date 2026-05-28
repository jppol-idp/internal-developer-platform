---
title: Working with S3 Buckets
nav_order: 24
parent: How to...
domain: public
permalink: /how-to-s3
last_reviewed_on: 2026-04-05
review_in: 6 months
---
# Working with S3 Buckets

Use the Helm chart helm-idp-s3-bucket to declaratively create and manage S3 buckets via Crossplane in IDP clusters.

- [Chart docs](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-s3-bucket/README.md)

## Define buckets
Specify buckets in the `buckets` array in your values.yaml:

```yaml
buckets:
  - name: my-team-artifacts
    region: eu-west-1      # optional, defaults to eu-west-1
    access: write          # optional, one of: none | read | write (default: write)
    publicRead: false      # optional, defaults to false
    tags:
      - key: environment
        value: dev
```

Notes
- Bucket names must be globally unique in AWS, 3–63 lowercase alphanumeric or `-`.
- The chart renders three Crossplane resources per bucket: Bucket, BucketOwnershipControls and iam policies for accessing the bucket.

### ACL options

Should you want to make the bucket content public, you can set the property `publicRead` to `true`. 

Generally we do not recommend this. Bucket access should instead be configured using the irsa roles of the 
various applications. 


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

## Workload access (IRSA)
For pods running in the cluster, there are two supported patterns.

### Option 1: attach S3 permissions directly in `idp-advanced`
If you want to keep the S3 permissions next to the workload, grant them directly on the IRSA role created by `idp-advanced` using `serviceAccount.irsa.iamPolicyStatements`, for example:

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

Replace `my-team-artifacts` with your actual bucket name. Ensure your application uses the service account created by `idp-advanced`.

### Option 2: let `helm-idp-s3-bucket` attach the generated policy to a deployment role
If you want bucket access declared together with the bucket, use the per-bucket `serviceAccountReadRoles` and `serviceAccountWriteRoles` fields:

```yaml
buckets:
  - name: my-team-artifacts
    serviceAccountReadRoles:
      - static-website
  - name: my-team-uploads
    serviceAccountWriteRoles:
      - uploader
```

Important details:
- These values are deployment names, not raw IAM role names.
- In namespace `idp-dev`, `static-website` resolves to the IAM role `static-website-idp-dev`.
- If you already provide a fully qualified role name ending in `-<namespace>`, the chart leaves it unchanged for backwards compatibility.
- The chart aggregates access per resolved role and renders one IAM `Policy` and one `RolePolicyAttachment` per distinct role.

### Assume-role policy / trust policy for workloads
`helm-idp-s3-bucket` only attaches the generated S3 policy. It does not create the workload role or its assume-role policy.

The common setup is to let `idp-advanced` create the IRSA role:

```yaml
serviceAccount:
  create: true
  irsa:
    enabled: true
```

That role's assume-role policy trusts the cluster's OIDC provider and the workload service account, which is what allows the pod to obtain AWS credentials. The S3 chart then attaches the generated S3 policy to that existing role. If the role is missing, named differently, or its assume-role policy does not match the service account, the pod will not be able to get credentials even though the S3 attachment exists.

For human/operator access to bucket contents from a workstation, see [Developer access (namespace S3 access role)](#developer-access-namespace-s3-access-role) below.

## Developer access (namespace S3 access role)
Separate from workload (IRSA) access, the chart can grant developers the ability to browse and modify bucket contents from their own machine via the namespace's IAM role `idp_ns_s3_access-<namespace>`. This is intended for human operators, not for pods — for pod access, use [Workload access (IRSA)](#workload-access-irsa) instead.

### The `access` parameter
Each bucket entry accepts an `access` setting that controls what the namespace S3 access role may do with that bucket:

- `write` – (default) grants `s3:GetObject`, `s3:ListBucket`, `s3:PutObject`, and `s3:DeleteObject`.
- `read` – grants `s3:GetObject` and `s3:ListBucket`.
- `none` – no permissions are granted on this bucket via the namespace S3 access role.

The value is schema-validated: anything other than `none`, `read`, or `write` causes `helm template`/`helm install` to fail.

### Assuming the role from your machine
Who may assume `idp_ns_s3_access-<namespace>` is controlled by the role's trust policy (managed outside this chart). If your AWS principal is not listed there, `aws sts assume-role` will fail with `AccessDenied` — contact the IDP platform team to get added.

The `apps-idp` repository ships helper scripts that call `aws sts assume-role` against the namespace S3 access role and emit the temporary credentials:

- `apps-idp/scripts/assume-idp-dev-s3-role.sh`
- `apps-idp/scripts/assume-idp-test-s3-role.sh`
- `apps-idp/scripts/assume-idp-shared-test-s3-role.sh`
- PowerShell equivalents under `apps-idp/scripts/powershell/` (e.g. `assume-idp-dev-s3-role.ps1`).

The Bash scripts print `export` statements so they can be sourced into the current shell:

```bash
eval "$(./scripts/assume-idp-dev-s3-role.sh)"
aws s3 ls s3://my-team-artifacts
```

The PowerShell scripts set the `AWS_*` environment variables on the current session directly:

```powershell
. .\scripts\powershell\assume-idp-dev-s3-role.ps1
aws s3 ls s3://my-team-artifacts
```


### What the chart renders
When at least one bucket declares `access: read` or `access: write`, the chart adds the namespace developer role `idp_ns_s3_access-<namespace>` to the same aggregated role map used for workload roles. It then renders:

- A managed IAM `Policy` named `<namespace>-idp-ns-s3-access-<namespace>-<release>-idp-s3-bucket` with `S3Read` and/or `S3Write` statements for the buckets that opted the developer role in.
- A `RolePolicyAttachment` that attaches that policy to `idp_ns_s3_access-<namespace>`.
- No observe-only Crossplane `Role` resource; the attachment references the IAM role by plain name.

If no bucket opts the developer role in (all are `access: none`), no developer-role policy or attachment is rendered. Buckets may still create workload-role policies independently via `serviceAccountReadRoles` / `serviceAccountWriteRoles`.

