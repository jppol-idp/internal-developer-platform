---
title: Grafana shared dashboards
nav_order: 6
parent: How to...
domain: public
permalink: /grafana-shared-dashboards
last_reviewed_on: 2026-04-09
review_in: 6 months
---
# Grafana Shared Dashboards

## Introduction

Grafana supports sharing dashboards externally via a unique link — no login required. This is useful for displaying dashboards on office screens (e.g. Raspberry Pi, Yodeck) or sharing read-only views with stakeholders who don't have a Grafana account.

Each shared dashboard gets a unique UUID-based URL that provides read-only access to that specific dashboard only. Access can be paused or revoked at any time.

## How it works

1. A unique URL is generated for one specific dashboard
2. Anyone with the link can view the dashboard — no authentication needed
3. Append `?kiosk` to the URL to hide all Grafana UI (header, sidebar, navigation) — ideal for office screens
4. The link can be paused or revoked instantly from the Grafana UI

## Requirements and limitations

Before requesting a shared dashboard, make sure your dashboard meets these requirements:

### No template variables

Dashboards that use **template variables** (the dropdowns at the top of a dashboard) **cannot be shared externally**. This is a Grafana limitation.

If your dashboard relies on template variables, you need to create a dedicated copy of the dashboard with hardcoded values instead of variables.

### No personal data (GDPR)

Shared dashboards are accessible to **anyone with the link** without authentication. You are responsible for ensuring that the dashboard does not display personal data (PII) as defined by GDPR — for example names, email addresses, IP addresses, or other identifiable information.

Pay special attention to:
- **Log panels** — log data may contain personal data that is not immediately obvious
- **Table panels** with raw query results
- **Query filters** that include user identifiers

If you are unsure whether your dashboard contains personal data, consult your team's data protection contact or Legal before requesting external sharing.

## How to request a shared dashboard

Sharing a dashboard externally requires **Grafana Admin** permissions. This is a limitation of the Grafana OSS license — granular permission delegation for this feature is only available in Grafana Enterprise. As a result, the IDP team handles sharing on your behalf.

To get a dashboard shared:

1. Make sure your dashboard meets the requirements above (no template variables, etc.)
2. Contact the IDP team on Slack with the cluster and dashboard name (or URL)
3. The IDP team will enable external sharing and provide you with the link
4. To revoke or pause sharing, contact the IDP team

## Displaying on an office screen

Once you have the shared link:

1. Append `?kiosk` to the URL to hide all Grafana UI
2. Open the URL in a fullscreen browser on your screen device (Raspberry Pi, Yodeck, etc.)
3. The dashboard will auto-refresh based on its configured refresh interval

Example URL format:
```
https://grafana.<cluster>.idp.jppol.dk/public-dashboards/<uuid>?kiosk
```

## Security considerations

- The shared link provides **read-only** access to the specific dashboard only
- The UUID in the link is not guessable, but anyone with the link can view the dashboard
- If a link is compromised, contact the IDP team to revoke it immediately
