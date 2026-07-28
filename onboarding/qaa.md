---
title: Q&A
nav_order: 3 
parent: Onboarding
domain: public
layout: last-reviewed
last_reviewed_on: 2026-01-12
review_in: 6 months
---

# Q&A - IDP 🚀
If you or your team have any questions or run into issues, send us a [Slack message](https://jppol.slack.com/archives/C09JUREPVBP). Always ❤️.

---

### 1. 🔑 How do I get access to IDP?
- You need to be granted the correct AD group permissions.
- Requst needs to go via Servicedesk and a ServiceNow form.
- Request access from IDP support and we will request on your behalf.  

Is your team not yet set up in the IDP? Reach out to us – we’ll have a chat.

---

### 2. 🤫 How should we handle config?

We recommend placing configuration as environment variables, which can be defined in the `values.yaml` file:

```yaml
env:
  - name: ASPNETCORE_ENVIRONMENT
    value: Staging
  - name: UseIDPSecrets
    value: "true"
  - name: Hangfire__Enabled
    value: "false"
  - name: SubscriptionOrderService__apiBasePath
    value: "http://subscription-order-service-koa-test-service.koa-test.svc.cluster.local:8080"
  - name: SaapiService__apiBasePath
    value: "http://saapi-koa-test-service.koa-test.svc.cluster.local:8080/"
  - name: ASPNETCORE_HTTP_PORTS
    value: "8080"
```

---

> Please [share feedback and improvements with us in Slack](https://jppol.slack.com/archives/C09JUREPVBP). 

---
