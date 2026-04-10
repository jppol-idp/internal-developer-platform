---
title: Auto updating deployments
nav_order: 4
parent: How to...
domain: public
permalink: /how-to-auto-update
last_reviewed_on: 2025-09-10
review_in: 6 months
---
# Auto updating

## Introduction
If you desire to integrate deployments in your pipeline, you can utilize the system [Argo Image Updater](https://argocd-image-updater.readthedocs.io/en/stable/) which is a first class citizen in the IDP. 


Argo Image Updater connects your application repository ("apps-") with a polling mechanism, that evaluate changes in ECR for eligibility for updating your various deployments. You decide if and how auto update should occur, and the image updater will create git commits, adhering to the gitops principles. 

## Setting up auto updates
While Argo Image Updater is a tool generally applicable for updating container image tags in Kubernetes, this document assumes you are using the helm chart `idp-advanced` provided by the IDP team. (If you need to integrate AIU with charts developed by you, we refer to the documentation from AIU linked above.)

Assuming you already have some deployment in place using `idp-advanced` chart, you can add argo image updater by extending the `application.yaml` file with a few settings matching the container reference in `values.yaml`. 

If we have a `values.yaml` containing the following `image` section:

```yaml
image:
  repository: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/koa/customer-overview
  pullPolicy: IfNotPresent
  tag: "2.0.59"
``` 

and we want Argo Image updater to update whenever a newer image is build with a tag starting with `2.`, we can 
instruct Argo Image Update to use a strategy called `newest-build`. 

The instructions for Argo Image Updater has been inserted into the `applications.yaml` in the following example:

```
apiVersion: v2
name: static-html
description: static-html
version: 0.1.0
helm:
  chart: helm/idp-advanced
  chartVersion: "1.3.1"
argocd_image_updater_ecr_image: koa/customer-overview
argocd_image_updater_update_strategy: newest-build
argocd_image_updater_allow_tags: regexp:^2\..*

```

In the example AIU is instructed to look for changes in `koa/customer-overview`. Please note that this must match the repository definition in the image section of the `values.yaml`, but that the registry is omitted. Or in plain terms, it should match the path of the repository reference. 

Using the `newest-build` AIU will check if something has been pushed since the referenced image, and inserting an `argocd_image_updater_allow_tags` with a `regexp:` limits it to tags matching `^2\..*`. 

AIU has other stragegies for updating images and can among other things used to detect and respect SemVer changes. We refer to the AIU documentation for the specifics. 

## If your values file becomes garbled
When AIU alters the image tag, it naturally perform changes to the `values.yaml` file. As part of this it performs a formatting of the file, that
may be undesired. One example is when a string containing a long list of elements has deliberately been split over multiple lines using yamls (`>`)[https://stackoverflow.com/questions/3790454/how-do-i-break-a-string-in-yaml-over-multiple-lines] notation for readability.  During the tag change AIU perform a reformatting of the entire file and such specific formatting may get lost. 

### Mutliple values file
The solution is to insers the `image` section in a separate file valled `values.aui.yaml` and instruct AIU to write back changes to the alternate file. As AIU only modifies the file it 
changes the `values.yaml` is left unodified. 

To enable this feature you should start by removing the `image` section of `values.yaml` and write this to `values-aiu.yaml`. You must then update `application.yaml` with the 
line `argocd_image_update_write_back_target: values-aiu.yaml`. 

Completing these steps will cause AIU to only write back to `values-aiu.yaml`. 
