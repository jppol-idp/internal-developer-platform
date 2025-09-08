---
title: Technology overview
nav_order: 1 
parent: Onboarding
domain: public
permalink: /technology
---


# Technology Overview

The main offering from the Internal Developer Platform (IDP) team is to bring a container to life in a context. 
You build a container, and we orchestrate it in **Kubernetes** based on your configuration.

We strictly follow **GitOps** principles, meaning every change is stored as a commit.

## Deployment & Scaling 
- Supports multiple deployment and scaling strategies
- All updates respect **GitOps** (i.e., changes are triggered by commits to your team’s configuration repository in **Github**)
- **Argo CD** is used as continuous delivery tool for Kubernetes
- Access to multiple environments (called **namespaces** in our terminology)

## Container Lifecycle Support
- Actions to assist in pushing containers to storage (e.g., **ECR**)
- A system for **auto-updating deployments** based on:
  - Tag matching
  - Semantic Versioning (SemVer)

## Access and Security
- Access is integrated with your **JPPOL work account**
- Services can be exposed:
  - **Publicly** or **internally**
  - As **load-balanced HTTP services** using **nginx** or **AWS ALB**
- Transparent secret storage via **AWS Secrets Manager**
  

## Storage Solutions

We offer a range of storage options:

- Mounted container storage backed by **persistent EBS volumes**
- **S3** object storage
- **DynamoDB** for NoSQL
- **PostgreSQL** via **AWS Aurora V2** (scalable)

## Eventing & Workflows

- Managed **Argo Events**
- Managed **Argo Workflows**

## Observability

- **Grafana** for data insights with **Prometheus** for metrics and **Loki** for log aggregation
- All console logs are automatically collected


## Philosophy

We aim to support:

- **Simple workloads** out-of-the-box
- **Complex setups** with multiple independent services inside a cluster
- **Architecture advice** during planning and migration
- **Continuous support** after onboarding

> Our goal is always to enable you to run everything as **self-service**.


## Overview of the current IDP architecture and tooling
![image](https://public.docs.idp.jppol.dk/assets/idp-architecture.png)

<img width="1420" height="734" alt="image" src="https://public.docs.idp.jppol.dk/assets/idp-architecture.png" />


