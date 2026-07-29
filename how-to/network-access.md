---
title: Controlling network access to your app
nav_order: 7
parent: How to...
domain: public
layout: last-reviewed
last_reviewed_on: 2026-07-28
review_in: 6 months
---

# Controlling network access to your app

When you deploy an app through IDP, you'll often need to control traffic in two directions:

- **Inbound (ingress)** — restricting who is allowed to reach your app's own API endpoints from the internet.
- **Outbound (egress)** — letting your app reach a managed service outside the IDP clusters, e.g. an external database or third-party API that only accepts connections from allowlisted IPs.

This guide covers both.

## Table of contents

- [Restricting external access to your API endpoints](#restricting-external-access-to-your-api-endpoints)
- [Giving your app access to an external managed service](#giving-your-app-access-to-an-external-managed-service)

## Restricting external access to your API endpoints

Whether your app is reachable at all, and from where, is controlled by the `ingress` section of your `values.yaml`:

```yaml
ingress:
  enabled: true
  fqdn:
    - myapp.my-namespace.idp.jppol.dk
  public:
    enabled: true
  private:
    enabled: false
```

- `public.enabled` — reachable from the internet
- `private.enabled` — reachable from internal JPPol networks (on-prem systems, VPN clients, or workloads in other Kubernetes namespaces, clusters or AWS accounts) that are routed in via the internal Transit Gateway. **This is not for calling another app in the same namespace** — for that, call the app's service directly instead of going through ingress.

If your app should be reachable from those internal networks but not from the public internet, set `public.enabled: false` and keep `private.enabled: true` — no further configuration is needed.

If your app needs to be public but reachable only from specific IP addresses (e.g. only from the office or VPN), add an `ipAllowList` under `public`:

```yaml
ingress:
  enabled: true
  fqdn:
    - myapp.my-namespace.idp.jppol.dk
  public:
    enabled: true
    ipAllowList:
      - "91.214.20.0/22" # only internal office vpn
  private:
    enabled: false
```

`ipAllowList` takes a list of CIDR ranges. Any request from an IP outside the listed ranges is rejected before it reaches your app. The same `ipAllowList` field is also available under `private`, if you want to further restrict which internal callers can reach your app.

For the full set of available `ingress` options (annotations, additional middleware references, wildcard certificates, etc.), see the [idp-advanced schema reference](https://public.docs.idp.jppol.dk/schemas/idp-advanced/latest.json).

## Giving your app access to an external managed service

If your app needs to reach a managed service outside of IDP — for example a database or third-party API that only accepts traffic from a fixed set of IP addresses — you need to allowlist the IP(s) your traffic will appear to come from on the other end.

Which IP(s) apply depends on how the service is reached:

- If the service is only reachable over the internet, your traffic leaves the cluster through the **NAT gateway**, which uses a fixed set of public IP addresses.
- These IPs are documented per namespace in your apps repo's README. As a concrete example (not a value to copy for your own namespace), the IPs for the `pol-dev` namespace are listed here: [apps/pol-dev/README.md](https://github.com/jppol-idp/apps-pol/blob/main/apps/pol-dev/README.md). Look up the same file for your own namespace.

> **Note:** These are specific addresses, not a range. When the external service asks for a CIDR, add each address as its own `/32` (e.g. `54.220.9.41/32`).

If you can't find your namespace's IPs in the README, contact the IDP team on Slack.
