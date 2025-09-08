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
- All updates respect **GitOps** (i.e., changes are triggered by commits to your team’s configuration repository in **GitHub**)
- Continuous delivery for Kubernetes using **Argo CD**
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
- Object storage via **S3**
- NoSQL support with **DynamoDB**
- Scalable relational databases via **PostgreSQL** on **AWS Aurora V2**

## Eventing & Workflows

- Event-driven workflows via **Argo Events**
- Workflow orchestration with **Argo Workflows**

## Observability

- Observability powered by **Grafana** with **Prometheus** for metrics and **Loki** for log aggregation
- All console logs are automatically collected


## Philosophy

We aim to support:

- **Simple workloads** out-of-the-box
- **Complex setups** with multiple independent services inside a cluster
- **Architecture advice** during planning and migration
- **Continuous support** after onboarding

> Our goal is always to enable you to run everything as **self-service**.


## How IDP Works: Architecture & Tools Behind the Platform
![image](https://public.docs.idp.jppol.dk/assets/idp-architecture.png)


