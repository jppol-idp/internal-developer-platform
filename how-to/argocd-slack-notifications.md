---
title: ArgoCD Slack Notifications
nav_order: 3
parent: How to...
domain: public
permalink: /argocd-slack-notifications
last_reviewed_on: 2026-06-29
review_in: 6 months
---

# ArgoCD Slack Notifications

Get notified in Slack when your application fails to sync or becomes unhealthy — and,
if you opt in, when it's deployed. Everything is configured from your own
`application.yaml` in Git — you don't need to raise a ticket with the IDP team.

## Quick start

Add a `slackChannel` to your `application.yaml`, pointing at a **public** Slack channel:

```yaml
apiVersion: v2
name: my-application
description: My application
version: 0.1.0
slackChannel: my-team-alerts
helm:
  chart: helm/idp-advanced
  chartVersion: "3.5.1" # check latest at github.com/jppol-idp/helm-idp/releases
```

Commit and let ArgoCD sync. By default you'll get a Slack message **only when something
goes wrong** — see [Default notifications](#default-notifications) below.

> The channel must already exist and be **public**. For private channels, see
> [Public vs. private channels](#public-vs-private-channels).

## Default notifications

With just `slackChannel` set, you receive notifications for failures only:

| You get notified when… | Trigger |
| --- | --- |
| A sync operation fails | `on-sync-failed` |
| The application becomes unhealthy (Degraded) | `on-health-degraded` |
| The sync status becomes Unknown | `on-sync-status-unknown` |

You will **not** be notified about every successful sync — that quickly becomes noise.
If you want to know about deployments too, opt in with `slackTriggers` below.

## Choosing which notifications you get

Set `slackTriggers` to a list of triggers to override the default. When `slackTriggers` is
present, you receive **exactly** those triggers — nothing else.

```yaml
slackChannel: my-team-alerts
slackTriggers:
  - on-sync-failed
  - on-deployed
```

### Available triggers

| Trigger | Fires when | Noise |
| --- | --- | --- |
| `on-sync-failed` | A sync operation fails | Low |
| `on-health-degraded` | The app's health becomes Degraded | Low |
| `on-sync-status-unknown` | The sync status becomes Unknown | Low |
| `on-deployed` | The app is synced **and** healthy — once per commit | Low — one message per release |
| `on-sync-succeeded` | Every successful sync operation | High — also fires on self-heal/refresh syncs |
| `on-sync-running` | A sync starts | High |
| `on-created` | The application is created | One-off |
| `on-deleted` | The application is deleted | One-off |

> **Want to know when something is deployed?** Use `on-deployed`, not `on-sync-succeeded`.
> `on-deployed` sends one message per actual release (per commit, only when healthy),
> whereas `on-sync-succeeded` fires on every sync — including automated self-heal syncs
> that didn't change anything.

## Examples

**Failures only (this is also the default, so `slackTriggers` is optional here):**

```yaml
slackChannel: my-team-alerts
slackTriggers:
  - on-sync-failed
  - on-health-degraded
  - on-sync-status-unknown
```

**Failures plus a message on every deployment:**

```yaml
slackChannel: my-team-alerts
slackTriggers:
  - on-sync-failed
  - on-health-degraded
  - on-sync-status-unknown
  - on-deployed
```

**Deployments only (no failure alerts):**

```yaml
slackChannel: my-team-deploys
slackTriggers:
  - on-deployed
```

## Public vs. private channels

- **Public channels** work out of the box. Just set `slackChannel` — nothing else to do.
- **Private channels** need one extra step — the bot must be a member before it can post there.
  Add it to the channel once, using **either** method:

  - **Quickest:** in the channel, type `/invite @IDP ArgoCD Notifications` and pick the app with
    the octopus icon.
  - **Via the menu:** open the channel name → **Integrations** → **Add apps**, search for
    **IDP ArgoCD Notifications** (the octopus icon — not the similarly named plain **ArgoCD**
    app), and click **Add**.

  Either way, notifications are then delivered the same as for public channels.

## Notes

- `slackChannel` takes the channel name **without** the leading `#`
  (e.g. `my-team-alerts`, not `#my-team-alerts`).
- `slack_channel` (snake_case) is accepted as an alias for `slackChannel` for backwards
  compatibility. Prefer `slackChannel` for new applications.
- Changes take effect on the next ArgoCD sync of your application.

## Need help?

If notifications don't arrive as expected, contact the IDP team on Slack.
