---
title: Grafana externally shared dashboards
nav_order: 14
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-10-30
review_in: 6 months
---
# Grafana Externally Shared Dashboards

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

### No playlist support

Grafana **playlists** (rotating through multiple dashboards) are not supported for externally shared dashboards — each shared link points to one specific dashboard only. If you need to rotate between multiple dashboards on an office screen, use a kiosk-style tool like **Yodeck** or **Grafana Kiosk** that cycles through multiple shared dashboard URLs on the client side.

## How to request an externally shared dashboard

Sharing a dashboard externally requires **Grafana Admin** permissions. This is a limitation of the Grafana OSS license — granular permission delegation for this feature is only available in Grafana Enterprise. As a result, the IDP team handles sharing on your behalf.

To get a dashboard shared:

1. Make sure your dashboard meets the requirements above (no template variables, etc.)
2. Contact the IDP team on Slack with the cluster and dashboard name (or URL), and tell us if the dashboard should only be reachable from the office network (see below)
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

## Restricting a dashboard to the office network

If the dashboard shows data that should not leave the house, the IDP team can restrict the shared link to the JPPol office network. This covers all JPPol locations, such as Rådhuspladsen (RHP) and Mediebyen in Aarhus. The link then only opens from devices on the office network, including office screens on the office Wi-Fi. From anywhere else, such as from home or a mobile network, it returns `403 Forbidden`.

Ask for this when you request the shared dashboard. It can also be added to an existing shared dashboard.

If your screen needs to be reachable from a network outside JPPol, tell us, and we can allow that network for your dashboard. Each dashboard has its own restriction, so this does not affect other teams.

The restriction is tied to the specific link. If sharing is revoked and enabled again, the dashboard gets a new link, and the restriction has to be requested again.

## Security considerations

- The shared link provides **read-only** access to the specific dashboard only
- The UUID in the link is not guessable, but anyone with the link can view the dashboard, unless it is [restricted to the office network](#restricting-a-dashboard-to-the-office-network)
- If a link is compromised, contact the IDP team to revoke it immediately
