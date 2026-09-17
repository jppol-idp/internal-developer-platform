---
title: Auto updating deployments
nav_order: 6
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-09-17
review_in: 6 months
---
# Auto updating

## Introduction
If you desire to integrate deployments in your pipeline, you can utilize the system [Argo CD Image Updater](https://argocd-image-updater.readthedocs.io/en/stable/) which is a first class citizen in the IDP. 


Argo CD Image Updater (AIU) connects your application repository ("apps-") with a polling mechanism, that evaluates changes in ECR for eligibility for updating your various deployments. You decide if and how auto update should occur, and the image updater will create git commits, adhering to the gitops principles. 

## Setting up auto updates
While Argo CD Image Updater is a tool generally applicable for updating container image tags in Kubernetes, this document assumes you are using the helm chart `idp-advanced` provided by the IDP team. (If you need to integrate AIU with charts developed by you, we refer to the documentation from AIU linked above.)

Assuming you already have some deployment in place using `idp-advanced` chart, you can add Argo CD Image Updater by extending the `application.yaml` file with a few settings matching the container reference in `values.yaml`. 

If we have a `values.yaml` containing the following `image` section:

```yaml
image:
  repository: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/koa/customer-overview
  pullPolicy: IfNotPresent
  tag: "2.0.59"
``` 

and we want AIU to update whenever a newer image is built with a tag starting with `2.`, we can 
instruct AIU to use a strategy called `newest-build`. 

The instructions for AIU have been inserted into the `application.yaml` in the following example:

```yaml
apiVersion: v2
name: static-html
description: static-html
version: 0.1.0
helm:
  chart: helm/idp-advanced
  chartVersion: "3.9.0"
argocd_image_updater_ecr_image: koa/customer-overview
argocd_image_updater_update_strategy: newest-build
argocd_image_updater_allow_tags: regexp:^2\..*

```

In the example AIU is instructed to look for changes in `koa/customer-overview`. Please note that this must match the repository definition in the image section of the `values.yaml`, but that the registry is omitted. Or in plain terms, it should match the path of the repository reference. 

Using `newest-build`, AIU will check if something has been pushed since the referenced image, and inserting an `argocd_image_updater_allow_tags` with a `regexp:` limits it to tags matching `^2\..*`. 

AIU has other strategies for updating images and can among other things be used to detect and respect SemVer changes. We refer to the AIU documentation for the specifics. 

### Available settings
Only `argocd_image_updater_ecr_image` is required. Adding it enables AIU for the application; all other settings fall back to a default.

| Setting | Default | Description |
|---------|---------|-------------|
| `argocd_image_updater_ecr_image` | (required) | Repository path in ECR, without the registry |
| `argocd_image_updater_update_strategy` | `semver` | Update strategy, e.g. `semver` or `newest-build` |
| `argocd_image_updater_allow_tags` | `any` | Limit eligible tags, e.g. `regexp:^2\..*` |
| `argocd_image_updater_git_branch` | `main` | Branch in your apps repository that AIU commits to |
| `argocd_image_updater_write_back_target` | `values.yaml` | File that AIU writes the new tag to (see below) |
| `argocd_image_updater_ecr_registry` | `354918371398.dkr.ecr.eu-west-1.amazonaws.com` | Registry hosting the image |
| `argocd_image_updater_helm_image_spec` | (not set) | Path to the full image reference in the values (see below) |
| `argocd_image_updater_force_update` | (not set) | Set to `"true"` to force the update (see below) |

AIU checks ECR for new images every 45 seconds, so a new tag is usually committed to your apps repository within a minute of the push.

## If your values file becomes garbled
When AIU alters the image tag, it naturally performs changes to the `values.yaml` file. As part of this it performs a formatting of the file, that
may be undesired. One example is when a string containing a long list of elements has deliberately been split over multiple lines using the YAML [`>`](https://stackoverflow.com/questions/3790454/how-do-i-break-a-string-in-yaml-over-multiple-lines) notation for readability.  During the tag change AIU performs a reformatting of the entire file and such specific formatting may get lost. 

### Multiple values files
The solution is to insert the `image` section in a separate file called `values-aiu.yaml` and instruct AIU to write back changes to the alternate file. As AIU only modifies the file it 
writes to, `values.yaml` is left unmodified. 

To enable this feature you should start by removing the `image` section of `values.yaml` and write this to `values-aiu.yaml`. You must then update `application.yaml` with the 
line `argocd_image_updater_write_back_target: values-aiu.yaml`. 

Completing these steps will cause AIU to only write back to `values-aiu.yaml`. 

Removing the `image` section from `values.yaml` is required: `values.yaml` takes precedence over `values-aiu.yaml`, so any image tag left in `values.yaml` overrides the one AIU writes.

## Working with Argo Workflows and other non-standard CRDs
AIU can update various kinds of objects, but will in such cases need more assistance 
from the user. 

The example below demonstrates AIU with the Argo Workflows cron chart provided by IDP. (Both `application.yaml` 
and `values.yaml` in the example are snippets.)

You should notice the presence of the two fields `argocd_image_updater_helm_image_spec` and `argocd_image_updater_force_update`.
Together these fields point AIU to look for image specification in a non-standard path (using the image\_spec field) and 
tell AIU to complete the update using "force\_update". Note that the JsonPath is _not_ rooted with a dot.

Application file

```yaml
(...)
helm:
  chart: helm/argo-cronworkflow-job
  chartVersion: "1.2.5"
argocd_image_updater_ecr_image: idp/demonstrate-cron
argocd_image_updater_update_strategy: newest-build
argocd_image_updater_allow_tags: regexp:^dev-.*
argocd_image_updater_force_update: "true"
argocd_image_updater_helm_image_spec: "spec.workflowSpec.templates[0].container.image"
```

Values file
```yaml
 (...)
spec:
 (...)
  startingDeadlineSeconds: 60
  workflowSpec:
    entrypoint: delete-pending-deletion
    templates:
    - name: delete-pending-deletion
      inputs: {}
      outputs: {}
      metadata: {}
      container:
        name: "cron-delete-pending-deletion"
        image: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/idp/demonstrate-cron:dev-1777465563
 (...)
```


