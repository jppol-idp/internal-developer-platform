---
title: Aurora RDS Proxy – Local Access Setup Guide
nav_order: 14
parent: How to...
domain: public
permalink: /how-to-proxy-rds
last_reviewed_on: 2026-01-29
review_in: 3 months
---
# Aurora RDS Proxy – Local Access Setup Guide

> [!NOTE]
> This doc is used with kind permission from KOA - namespace examples are theirs. Any errors are introduced by MF.

## Introduction: Why Use an RDS Proxy

Our Aurora databases live inside a private VPC and are not directly accessible from local machines. At the same time, our applications run inside a private Kubernetes namespace, which has network-level access to those databases.

To securely bridge this gap for local development and troubleshooting, we use an Aurora RDS Proxy exposed inside the Kubernetes cluster. By port-forwarding to the proxy through kubectl.

This setup allows your local machine to securely connect to Aurora as if it were running inside the cluster, without compromising network isolation.

## Setup Instructions
### Step 1: Clone the Repository

Clone the jppol-idp/apps-koa repository:
```
git clone https://github.com/jppol-idp/apps-koa
```
### Step 2: Navigate to the Powershell folder inside Scripts
```
cd apps-koa/scripts/powershell
```
### Step 3: Install Required Kubernetes Tools

Open your Powershell as administrator, Run the following command:
```
powershell.exe -ExecutionPolicy Bypass -File .\kubernetes-install-tools.ps1
```

This script will:

-   Install Homebrew (macOS) or Chocolatey (Windows), depending on your OS

-   Install the required Kubernetes CLI tools (kubectl, etc.)

### Step 4: Configure Kubernetes Access for Your Environment (Needs to be run for daily use)

Run the environment-specific setup script:
```
./idp-ns-koa-dev.ps1
```

Choose the right script for the right environment:

-   idp-ns-koa-dev

-   idp-ns-koa-test

-   idp-ns-koa-prod

This configures your kubeconfig and AWS profile for the selected environment.
### Step 4.5: Troubleshooting (Optional)

If the previous step fails, try removing the AWS profile and re-running it:
```
./remove-aws-profile.ps -ProfileName idp-ns-koa-dev
```

Choose the right AWS Profile to remove:

-   idp-ns-koa-dev

-   idp-ns-koa-test

-   idp-ns-koa-prod

Then retry Step 4.
### Step 5: Port-Forward to the RDS Proxy (Needs to be run for daily use - and kept open and running in terminal)

Start port forwarding to the RDS proxy service:
```
kubectl port-forward -n rds-proxy svc/rds-proxy-idp-rds-proxy 5432:5432
```

Once this is running, you should see output indicating that the proxy is listening and forwarding traffic.
You can now connect to the database locally on localhost:5432.

 
