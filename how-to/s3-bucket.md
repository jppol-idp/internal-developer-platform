---
title: Working with S3 Buckets
nav_order: 29
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-10-02
review_in: 6 months
---
# Working with S3 Buckets
{: .no_toc }

Use the Helm chart `idp-s3-bucket` to declaratively create and manage S3 buckets via Crossplane in IDP clusters.

- [Chart docs](https://github.com/jppol-idp/helm-idp/blob/main/charts/idp-s3-bucket/README.md)

---

## Table of contents
{: .no_toc }

- TOC
{:toc}

---

## Getting started
A bucket is created by a bucket app in your team's apps repository, in the same way as your other apps. One bucket app can hold several buckets.

1. Create a folder for the app under the namespace it belongs to, for example `apps/idp-dev/my-buckets/`.
2. Add an `application.yaml` that points at the chart:

   ```yaml
   apiVersion: v2
   name: my-buckets
   description: S3 buckets for my team
   version: 0.1.0
   helm:
     chart: helm/idp-s3-bucket
     chartVersion: "0.11.0"   # example version
   ```

   The latest chart version is listed under [releases in helm-idp](https://github.com/jppol-idp/helm-idp/releases).

3. Add a `values.yaml` with your buckets, see [Define buckets](#define-buckets).
4. Merge the change. ArgoCD creates an application named after the folder and the namespace, here `my-buckets-idp-dev`. When it is Synced and Healthy, the bucket exists.

Both files are required. A folder with only a `values.yaml` is not picked up, and no bucket is created.

The bucket is created in the AWS account of the cluster your namespace runs in.

## Define buckets
Specify buckets in the `buckets` array in your values.yaml:

```yaml
buckets:
  - name: my-team-artifacts
    region: eu-west-1      # optional, defaults to eu-west-1
    access: write          # developer access, one of: none | read | write. Leaving it out means none
    publicRead: false      # optional, defaults to false
    tags:
      - key: environment
        value: dev
```

Notes
- Bucket names must be globally unique in AWS, 3-63 lowercase alphanumeric or `-`.
- The chart always renders three Crossplane resources per bucket: `Bucket`, `BucketOwnershipControls` and `BucketPublicAccessBlock`. Depending on your values it also renders a `BucketPolicy` (`publicRead`), a `BucketLifecycleConfiguration` (`lifecycleRules`), a `BucketVersioning` (`versioning`), a `BucketServerSideEncryptionConfiguration` (`encryptionRules`), and the IAM policies that give access to the bucket.

### Public read

Should you want to make the bucket content public, you can set the property `publicRead` to `true`. The chart then adds a bucket policy that lets anyone read the objects. Access control lists (ACLs) are disabled on the bucket and are not used.

Generally we do not recommend this. Bucket access should instead be configured using the IAM Roles for Service Accounts (IRSA) roles of the various applications.

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

### Option 2: let `idp-s3-bucket` attach the generated policy to a deployment role
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
`idp-s3-bucket` only attaches the generated S3 policy. It does not create the workload role or its assume-role policy.

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
Separate from workload (IRSA) access, the chart can grant developers the ability to browse and modify bucket contents from their own machine via the namespace's IAM role `idp_ns_s3_access-<namespace>`. This is intended for human operators, not for pods. For pod access, use [Workload access (IRSA)](#workload-access-irsa) instead.

### The `access` parameter
Each bucket entry accepts an `access` setting that controls what the namespace S3 access role may do with that bucket:

- `write`: grants `s3:GetObject`, `s3:ListBucket`, `s3:PutObject`, and `s3:DeleteObject`.
- `read`: grants `s3:GetObject` and `s3:ListBucket`.
- `none`: no permissions are granted on this bucket via the namespace S3 access role.

Set `access` explicitly. A bucket without `access` is treated as `none`, so developers get no access to it.

The value is schema-validated: anything other than `none`, `read`, or `write` causes `helm template`/`helm install` to fail.

### Assuming the role from your machine
Who may assume `idp_ns_s3_access-<namespace>` is controlled by the role's trust policy (managed outside this chart). If your AWS principal is not listed there, `aws sts assume-role` will fail with `AccessDenied`. Contact the IDP team in your team's onboarding channel on Slack to get added.

Your team's apps repository ships helper scripts that call `aws sts assume-role` against the namespace S3 access role and emit the temporary credentials. There is one per namespace:

- `scripts/assume-<namespace>-s3-role.sh`, for example `scripts/assume-idp-dev-s3-role.sh`.
- PowerShell equivalents under `scripts/powershell/`, for example `assume-idp-dev-s3-role.ps1`.

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

Always name the bucket. `aws s3 ls` without a bucket name fails, because the role is not allowed to list all buckets in the account.

### What the chart renders
When at least one bucket declares `access: read` or `access: write`, the chart adds the namespace developer role `idp_ns_s3_access-<namespace>` to the same aggregated role map used for workload roles. It then renders:

- A managed IAM `Policy` named `<namespace>-idp-ns-s3-access-<namespace>-<release>-idp-s3-bucket` with `S3Read` and/or `S3Write` statements for the buckets that opted the developer role in.
- A `RolePolicyAttachment` that attaches that policy to `idp_ns_s3_access-<namespace>`.
- No observe-only Crossplane `Role` resource; the attachment references the IAM role by plain name.

If no bucket opts the developer role in (all are `access: none` or have no `access`), no developer-role policy or attachment is rendered. Buckets may still create workload-role policies independently via `serviceAccountReadRoles` / `serviceAccountWriteRoles`.

## GitHub Actions access
A workflow in one of your GitHub repositories can read from or write to a bucket without any stored AWS keys. The workflow assumes an IAM role through OpenID Connect (OIDC), and the bucket decides which repositories it lets in.

This is separate from workload access and developer access above. A bucket can use all three at the same time.

### Step 1: ask the IDP team to register the repository
The role is created by the IDP team, once per repository and namespace. Ask the IDP team in your team's onboarding channel on Slack and include:

- The repository, for example `my-org/my-repo`.
- The namespace the bucket lives in, for example `idp-dev`.

You get the Amazon Resource Name (ARN) of the role back. It looks like this:

```
arn:aws:iam::123456789012:role/crossplane/idp_ns_github_access-idp-dev-my-repo
```

The last part of the ARN, after the namespace, is the name you use for the repository in step 2. Here it is `my-repo`. It is normally the repository name, but the IDP team can register a repository under a shorter name.

### Step 2: grant the repository access on the bucket
Add `githubAccess` to the bucket in the values.yaml of your bucket app:

```yaml
buckets:
  - name: my-team-artifacts
    githubAccess:
      - repository: my-repo   # the name from the ARN in step 1, without the organisation
        access: write         # read | write
```

- `read`: grants `s3:GetObject` and `s3:ListBucket`.
- `write`: grants the same as `read`, plus `s3:PutObject` and `s3:DeleteObject`.

This `access` only applies to the repository. It is independent of the bucket's own `access` setting, which controls [developer access](#developer-access-namespace-s3-access-role).

`githubAccess` requires chart version 0.11.0 or later, set as `chartVersion` in the `application.yaml` of your bucket app. The latest version is listed under [releases in helm-idp](https://github.com/jppol-idp/helm-idp/releases). If you upgrade an existing bucket app that is on a version before 0.10.1 and uses `deletionPolicy: Delete` (the default), developer access to the buckets in that app is gone for about 10 minutes after the upgrade. It happens once and recovers by itself. Workload access and GitHub Actions access are not affected.

Wait until the bucket app is Synced and Healthy in ArgoCD before you run the workflow.

The role only reaches the buckets that list the repository. Other buckets in the namespace stay closed to it. To give several repositories access, ask for each of them to be registered and add one entry per repository.

### Step 3: assume the role in the workflow
The role only works in workflows that run on the `main` branch, see [the next section](#the-role-only-works-from-the-main-branch). The job needs permission to request an OIDC token, and then assumes the role with the ARN from step 1:

```yaml
name: Upload to S3

on:
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      # The action version is an example; use the latest major version.
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/crossplane/idp_ns_github_access-idp-dev-my-repo
          aws-region: eu-west-1

      - run: |
          echo "hello from GitHub Actions" > hello.txt
          aws s3 cp hello.txt s3://my-team-artifacts/hello.txt
```

The workflow file has to be on the `main` branch. Start it from the Actions tab. When the upload succeeds, the setup works and you can build your own workflow on top of it.

### The role only works from the main branch
The role trusts workflows that run on the `main` branch of the registered repository, for example on `workflow_dispatch`, `schedule` or `workflow_run`. Workflows that run on the `pull_request` event cannot assume it. This includes the `closed` activity type.

If you need to upload something that is built from a pull request, for example a preview, split it in two workflows:

1. A workflow on `pull_request` builds without AWS credentials and uploads the result as a workflow artifact.
2. A workflow on `workflow_run`, which runs from `main`, downloads the artifact and uploads it to the bucket.

Code from the pull request then never runs while the role is held. Cleanup when a pull request closes has to follow the same pattern: a job on `main`, for example on a schedule, removes what is no longer needed.

If you need the role to trust another branch than `main`, ask the IDP team in your team's onboarding channel on Slack.

### Troubleshooting GitHub Actions access
**`Not authorized to perform sts:AssumeRoleWithWebIdentity`**: the workflow is not allowed to assume the role.

- The workflow runs on a pull request or on another branch than `main`.
- The job is missing `permissions: id-token: write`.
- The job uses a GitHub environment (`environment:`). The role does not trust jobs that run in an environment.
- The ARN is wrong. The path `/crossplane/` is part of it.
- The repository was renamed or recreated after it was registered. It has to be registered again, see step 1.

**`AccessDenied` from S3**: the role was assumed, but it has no access to the bucket.

- The bucket does not list the repository under `githubAccess`, the name in `repository` does not match the last part of the ARN, or it lists `read` and the workflow writes.
- The chart version is older than 0.11.0.
- The change has not been synced in ArgoCD yet.

If none of this helps, contact the IDP team in your team's onboarding channel on Slack.

## Serving bucket content in a browser
If the content of a bucket has to be viewed in a browser, for example a static site or a preview build, you do not have to make the bucket public. You can run a small gateway app in front of it. This is a valid alternative to hosting the bucket content through CloudFront.

The gateway is [nginx-s3-gateway](https://github.com/nginx/nginx-s3-gateway), deployed as an ordinary `idp-advanced` app:

- The bucket stays private (`publicRead: false`).
- The gateway reads the bucket with its own role, which you grant with `serviceAccountReadRoles`.
- You decide who can reach the gateway with the ingress settings of the app, for example only the office and VPN. See [Controlling network access to your app](network-access.html).

### Step 1: give the gateway read access to the bucket
In the values.yaml of your bucket app, list the name of the gateway app:

```yaml
buckets:
  - name: my-team-artifacts
    publicRead: false
    serviceAccountReadRoles:
      - my-gateway
```

### Step 2: deploy the gateway app
Create a new app folder named `my-gateway` next to your other apps, with an `application.yaml` and a `values.yaml`. The folder name must match the name you listed in step 1.

`application.yaml`:

```yaml
apiVersion: v2
name: my-gateway
description: Serves the my-team-artifacts bucket
version: 0.1.0
helm:
  chart: helm/idp-advanced
  chartVersion: "3.12.1"   # example version; use the version your other apps use
```

The available versions of `idp-advanced` are listed under [releases in helm-idp](https://github.com/jppol-idp/helm-idp/releases).

In `values.yaml` you only have to change three things: the bucket name in `S3_BUCKET_NAME`, the hostname under `ingress.fqdn`, and who may reach it under `ingress.public`.

<details markdown="block">
<summary>Show the full values.yaml for the gateway</summary>

```yaml
image:
  repository: ghcr.io/nginx/nginx-s3-gateway/nginx-oss-s3-gateway
  pullPolicy: IfNotPresent
  tag: "unprivileged-oss-20260928"   # example version; check the nginx-s3-gateway repository for newer tags
serviceAccount:
  create: true
  irsa:
    enabled: true
env:
  - name: S3_BUCKET_NAME
    value: my-team-artifacts
  - name: S3_SERVER
    value: s3.eu-west-1.amazonaws.com
  - name: S3_SERVER_PROTO
    value: https
  - name: S3_SERVER_PORT
    value: "443"
  - name: S3_STYLE
    value: virtual
  - name: S3_REGION
    value: eu-west-1
  - name: AWS_REGION
    value: eu-west-1
  - name: AWS_SIGS_VERSION
    value: "4"
  - name: JS_TRUSTED_CERT_PATH
    value: /etc/ssl/certs/Amazon_Root_CA_1.pem
  - name: ALLOW_DIRECTORY_LIST
    value: "false"
  - name: PROVIDE_INDEX_PAGE
    value: "true"
  - name: APPEND_SLASH_FOR_POSSIBLE_DIRECTORY
    value: "true"
  # How long the gateway caches a file. The default is 1 hour.
  - name: PROXY_CACHE_VALID_OK
    value: 1m
  - name: PROXY_CACHE_MAX_SIZE
    value: 256m
service:
  type: ClusterIP
  port: 8080
ingress:
  enabled: true
  fqdn:
    - my-gateway.example.idp.jppol.dk   # replace with a hostname on the same domain as your other apps
  public:
    enabled: true
    ipAllowList:
      - "91.214.20.0/22"   # only the office and VPN
  private:
    enabled: false
resources:
  requests:
    memory: 64Mi
    cpu: 50m
  limits:
    memory: 128Mi
livenessProbe:
  httpGet:
    path: /health
    port: 8080
readinessProbe:
  httpGet:
    path: /health
    port: 8080
autoscaling:
  enabled: false
```

</details>

A file stored as `docs/index.html` in the bucket is then served at `https://my-gateway.example.idp.jppol.dk/docs/`.

### Things to know about the gateway
- **Set `PROXY_CACHE_VALID_OK`.** Without it the gateway caches every file for 1 hour, so a new upload under the same path keeps showing the old content for up to an hour. The values above set it to 1 minute.
- **404 for everything means missing access.** The gateway answers 404 both when a file does not exist and when it is not allowed to read the bucket. If every path gives 404, check that the bucket lists the gateway app under `serviceAccountReadRoles` and that both apps are Synced and Healthy in ArgoCD.
- The line "using IMDS for credentials" in the gateway's startup log is harmless. It reads the bucket with the role of the app.

## Lifecycle policies and versioning
S3 supports lifecycle policies that can transition older objects to cheaper storage classes (infrequent access, glacier etc) or delete old versions entirely.

S3 also supports versioning where changed objects are kept when an object is modified.

From version 0.8.0 of the chart `idp-s3-bucket` these settings are available for all buckets created using the chart. Configuration is made on a per-bucket basis. Please refer to the [documentation here, for further details](https://github.com/jppol-idp/helm-idp/tree/main/charts/idp-s3-bucket#lifecycle-configuration)

Versioning and encryption are set per bucket in the same way:

```yaml
buckets:
  - name: my-team-artifacts
    versioning: Enabled        # Enabled | Suspended
    encryptionRules:
      - applyServerSideEncryptionByDefault:
          sseAlgorithm: AES256   # AES256 | aws:kms | aws:kms:dsse
```

See [Versioning](https://github.com/jppol-idp/helm-idp/tree/main/charts/idp-s3-bucket#versioning) and [Encryption](https://github.com/jppol-idp/helm-idp/tree/main/charts/idp-s3-bucket#encryption) in the chart documentation.

## Crossplane policies
Control how Crossplane manages the resources of a bucket app via top-level settings in values.yaml:

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
- AWS will not delete non-empty buckets. With Delete, Crossplane's deletion will fail until the bucket is emptied; consider using Orphan during migrations.
- Policies apply to all resources the chart renders for the bucket, including the IAM policies and their attachments.

## Troubleshooting
**The bucket is not created.**

- The app folder is missing `application.yaml`. See [Getting started](#getting-started).
- The bucket name is already taken. Bucket names are unique across all of AWS, not only within your account.
- Look at the application in ArgoCD. The `Bucket` resource shows the error from AWS.

**A bucket cannot be deleted.**

AWS does not delete a bucket that still has objects in it. Empty the bucket first, then the deletion goes through.

**`aws s3 ls` fails with `AccessDenied` for a developer.**

- Name the bucket: `aws s3 ls s3://my-team-artifacts`. Listing all buckets is not allowed.
- Check that the bucket has `access: read` or `access: write`. A bucket without `access` gives developers no access.

For problems with a workflow, see [Troubleshooting GitHub Actions access](#troubleshooting-github-actions-access).

If none of this helps, contact the IDP team in your team's onboarding channel on Slack.
