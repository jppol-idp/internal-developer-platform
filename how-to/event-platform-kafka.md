---
title: Connecting to the Event Platform (Kafka)
nav_order: 8
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-10-01
review_in: 6 months
---

# Connecting to the Event Platform (Kafka)

The Event Platform is a managed Kafka cluster (Amazon MSK) run by the Event Platform team. Apps on IDP can read from and write to its topics using AWS IAM authentication.

{: .note }
> **Source of truth:** The Event Platform team's [Getting Access](https://jira-jppol.atlassian.net/wiki/spaces/EP/pages/4157931543/Getting+Access) page describes the full access process, including environments, account IDs, broker addresses and local development. Existing access roles per team and environment are listed on their [MSK Environment Overview](https://jira-jppol.atlassian.net/wiki/spaces/EP/pages/4173332486/MSK+Environment+Overview). This page only covers the IDP-specific part. If the two disagree, follow the Event Platform documentation.

## How it works

Your pod gets an AWS identity through IRSA (IAM Roles for Service Accounts). Your app uses that identity to assume a team-specific role in the Event Platform's AWS account, and then connects to the Kafka brokers on port `9098` with TLS and IAM authentication.

Network routing between the IDP clusters and the Event Platform is handled by the IDP team, so you do not need to set up anything network-related yourself. If your IDP account is not listed in the [MSK Environment Overview](https://jira-jppol.atlassian.net/wiki/spaces/EP/pages/4173332486/MSK+Environment+Overview), contact the IDP team on Slack.

## Setup

1. **Request an access role from the Event Platform team.** Follow the "IDP-managed AWS Account" steps on their [Getting Access](https://jira-jppol.atlassian.net/wiki/spaces/EP/pages/4157931543/Getting+Access) page. Check the [MSK Environment Overview](https://jira-jppol.atlassian.net/wiki/spaces/EP/pages/4173332486/MSK+Environment+Overview) first - your team may already have a role. Otherwise the Event Platform team will create one for each of your environments.

2. **Allow your app to assume the role.** Enable IRSA in your app's `values.yaml`, replacing `<ep-account-id>` with the Event Platform account ID for the environment (listed in the [MSK Environment Overview](https://jira-jppol.atlassian.net/wiki/spaces/EP/pages/4173332486/MSK+Environment+Overview)):

   ```yaml
   serviceAccount:
     create: true
     irsa:
       enabled: true
       iamPolicyStatements:
         - Effect: Allow
           Action:
             - sts:AssumeRole
           Resource:
             - arn:aws:iam::<ep-account-id>:role/*
   ```

3. **Configure your app.** Pass the role ARN and bootstrap broker addresses to your app, for example as [environment variables](./app-configuration). Your Kafka client must support MSK IAM authentication and assume the role before connecting.

To verify the role assumption from your laptop, you can [assume your deployment's IRSA role locally](./kubernetes-namespace-access).

## Support

- Access roles, topics and broker details: contact the Event Platform team (see their [Getting Access](https://jira-jppol.atlassian.net/wiki/spaces/EP/pages/4157931543/Getting+Access) page).
- IRSA or connectivity from the IDP clusters: contact the IDP team on Slack.
